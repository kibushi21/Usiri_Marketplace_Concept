from __future__ import annotations

import re
import time
from collections import deque
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from ..adapters.assistant import AssistantContext, get_assistant
from ..models import Category, Department, Product, ProductStatus, SupplierStatus
from .platform_config import load_config

MAX_HISTORY = 8
MAX_HISTORY_CHARS = 2000
RATE_WINDOW_SECONDS = 60
RATE_LIMIT = 20
MAX_TRACKED_CLIENTS = 2000

STOPWORDS = {
    "a", "about", "also", "an", "and", "any", "are", "as", "at", "available", "be", "best",
    "buy", "by", "can", "cheapest", "compare", "contact", "cost", "could", "delivery", "do",
    "does", "for", "from", "get", "good", "got", "has", "have", "help", "here", "how", "i",
    "if", "in", "is", "it", "item", "items", "just", "like", "look", "looking", "many", "me",
    "much", "my", "need", "of", "on", "or", "order", "orders", "our", "pay", "payment",
    "payments", "please", "price", "prices", "product", "products", "recommend", "refund",
    "return", "returns", "sell", "selling", "shop", "show", "size", "some", "something",
    "stock", "store", "suggest", "support", "tanzania", "tell", "that", "the", "their",
    "there", "these", "they", "this", "those", "to", "top", "track", "tracking", "ticket",
    "usiri", "want", "was", "we", "were", "what", "when", "where", "which", "who", "why",
    "with", "work", "works", "would", "you", "your",
}


class RateLimited(RuntimeError):
    """Raised when one client sends too many assistant messages."""


_hits: dict[str, deque[float]] = {}


def check_rate_limit(client_key: str) -> None:
    now = time.monotonic()
    if len(_hits) > MAX_TRACKED_CLIENTS:
        stale = [key for key, queue in _hits.items() if not queue or now - queue[-1] > RATE_WINDOW_SECONDS]
        for key in stale:
            _hits.pop(key, None)
    queue = _hits.setdefault(client_key, deque())
    while queue and now - queue[0] > RATE_WINDOW_SECONDS:
        queue.popleft()
    if len(queue) >= RATE_LIMIT:
        raise RateLimited
    queue.append(now)


def _tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in re.findall(r"[a-z0-9]+", text.lower()):
        if len(raw) < 3 or raw.isdigit() or raw in STOPWORDS:
            continue
        candidates = [raw]
        if raw.endswith("s") and len(raw) > 3:
            candidates.append(raw[:-1])
        for candidate in candidates:
            if candidate not in tokens:
                tokens.append(candidate)
    return tokens


def _score(
    product: Product,
    tokens: list[str],
    category: str | None,
    department: str | None,
) -> int:
    name = product.name.lower()
    brand = (product.brand or "").lower()
    description = product.description.lower()
    attributes = " ".join(str(value) for value in (product.attributes or {}).values()).lower()
    score = 0
    for token in tokens:
        if token in name:
            score += 5
        if token in brand:
            score += 4
        if category and token in category.lower():
            score += 3
        if department and token in department.lower():
            score += 2
        if token in description:
            score += 1
        if token in attributes:
            score += 1
    return score


def _matches(db: Session, question: str, limit: int = 3) -> list[Product]:
    tokens = _tokens(question)
    if not tokens:
        return []
    products = (
        db.scalars(
            select(Product)
            .where(Product.status == ProductStatus.ACTIVE)
            .options(selectinload(Product.variants), joinedload(Product.supplier))
        )
        .unique()
        .all()
    )
    departments = {row.id: row for row in db.scalars(select(Department)).all()}
    categories = {row.id: row for row in db.scalars(select(Category)).all()}

    ranked: list[tuple[int, Product]] = []
    for product in products:
        if product.supplier.status != SupplierStatus.VERIFIED:
            continue
        department = departments.get(product.department_id)
        category = categories.get(product.category_id)
        score = _score(
            product,
            tokens,
            category.name if category else None,
            department.name if department else None,
        )
        if score == 0:
            continue
        product.department_slug = department.slug if department else None
        product.department_name = department.name if department else None
        ranked.append((score, product))

    ranked.sort(key=lambda entry: (entry[0], entry[1].created_at), reverse=True)
    return [product for _, product in ranked[:limit]]


def _catalogue_item(product: Product) -> dict[str, Any]:
    variants = [variant for variant in product.variants if variant.active]
    prices = [variant.price_tzs for variant in variants] or [0]
    return {
        "name": product.name,
        "brand": product.brand,
        "department": getattr(product, "department_name", None),
        "slug": product.slug,
        "price_from": min(prices),
        "price_to": max(prices),
        "variant_count": len(variants),
    }


def build_context(
    db: Session, *, audience: str, question: str
) -> tuple[AssistantContext, list[Product]]:
    config = load_config(db)
    departments = [
        row.name
        for row in db.scalars(
            select(Department).where(Department.active.is_(True)).order_by(Department.sort_order)
        )
    ]
    products = _matches(db, question)

    if audience == "ops":
        facts: dict[str, Any] = {
            "commission_bp": config["commission_bp"],
            "delivery_fee_flat": config["delivery_fee_flat"],
            "free_delivery_threshold": config["free_delivery_threshold"],
            "return_window_days": config["return_window_days"],
            "payout_hold_days": config["payout_hold_days"],
            "payout_minimum": config["payout_minimum"],
            "supplier_accept_sla_hours": config["supplier_accept_sla_hours"],
            "reservation_ttl_minutes": config["reservation_ttl_minutes"],
        }
    else:
        facts = {
            "delivery_fee_flat": config["delivery_fee_flat"],
            "free_delivery_threshold": config["free_delivery_threshold"],
            "return_window_days": config["return_window_days"],
            "support_email": config["support_email"],
            "support_phone": config["support_phone"],
            "currency": config["currency"],
        }

    context = AssistantContext(
        audience=audience,
        facts=facts,
        departments=departments,
        products=[_catalogue_item(product) for product in products],
    )
    return context, products


def _note(provider: str, model: str | None) -> str:
    if provider == "mock":
        return (
            "Demo assistant: replies come from the Usiri catalogue and store settings. "
            "No language model is connected yet."
        )
    return (
        f"Answers are generated by {model or 'a connected model'} and may be imperfect. "
        "Prices and stock come from the Usiri catalogue."
    )


def ask(
    db: Session,
    *,
    question: str,
    history: list[dict[str, str]],
    audience: str,
    client_key: str,
) -> dict[str, Any]:
    check_rate_limit(client_key)
    context, products = build_context(db, audience=audience, question=question)
    safe_history = [
        {"role": entry["role"], "content": entry["content"][:MAX_HISTORY_CHARS]}
        for entry in history
        if entry.get("role") in {"user", "assistant"} and entry.get("content")
    ][-MAX_HISTORY:]

    reply = get_assistant().respond(
        question=question,
        history=safe_history,
        context=context,
    )
    return {
        "reply": reply.content,
        "provider": reply.provider,
        "model": reply.model,
        "note": _note(reply.provider, reply.model),
        "audience": audience,
        "products": products,
    }
