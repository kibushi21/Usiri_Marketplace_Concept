from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..adapters.carrier import get_carrier
from ..errors import Conflict, NotFound
from ..models import Order, Shipment, ShipmentEvent, User

OVERRIDE_STATUSES = {
    "picked_up",
    "in_transit",
    "out_for_delivery",
    "delayed",
    "delivery_attempted",
    "returned_to_sender",
}
CLOSED_STATUSES = {"delivered", "cancelled", "returned_to_sender"}
ACTIVE_STATUSES = {"booked", "picked_up", "in_transit", "out_for_delivery", "delayed"}
OVERRIDE_PREFIX = "ops:"


def _now() -> datetime:
    return datetime.now(UTC)


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def get_shipment(db: Session, shipment_id: str) -> Shipment:
    shipment = db.scalar(
        select(Shipment)
        .where(Shipment.id == shipment_id)
        .options(selectinload(Shipment.events))
    )
    if shipment is None:
        raise NotFound("Shipment not found")
    return shipment


def has_manual_override(shipment: Shipment) -> bool:
    return any(event.actor.startswith(OVERRIDE_PREFIX) for event in shipment.events)


def advance(db: Session, shipment: Shipment, *, now: datetime | None = None) -> int:
    """Materialise due carrier milestones for the mock API carrier."""
    if shipment.carrier_mode != "api" or shipment.booked_at is None:
        return 0
    if shipment.status in CLOSED_STATUSES or has_manual_override(shipment):
        return 0

    now = now or _now()
    booked_at = _aware(shipment.booked_at)
    existing = {event.status for event in shipment.events}
    due = [
        step
        for step in get_carrier().schedule()
        if booked_at + timedelta(seconds=step.offset_seconds) <= now
    ]

    created = 0
    for step in due:
        if step.status in existing:
            continue
        shipment.events.append(
            ShipmentEvent(
                status=step.status,
                note=step.note,
                actor="carrier",
                occurred_at=booked_at + timedelta(seconds=step.offset_seconds),
            )
        )
        existing.add(step.status)
        created += 1

    if due:
        shipment.status = due[-1].status
        if shipment.picked_at is None and "picked_up" in existing:
            shipment.picked_at = booked_at + timedelta(seconds=1)
    if created:
        db.flush()
    return created


def advance_for_order(db: Session, order: Order, *, now: datetime | None = None) -> int:
    total = 0
    for so in order.supplier_orders:
        for shipment in so.shipments:
            total += advance(db, shipment, now=now)
    return total


def advance_due(db: Session, *, now: datetime | None = None) -> int:
    shipments = db.scalars(
        select(Shipment)
        .where(
            Shipment.carrier_mode == "api",
            Shipment.status.in_(ACTIVE_STATUSES),
        )
        .options(selectinload(Shipment.events))
    ).all()
    total = 0
    for shipment in shipments:
        total += advance(db, shipment, now=now)
    return total


def override(
    db: Session,
    *,
    shipment: Shipment,
    status: str,
    note: str | None,
    actor: User,
) -> ShipmentEvent:
    if status not in OVERRIDE_STATUSES:
        raise Conflict("That tracking status cannot be set manually", code="invalid_tracking_status")
    if shipment.status in CLOSED_STATUSES:
        raise Conflict("Tracking is closed for this shipment", code="tracking_closed")

    shipment.status = status
    event = ShipmentEvent(
        status=status,
        note=note or "Updated by operations",
        actor=OVERRIDE_PREFIX + actor.email,
    )
    shipment.events.append(event)
    db.flush()
    return event
