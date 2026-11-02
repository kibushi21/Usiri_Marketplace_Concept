from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..adapters.carrier import get_carrier
from ..errors import Conflict, Forbidden, NotFound
from ..models import (
    ItemStatus,
    Order,
    OrderItem,
    PaymentStatus,
    Shipment,
    ShipmentEvent,
    SupplierOrder,
    SupplierOrderStatus,
    User,
)
from . import notifications, refunds
from . import orders as order_service
from .platform_config import get_value, load_config


def _now() -> datetime:
    return datetime.now(UTC)


def get_supplier_order(db: Session, supplier_order_id: str) -> SupplierOrder:
    so = db.scalar(
        select(SupplierOrder)
        .where(SupplierOrder.id == supplier_order_id)
        .options(
            selectinload(SupplierOrder.items),
            selectinload(SupplierOrder.order).selectinload(Order.items),
            selectinload(SupplierOrder.shipments).selectinload(Shipment.events),
            selectinload(SupplierOrder.supplier),
        )
    )
    if so is None:
        raise NotFound("Supplier order not found")
    return so


def assert_owner(so: SupplierOrder, actor: User) -> None:
    if actor.supplier_id != so.supplier_id:
        raise Forbidden("This order belongs to another supplier")


def _require_status(so: SupplierOrder, *allowed: str) -> None:
    if so.status not in allowed:
        raise Conflict(
            f"Action not allowed while the supplier order is {so.status}",
            code="invalid_transition",
        )


def accept(
    db: Session,
    *,
    so: SupplierOrder,
    actor: User,
    accepted_item_ids: list[str] | None,
    rejection_reason: str = "Item is out of stock",
) -> SupplierOrder:
    _require_status(so, SupplierOrderStatus.AWAITING_ACCEPTANCE)
    order = db.get(Order, so.order_id)
    if order is None or order.payment_status not in {PaymentStatus.PAID, PaymentStatus.PARTIALLY_REFUNDED}:
        raise Conflict("The customer payment has not been captured", code="payment_not_captured")

    pending = [item for item in so.items if item.status == ItemStatus.PENDING]
    if not pending:
        raise Conflict("There are no items awaiting acceptance", code="nothing_to_accept")

    accepted_ids = set(accepted_item_ids) if accepted_item_ids is not None else {i.id for i in pending}
    unknown = accepted_ids - {item.id for item in pending}
    if unknown:
        raise Conflict("Some items do not belong to this supplier order", code="invalid_items")

    rejected: list[OrderItem] = []
    accepted: list[OrderItem] = []
    for item in pending:
        if item.id in accepted_ids:
            item.status = ItemStatus.ACCEPTED
            item.accepted_at = _now()
            accepted.append(item)
        else:
            item.status = ItemStatus.REJECTED
            item.rejection_reason = rejection_reason
            rejected.append(item)

    so.accepted_at = _now()
    if accepted:
        so.status = SupplierOrderStatus.ACCEPTED
    else:
        so.status = SupplierOrderStatus.CANCELLED
        so.rejection_reason = rejection_reason

    if rejected:
        config = load_config(db)
        refund_delivery = bool(config["refund_delivery_on_supplier_rejection"]) and not accepted
        refunds.refund_rejected_items(
            db,
            supplier_order=so,
            items=rejected,
            reason=f"Supplier rejected items on {so.code}",
            actor=actor,
            refund_delivery=refund_delivery,
        )
        notifications.notify(
            db,
            user_id=order.customer_id,
            template="items_rejected",
            payload={
                "supplier_order_code": so.code,
                "items": [item.product_name for item in rejected],
            },
        )

    order_service.recompute_order_status(db, order)
    db.flush()
    return so


def reject(
    db: Session, *, so: SupplierOrder, actor: User, reason: str
) -> SupplierOrder:
    return accept(db, so=so, actor=actor, accepted_item_ids=[], rejection_reason=reason)


def mark_ready(db: Session, *, so: SupplierOrder, actor: User) -> SupplierOrder:
    _require_status(so, SupplierOrderStatus.ACCEPTED)
    if not any(item.status == ItemStatus.ACCEPTED for item in so.items):
        raise Conflict("There is nothing to dispatch", code="nothing_to_ship")
    so.status = SupplierOrderStatus.READY
    so.ready_at = _now()
    order = db.get(Order, so.order_id)
    if order:
        notifications.notify(
            db,
            user_id=order.customer_id,
            template="order_ready",
            payload={"supplier_order_code": so.code},
        )
    db.flush()
    return so


def ship(
    db: Session,
    *,
    so: SupplierOrder,
    actor: User,
    carrier: str | None = None,
    tracking_number: str | None = None,
    fee: int | None = None,
) -> Shipment:
    _require_status(so, SupplierOrderStatus.ACCEPTED, SupplierOrderStatus.READY)
    items = [item for item in so.items if item.status == ItemStatus.ACCEPTED]
    if not items:
        raise Conflict("There is nothing to dispatch", code="nothing_to_ship")

    carrier_name = carrier or str(get_value(db, "carrier_default"))
    weight = sum(
        (item.variant.weight_g if item.variant else 500) * item.qty for item in items
    )
    order = db.get(Order, so.order_id)

    draft = Shipment(
        supplier_order_id=so.id,
        carrier=carrier_name,
        carrier_mode="manual",
        status="pending",
        fee=so.delivery_fee,
    )
    tracking = tracking_number
    mode = "manual"
    adapter = get_carrier()
    if not tracking:
        result = adapter.book(shipment=draft, region=order.ship_region if order else "", weight_g=weight)
        if not result.ok:
            raise Conflict(
                result.message or "A tracking number is required for this carrier",
                code="tracking_required",
            )
        tracking = result.tracking_number
        mode = adapter.mode
        if fee is None:
            fee = result.fee

    draft.carrier_mode = mode
    draft.tracking_number = tracking
    draft.status = "booked"
    draft.fee = fee if fee is not None else so.delivery_fee
    draft.booked_at = _now()
    draft.picked_at = _now() if mode == "manual" else None
    so.shipments.append(draft)
    draft.events.append(
        ShipmentEvent(
            status="booked",
            note=f"Dispatched with {carrier_name}",
            actor="carrier",
        )
    )
    db.flush()
    shipment = draft

    for item in items:
        item.status = ItemStatus.SHIPPED
    so.status = SupplierOrderStatus.IN_TRANSIT
    so.ready_at = so.ready_at or _now()

    order = db.get(Order, so.order_id)
    if order:
        notifications.notify(
            db,
            user_id=order.customer_id,
            template="order_shipped",
            payload={"supplier_order_code": so.code, "tracking": tracking},
        )
    db.flush()
    return shipment


def deliver(
    db: Session,
    *,
    so: SupplierOrder,
    actor: User,
    pod_ref: str | None = None,
    note: str | None = None,
) -> SupplierOrder:
    _require_status(so, SupplierOrderStatus.IN_TRANSIT, SupplierOrderStatus.READY)
    shipments = list(so.shipments)
    if not shipments:
        raise Conflict("No shipment exists for this order", code="no_shipment")
    shipment = shipments[-1]
    shipment.status = "delivered"
    shipment.delivered_at = _now()
    shipment.pod_ref = pod_ref
    shipment.events.append(
        ShipmentEvent(
            status="delivered",
            note=note or "Proof of delivery recorded",
            actor=actor.email,
        )
    )

    for item in so.items:
        if item.status == ItemStatus.SHIPPED:
            item.status = ItemStatus.DELIVERED

    hold_days = int(get_value(db, "payout_hold_days"))
    so.status = SupplierOrderStatus.DELIVERED
    so.delivered_at = _now()
    so.eligible_at = _now() + timedelta(days=hold_days)

    order = db.get(Order, so.order_id)
    if order:
        notifications.notify(
            db,
            user_id=order.customer_id,
            template="order_delivered",
            payload={"supplier_order_code": so.code},
        )
        order_service.recompute_order_status(db, order)
    db.flush()
    return so


def mark_completed(db: Session, *, so: SupplierOrder, actor: User) -> SupplierOrder:
    _require_status(so, SupplierOrderStatus.DELIVERED)
    so.status = SupplierOrderStatus.COMPLETED
    so.completed_at = _now()
    db.flush()
    return so


def payout_eligible(so: SupplierOrder, now: datetime | None = None) -> bool:
    now = now or _now()
    if so.status not in {SupplierOrderStatus.DELIVERED, SupplierOrderStatus.COMPLETED}:
        return False
    if so.payout_status != "unpaid" or so.payout_id is not None:
        return False
    if so.eligible_at is None:
        return False
    from .inventory import _aware

    return _aware(so.eligible_at) <= now


def eligible_orders(db: Session, supplier_id: str) -> list[SupplierOrder]:
    candidates = db.scalars(
        select(SupplierOrder).where(
            SupplierOrder.supplier_id == supplier_id,
            SupplierOrder.payout_status == "unpaid",
            SupplierOrder.payout_id.is_(None),
            SupplierOrder.status.in_(
                [SupplierOrderStatus.DELIVERED, SupplierOrderStatus.COMPLETED]
            ),
        )
    ).all()
    return [so for so in candidates if payout_eligible(so)]
