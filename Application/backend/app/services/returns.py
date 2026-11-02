from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..errors import Conflict, Forbidden, NotFound
from ..models import (
    ItemStatus,
    Order,
    OrderItem,
    Return,
    ReturnStatus,
    SupplierOrder,
    User,
)
from . import notifications, numbering, refunds
from .platform_config import get_value, load_config


def _now() -> datetime:
    return datetime.now(UTC)


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def open_return_qty(db: Session, item_id: str) -> int:
    rows = db.scalars(
        select(Return).where(
            Return.item_id == item_id,
            Return.status.in_(
                [ReturnStatus.REQUESTED, ReturnStatus.APPROVED, ReturnStatus.RECEIVED]
            ),
        )
    ).all()
    return sum(row.qty for row in rows)


def request_return(
    db: Session,
    *,
    customer: User,
    item: OrderItem,
    qty: int,
    reason: str,
    details: str | None,
) -> Return:
    order = db.get(Order, item.order_id)
    if order is None or order.customer_id != customer.id:
        raise Forbidden("This item does not belong to your order")
    so = db.get(SupplierOrder, item.supplier_order_id)
    if so is None:
        raise NotFound("Supplier order not found")
    if item.status != ItemStatus.DELIVERED:
        raise Conflict("Only delivered items can be returned", code="item_not_delivered")
    delivered_at = _aware(so.delivered_at)
    window_days = int(get_value(db, "return_window_days"))
    if delivered_at is None or _now() > delivered_at + timedelta(days=window_days):
        raise Conflict(
            f"The {window_days}-day return window has closed", code="return_window_closed"
        )
    if qty < 1:
        raise Conflict("Quantity must be at least one", code="invalid_quantity")
    remaining = item.qty - item.refunded_qty - open_return_qty(db, item.id)
    if qty > remaining:
        raise Conflict(f"Only {remaining} of this item can still be returned", code="invalid_quantity")

    ret = Return(
        code=numbering.next_return_code(db),
        order_id=order.id,
        supplier_order_id=so.id,
        item_id=item.id,
        customer_id=customer.id,
        qty=qty,
        reason=reason,
        details=details,
        status=ReturnStatus.REQUESTED,
    )
    db.add(ret)
    db.flush()
    notifications.notify_ops(
        db,
        "return_requested",
        {"return_code": ret.code, "order_code": order.code, "item": item.product_name},
    )
    return ret


def decide(db: Session, *, ret: Return, actor: User, approve: bool, note: str | None) -> Return:
    if ret.status != ReturnStatus.REQUESTED:
        raise Conflict("This return has already been decided", code="invalid_transition")
    ret.status = ReturnStatus.APPROVED if approve else ReturnStatus.REJECTED
    ret.decision_note = note
    ret.decided_by = actor.id
    ret.decided_at = _now()
    notifications.notify(
        db,
        user_id=ret.customer_id,
        template="return_approved" if approve else "return_rejected",
        payload={"return_code": ret.code, "note": note or ""},
    )
    db.flush()
    return ret


def receive(db: Session, *, ret: Return, actor: User, note: str | None) -> Return:
    if ret.status != ReturnStatus.APPROVED:
        raise Conflict("Only approved returns can be received", code="invalid_transition")
    item = db.get(OrderItem, ret.item_id)
    so = db.get(SupplierOrder, ret.supplier_order_id)
    if item is None or so is None:
        raise NotFound("Return references a missing item")

    config = load_config(db)
    merchandise = item.unit_price * ret.qty
    delivery = 0
    if config.get("refund_delivery_on_return"):
        delivery = so.delivery_fee

    refund = refunds.create_refund(
        db,
        supplier_order=so,
        merchandise_amount=merchandise,
        delivery_amount=delivery,
        reason=f"Return {ret.code}: {ret.reason}",
        actor=actor,
        return_id=ret.id,
    )

    ret.status = ReturnStatus.REFUNDED
    ret.received_at = _now()
    ret.refund_id = refund.id
    ret.refund_amount = refund.amount
    if note:
        ret.decision_note = note

    item.refunded_qty += ret.qty
    if item.refunded_qty >= item.qty:
        item.status = ItemStatus.RETURNED

    notifications.notify(
        db,
        user_id=ret.customer_id,
        template="return_refunded",
        payload={"return_code": ret.code, "amount": refund.amount},
    )
    db.flush()
    return ret


def list_customer_returns(db: Session, customer: User) -> list[Return]:
    return list(
        db.scalars(
            select(Return).where(Return.customer_id == customer.id).order_by(Return.created_at.desc())
        )
    )


def list_returns(db: Session, status: str | None = None) -> list[Return]:
    query = select(Return).order_by(Return.created_at.desc())
    if status:
        query = query.where(Return.status == status)
    return list(db.scalars(query))
