from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from ..adapters.vision import VisionProvider, VisionResult, get_vision
from ..models import (
    Category,
    Department,
    Product,
    ProductStatus,
    SupplierStatus,
)


def _score(product: Product, tokens: list[str], category: str | None, department: str | None) -> int:
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


def search(
    db: Session,
    *,
    filename: str,
    data: bytes,
    hint: str | None = None,
    limit: int = 24,
    provider: VisionProvider | None = None,
) -> tuple[list[Product], VisionResult]:
    active = provider or get_vision()
    vision = active.describe(filename=filename, data=data, hint=hint)
    if not vision.tags:
        return [], vision

    products = db.scalars(
        select(Product)
        .where(Product.status == ProductStatus.ACTIVE)
        .options(selectinload(Product.variants), joinedload(Product.supplier))
    ).unique().all()
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
            vision.tags,
            category.name if category else None,
            department.name if department else None,
        )
        if score == 0:
            continue
        product.department_slug = department.slug if department else None
        product.department_name = department.name if department else None
        ranked.append((score, product))

    ranked.sort(key=lambda entry: (entry[0], entry[1].created_at), reverse=True)
    return [product for _, product in ranked[:limit]], vision
