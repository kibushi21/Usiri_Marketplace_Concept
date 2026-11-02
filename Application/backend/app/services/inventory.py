from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..errors import Conflict
from ..models import Order, OrderStatus, ProductVariant, Reservation


def get_variant_for_update(db: Session, variant_id: str) -> ProductVariant | None:
    return db.scalar(select(ProductVariant).where(ProductVariant.id == variant_id).with_for_update())


def reserve(
    db: Session,
    *,
    variant: ProductVariant,
    qty: int,
    order_id: str,
    ttl_minutes: int,
) -> Reservation:
    if qty <= 0:
        raise Conflict("Quantity must be positive", code="invalid_quantity")
    if variant.available < qty:
        raise Conflict(
            f"Insufficient stock for {variant.sku}: {variant.available} available",
            code="insufficient_stock",
        )
    variant.reserved += qty
    reservation = Reservation(
        variant_id=variant.id,
        order_id=order_id,
        qty=qty,
        status="held",
        expires_at=datetime.now(UTC) + timedelta(minutes=ttl_minutes),
    )
    db.add(reservation)
    db.flush()
    return reservation


def commit(db: Session, reservation: Reservation) -> None:
    if reservation.status != "held":
        return
    variant = get_variant_for_update(db, reservation.variant_id)
    if variant is None:
        return
    reservation.status = "committed"
    variant.reserved = max(0, variant.reserved - reservation.qty)
    variant.on_hand = max(0, variant.on_hand - reservation.qty)
    db.flush()


def release(db: Session, reservation: Reservation) -> None:
    if reservation.status != "held":
        return
    variant = get_variant_for_update(db, reservation.variant_id)
    reservation.status = "released"
    if variant is not None:
        variant.reserved = max(0, variant.reserved - reservation.qty)
    db.flush()


def reservations_for_order(db: Session, order_id: str) -> list[Reservation]:
    return list(
        db.scalars(
            select(Reservation).where(Reservation.order_id == order_id).order_by(Reservation.created_at)
        )
    )


def release_order(db: Session, order_id: str) -> None:
    for reservation in reservations_for_order(db, order_id):
        release(db, reservation)


def has_live_reservations(db: Session, order_id: str) -> bool:
    now = datetime.now(UTC)
    for reservation in reservations_for_order(db, order_id):
        if reservation.status == "held" and _aware(reservation.expires_at) > now:
            return True
    return False


def commit_order(db: Session, order_id: str) -> None:
    for reservation in reservations_for_order(db, order_id):
        commit(db, reservation)


def expire_reservations(db: Session) -> int:
    now = datetime.now(UTC)
    released = 0

    # A payment that never resolved must not hold stock indefinitely.
    from ..models import Payment

    stale_payments = db.scalars(
        select(Payment).where(
            Payment.status == "pending",
            Payment.initiated_at < now - timedelta(minutes=45),
        )
    ).all()
    for payment in stale_payments:
        payment.status = "expired"
        payment.failure_reason = "No confirmation was received from the payment provider"

    stale = db.scalars(
        select(Reservation).where(Reservation.status == "held", Reservation.expires_at <= now)
    ).all()
    for reservation in stale:
        release(db, reservation)
        released += 1
    if released:
        open_orders = db.scalars(
            select(Order).where(Order.status == OrderStatus.PENDING_PAYMENT)
        ).all()
        for order in open_orders:
            if has_live_reservations(db, order.id):
                continue
            pending_payment = db.scalar(
                select(Payment).where(Payment.order_id == order.id, Payment.status == "pending")
            )
            if pending_payment is not None:
                continue
            order.status = OrderStatus.CANCELLED
            order.cancelled_at = now
            order.cancellation_reason = "Payment was not completed before the reservation expired"
    db.flush()
    return released


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)
