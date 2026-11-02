from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..config import Settings, get_settings


@dataclass(frozen=True)
class AssistantContext:
    audience: str = "customer"
    facts: dict[str, Any] = field(default_factory=dict)
    departments: list[str] = field(default_factory=list)
    products: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class AssistantReply:
    provider: str
    content: str
    model: str | None = None


class AssistantUnavailable(RuntimeError):
    """Raised when the configured model provider cannot produce an answer."""


class ChatProvider:
    """Provider-agnostic assistant boundary.

    The bundled implementation answers deterministically from the catalogue and
    store settings. A larger model is connected by implementing this interface
    (or by selecting the OpenAI-compatible adapter) without changing the API or UI.
    """

    name = "abstract"

    def respond(
        self,
        *,
        question: str,
        history: list[dict[str, str]],
        context: AssistantContext,
    ) -> AssistantReply:
        raise NotImplementedError


def _any(text: str, words: tuple[str, ...]) -> bool:
    return any(re.search(rf"\b{re.escape(word)}\b", text) for word in words)


def _money(value: Any) -> str:
    try:
        return f"TZS {int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def _price(item: dict[str, Any]) -> str:
    low = item.get("price_from") or 0
    high = item.get("price_to") or low
    if high and high != low:
        return f"{_money(low)}–{int(high):,}"
    return _money(low)


GREETINGS = (
    "hello",
    "hi",
    "hey",
    "habari",
    "mambo",
    "jambo",
    "good morning",
    "good afternoon",
    "good evening",
)
THANKS = ("thanks", "thank you", "asante", "ahsante")
MARKET_WORDS = (
    "best selling",
    "best-selling",
    "bestselling",
    "best seller",
    "best sellers",
    "top selling",
    "top sellers",
    "popular",
    "trending",
)
TRACKING_WORDS = (
    "track",
    "tracking",
    "cargo",
    "batch",
    "where is my order",
    "shipment status",
    "tracking number",
)
RETURN_WORDS = ("return", "returns", "refund", "exchange", "kurudisha", "rejesha")
DELIVERY_WORDS = ("delivery", "shipping", "deliver", "courier", "usafirishaji", "kufikisha")
PAYMENT_WORDS = ("payment", "payments", "pay", "mpesa", "m-pesa", "tigopesa", "card", "malipo")
SUPPORT_WORDS = ("support", "human", "agent", "ticket", "contact", "msaada", "complaint")
OPS_PAYOUT_WORDS = ("payout", "payouts", "finance", "commission", "malipo")
OPS_TRACKING_WORDS = ("tracking", "cargo", "batch", "shipment", "delayed", "override")
OPS_RETURN_WORDS = ("return", "returns", "refund", "exchange")
OPS_TICKET_WORDS = ("ticket", "tickets", "support", "complaint")
OPS_SETTINGS_WORDS = ("setting", "settings", "config", "configuration", "fee", "hold")
GENERAL_WORDS = (
    "recommend",
    "suggest",
    "compare",
    "which",
    "what is",
    "what are",
    "where can i buy",
    "cheapest",
    "best",
)


class MockChatProvider(ChatProvider):
    """Deterministic assistant over the live catalogue and platform settings.

    It intentionally does not invent market-wide facts. Broader questions get an
    honest answer plus a pointer to what the demo can see, so the UI can present
    this as a demo assistant rather than a connected language model.
    """

    name = "mock"

    def respond(
        self,
        *,
        question: str,
        history: list[dict[str, str]],
        context: AssistantContext,
    ) -> AssistantReply:
        text = " ".join(question.lower().split())
        if _any(text, GREETINGS):
            return self._reply(self._intro(context))
        if _any(text, THANKS):
            return self._reply("You're welcome. Ask me anything else about Usiri.")

        if context.audience == "ops":
            return self._reply(self._ops_answer(text, context))

        if _any(text, MARKET_WORDS):
            return self._reply(self._market_answer(context))
        if _any(text, TRACKING_WORDS):
            return self._reply(self._tracking_answer())
        if _any(text, RETURN_WORDS):
            return self._reply(self._return_answer(context))
        if _any(text, DELIVERY_WORDS):
            return self._reply(self._delivery_answer(context))
        if _any(text, PAYMENT_WORDS):
            return self._reply(self._payment_answer())
        if _any(text, SUPPORT_WORDS):
            return self._reply(self._support_answer(context))

        if context.products:
            return self._reply(self._product_answer(context))

        if _any(text, GENERAL_WORDS):
            return self._reply(
                "This demo assistant only sees the Usiri catalogue and store settings, so I "
                "can't answer general market or product questions from outside. Connect a "
                "larger model with USIRI_LLM_PROVIDER=openai to enable those answers. In the "
                "meantime I can explain delivery, returns, payments or find catalogue products."
            )

        return self._reply(self._intro(context))

    def _reply(self, content: str) -> AssistantReply:
        return AssistantReply(provider=self.name, content=content)

    def _intro(self, context: AssistantContext) -> str:
        if context.audience == "ops":
            return (
                "I'm the operations assistant. I can explain payouts, cargo tracking "
                "overrides, returns, support tickets and platform settings. Ask me about a "
                "process and I'll point you to the right tab."
            )
        return (
            "I'm the Usiri shop assistant. I can explain delivery, returns, payments and "
            "support, and find products in the catalogue. Try “show me kettles” or “what are "
            "the delivery fees?”"
        )

    def _market_answer(self, context: AssistantContext) -> str:
        departments = ", ".join(context.departments) or "the departments on the shop page"
        return (
            "I can't rank Tanzania-wide best sellers: this demo only sees the Usiri "
            "catalogue and store settings, and it has no market sales data. What I can do is "
            "help you browse our departments — "
            f"{departments}. A connected language model could answer broader market "
            "questions from general knowledge."
        )

    def _delivery_answer(self, context: AssistantContext) -> str:
        fee = _money(context.facts.get("delivery_fee_flat", 0))
        threshold = _money(context.facts.get("free_delivery_threshold", 0))
        return (
            f"Delivery is {fee} per supplier shipment and becomes free when the basket "
            f"reaches {threshold}. Each supplier ships as its own cargo batch, so an order "
            "split across suppliers can carry more than one delivery fee."
        )

    def _return_answer(self, context: AssistantContext) -> str:
        days = context.facts.get("return_window_days", "—")
        return (
            f"You can request a return within {days} days of delivery from the order page. "
            "Operations review the request, and recording the received item refunds it in the "
            "same step. Delivery fees follow the return policy set by Usiri."
        )

    def _payment_answer(self) -> str:
        return (
            "Payments in this build are simulated: checkout sends you to a mock provider page "
            "where you choose paid or failed, and no real money moves. In production Usiri "
            "uses a licensed payment provider; customer funds are not held in escrow, and "
            "suppliers are paid after delivery."
        )

    def _tracking_answer(self) -> str:
        return (
            "Every supplier order is its own cargo batch. After dispatch you can follow each "
            "batch — carrier, tracking number and event trail — on the order page. Sign in and "
            "open Orders to see the latest milestone. I can't look up personal orders from "
            "this chat in the demo."
        )

    def _support_answer(self, context: AssistantContext) -> str:
        email = context.facts.get("support_email", "the support email")
        phone = context.facts.get("support_phone", "the support phone line")
        return (
            f"Customer support is at {email} or {phone}. Signed-in customers can also open a "
            "ticket on the Support page; replies stay on the ticket so there is a record."
        )

    def _product_answer(self, context: AssistantContext) -> str:
        lines = []
        for item in context.products[:3]:
            brand = f" — {item['brand']}" if item.get("brand") else ""
            department = f" · {item['department']}" if item.get("department") else ""
            lines.append(f"• {item['name']}{brand}{department} · {_price(item)}")
        return (
            "Closest matches in the Usiri catalogue:\n"
            + "\n".join(lines)
            + "\n\nOpen a match below for options and stock."
        )

    def _ops_answer(self, text: str, context: AssistantContext) -> str:
        facts = context.facts
        if _any(text, OPS_PAYOUT_WORDS):
            commission = facts.get("commission_bp", 0)
            hold = facts.get("payout_hold_days", "—")
            minimum = _money(facts.get("payout_minimum", 0))
            return (
                "Payouts use maker-checker: finance requests a payout after the hold period, "
                "a different finance user approves it, then it is executed. The flow lives in "
                f"the Payouts tab. Commission is currently {int(commission) / 100:.1f}% of "
                f"merchandise, the hold is {hold} days after delivery, and the minimum payout "
                f"is {minimum}."
            )
        if _any(text, OPS_TRACKING_WORDS):
            return (
                "Open Orders in this console, expand an order and pick a batch. The tracking "
                "form accepts picked_up, in_transit, out_for_delivery, delayed, "
                "delivery_attempted and returned_to_sender plus a customer-visible note. An "
                "override pauses simulated carrier events; delivered, cancelled and "
                "returned_to_sender batches are closed to further overrides."
            )
        if _any(text, OPS_RETURN_WORDS):
            return (
                "Returns are decided in the Returns tab. Receiving the item refunds it in the "
                "same step: commission is reversed, the supplier payable is reduced and the "
                "ledger entries are posted."
            )
        if _any(text, OPS_TICKET_WORDS):
            return (
                "Customer tickets are in the Support tab. You can reply publicly or add an "
                "internal note; internal notes never appear in the customer's thread."
            )
        if _any(text, OPS_SETTINGS_WORDS):
            return (
                "Platform settings are in the Settings tab: commission, delivery fee, "
                "free-delivery threshold, return window, payout hold, reservation TTL and "
                "contact details. Every change is audited. "
                f"Current return window: {facts.get('return_window_days', '—')} days; "
                f"reservation TTL: {facts.get('reservation_ttl_minutes', '—')} minutes."
            )
        return self._intro(context)


SYSTEM_PROMPT = (
    "You are the Usiri marketplace assistant. Usiri is a managed marketplace for Tanzanian "
    "homes with verified suppliers, licensed carriers and payments through authorised "
    "providers. Answer briefly and plainly, in the language the person writes in. Use only "
    "the store facts below for prices, fees, timings and policies; never invent stock, order "
    "statuses or personal data. You may answer general product or market questions from your "
    "own knowledge, but label them as general guidance rather than Usiri policy. This is a "
    "demo build: payments are simulated. For order-specific questions, ask the customer to "
    "sign in and open Orders."
)


def _system_prompt(context: AssistantContext) -> str:
    parts = [SYSTEM_PROMPT, f"Audience: {context.audience}."]
    if context.facts:
        facts = "; ".join(f"{key}={value}" for key, value in context.facts.items())
        parts.append(f"Store facts: {facts}.")
    if context.departments:
        parts.append(f"Departments: {', '.join(context.departments)}.")
    if context.products:
        lines = [
            f"{item['name']} (brand {item.get('brand') or 'unbranded'}, "
            f"{item.get('department') or 'unassigned'}, {_price(item)}, slug {item['slug']})"
            for item in context.products
        ]
        parts.append("Catalogue matches: " + "; ".join(lines) + ".")
    return "\n".join(parts)


class OpenAICompatibleProvider(ChatProvider):
    """Calls any OpenAI-compatible chat completion endpoint.

    The base URL, model name and key come from configuration, so a hosted model,
    a gateway or a local server (Ollama, LM Studio) can be used without code
    changes. The key is never returned to the client or logged.
    """

    name = "openai"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 30.0,
        max_tokens: int = 400,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens

    def respond(
        self,
        *,
        question: str,
        history: list[dict[str, str]],
        context: AssistantContext,
    ) -> AssistantReply:
        if not self.api_key:
            raise AssistantUnavailable("The assistant model is not configured yet.")
        messages = [{"role": "system", "content": _system_prompt(context)}]
        for entry in history:
            if entry["role"] in {"user", "assistant"} and entry["content"]:
                messages.append({"role": entry["role"], "content": entry["content"]})
        messages.append({"role": "user", "content": question})

        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.4,
                    "max_tokens": self.max_tokens,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise AssistantUnavailable(
                "The assistant model is unavailable right now. Try again shortly."
            ) from exc

        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (IndexError, KeyError, TypeError, ValueError) as exc:
            raise AssistantUnavailable(
                "The assistant model returned an unexpected response."
            ) from exc
        content = (content or "").strip()
        if not content:
            raise AssistantUnavailable("The assistant model returned an empty answer.")
        return AssistantReply(provider=self.name, content=content, model=self.model)


_assistant: ChatProvider | None = None


def build_assistant(settings: Settings | None = None) -> ChatProvider:
    active = settings or get_settings()
    if active.llm_provider == "openai":
        return OpenAICompatibleProvider(
            base_url=active.llm_base_url,
            api_key=active.llm_api_key,
            model=active.llm_model,
            timeout=active.llm_timeout_seconds,
            max_tokens=active.llm_max_tokens,
        )
    return MockChatProvider()


def get_assistant() -> ChatProvider:
    global _assistant
    if _assistant is None:
        _assistant = build_assistant()
    return _assistant


def set_assistant(provider: ChatProvider | None) -> None:
    global _assistant
    _assistant = provider
