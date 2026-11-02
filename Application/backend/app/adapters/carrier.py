from __future__ import annotations

import uuid
from dataclasses import dataclass

from ..models import Shipment


@dataclass
class BookingResult:
    ok: bool
    tracking_number: str | None = None
    fee: int | None = None
    message: str | None = None


@dataclass(frozen=True)
class TrackingStep:
    offset_seconds: int
    status: str
    note: str


class CarrierProvider:
    """Provider-agnostic carrier boundary: quote, book, cancel, track, POD."""

    name = "abstract"
    mode = "manual"

    def quote(self, *, region: str, weight_g: int) -> int:
        base = 7_000
        return base + max(0, weight_g - 3_000) // 1_000 * 500

    def book(self, *, shipment: Shipment, region: str, weight_g: int) -> BookingResult:
        raise NotImplementedError

    def cancel(self, *, tracking_number: str) -> bool:
        raise NotImplementedError

    def schedule(self) -> list[TrackingStep]:
        """Carrier-reported milestones after booking, relative to the booking time."""
        return []


class ManualCarrier(CarrierProvider):
    """Mode A at launch: the provider books offline and confirms in the console."""

    name = "manual"
    mode = "manual"

    def book(self, *, shipment: Shipment, region: str, weight_g: int) -> BookingResult:
        return BookingResult(ok=False, message="Manual carrier: enter the tracking number to confirm")

    def cancel(self, *, tracking_number: str) -> bool:
        return True


class MockApiCarrier(CarrierProvider):
    """Mode B: behaves like a courier with a booking and tracking API."""

    name = "mock_api"
    mode = "api"

    def book(self, *, shipment: Shipment, region: str, weight_g: int) -> BookingResult:
        return BookingResult(
            ok=True,
            tracking_number=f"TRK-{uuid.uuid4().hex[:10].upper()}",
            fee=self.quote(region=region, weight_g=weight_g),
        )

    def cancel(self, *, tracking_number: str) -> bool:
        return True

    def schedule(self) -> list[TrackingStep]:
        # Compressed for the demo: a real carrier reports these over hours, not minutes.
        return [
            TrackingStep(1, "picked_up", "Parcel collected from the supplier"),
            TrackingStep(120, "in_transit", "In transit to the delivery hub"),
            TrackingStep(360, "out_for_delivery", "Out for delivery"),
        ]


_carrier: CarrierProvider = MockApiCarrier()


def get_carrier() -> CarrierProvider:
    return _carrier


def set_carrier(carrier: CarrierProvider) -> None:
    global _carrier
    _carrier = carrier
