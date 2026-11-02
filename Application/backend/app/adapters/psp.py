from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import ClassVar

from ..config import get_settings


@dataclass
class ProviderResult:
    ok: bool
    provider_ref: str | None = None
    status: str | None = None
    redirect_url: str | None = None
    message: str | None = None
    raw: dict | None = None


class PaymentProvider:
    """Boundary the marketplace owns; every provider is adapted to this shape."""

    name = "abstract"

    def initiate(self, *, payment_id: str, amount: int, currency: str, method: str, msisdn: str | None, reference: str) -> ProviderResult:
        raise NotImplementedError

    def verify(self, *, provider_ref: str, expected_amount: int) -> ProviderResult:
        raise NotImplementedError

    def refund(self, *, provider_ref: str, amount: int, reason: str | None) -> ProviderResult:
        raise NotImplementedError

    def payout(self, *, destination: dict, amount: int, reference: str) -> ProviderResult:
        raise NotImplementedError


class MockPaymentProvider(PaymentProvider):
    """In-process sandbox that mimics an authorised PSP.

    Statuses live in a module-level map so the callback can be exercised without
    a real provider. It is replaced, not extended, when a licensed PSP is wired in.
    """

    name = "mock"
    _statuses: ClassVar[dict[str, str]] = {}

    def initiate(self, *, payment_id: str, amount: int, currency: str, method: str, msisdn: str | None, reference: str) -> ProviderResult:
        provider_ref = f"MOCK-{uuid.uuid4().hex[:16].upper()}"
        self._statuses[provider_ref] = "pending"
        base = get_settings().psp_callback_base.rstrip("/")
        return ProviderResult(
            ok=True,
            provider_ref=provider_ref,
            status="pending",
            redirect_url=f"{base}/pay/{payment_id}",
            raw={"provider": self.name, "reference": reference, "method": method, "msisdn": msisdn},
        )

    def verify(self, *, provider_ref: str, expected_amount: int) -> ProviderResult:
        status = self._statuses.get(provider_ref, "pending")
        return ProviderResult(ok=status == "succeeded", provider_ref=provider_ref, status=status)

    def set_status(self, provider_ref: str, status: str) -> None:
        self._statuses[provider_ref] = status

    def refund(self, *, provider_ref: str, amount: int, reason: str | None) -> ProviderResult:
        return ProviderResult(
            ok=True,
            provider_ref=f"REF-{uuid.uuid4().hex[:12].upper()}",
            status="succeeded",
            raw={"amount": amount, "reason": reason, "original": provider_ref},
        )

    def payout(self, *, destination: dict, amount: int, reference: str) -> ProviderResult:
        return ProviderResult(
            ok=True,
            provider_ref=f"PYT-{uuid.uuid4().hex[:12].upper()}",
            status="succeeded",
            raw={"amount": amount, "destination": destination, "reference": reference},
        )


_provider: PaymentProvider = MockPaymentProvider()


def get_provider() -> PaymentProvider:
    return _provider
