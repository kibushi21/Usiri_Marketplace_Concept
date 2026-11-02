from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..adapters.psp import get_provider
from ..errors import Conflict, DomainError
from ..models import (
    Order,
    Payment,
    Refund,
    RefundStatus,
    SupplierOrder,
    User,
)
from . import ledger, notifications
from . import orders as order_service
from .payments import commission_reversal_for


def _now() -> datetime:
    return datetime.now(UTC)


def captured_payment(db: Session, order_id: str) -> Payment | None:
    return db.scalar(
        select(Payment)
        .where(Payment.order_id == order_id, Payment.status == "succeeded")
        .order_by(Payment.completed_at.desc())
    )


def refundable_merchandise(so: SupplierOrder) -> int:
    return max(0, so.merchandise_total - so.refunded_merchandise)


def refundable_delivery(so: SupplierOrder) -> int:
    return max(0, so.delivery_fee - so.refunded_delivery)


def remaining_supplier_payable(so: SupplierOrder) -> int:
    clawback = so.refunded_merchandise - so.refunded_commission
    return so.supplier_payable - clawback


def create_refund(
    db: Session,
    *,
    supplier_order: SupplierOrder,
    merchandise_amount: int,
    delivery_amount: int,
    reason: str,
    actor: User | None,
    return_id: str | None = None,
) -> Refund:
    order = db.get(Order, supplier_order.order_id)
    if order is None:
        raise DomainError("Order not found", status_code=404, code="not_found")
    payment = captured_payment(db, order.id)
    if payment is None:
        raise Conflict("The order has no captured payment to refund", code="no_captured_payment")
    if merchandise_amount < 0 or delivery_amount < 0:
        raise Conflict("Refund amounts cannot be negative", code="invalid_refund")
    if merchandise_amount == 0 and delivery_amount == 0:
        raise Conflict("Refund amount must be greater than zero", code="invalid_refund")
    if merchandise_amount > refundable_merchandise(supplier_order):
        raise Conflict(
            f"Merchandise refund exceeds the remaining {refundable_merchandise(supplier_order)} TZS",
            code="refund_exceeds_capture",
        )
    if delivery_amount > refundable_delivery(supplier_order):
        raise Conflict("Delivery refund exceeds the captured delivery fee", code="refund_exceeds_capture")

    commission_reversal = commission_reversal_for(supplier_order, merchandise_amount)
    total = merchandise_amount + delivery_amount

    refund = Refund(
        payment_id=payment.id,
        order_id=order.id,
        supplier_order_id=supplier_order.id,
        return_id=return_id,
        amount=total,
        merchandise_amount=merchandise_amount,
        delivery_amount=delivery_amount,
        commission_reversal=commission_reversal,
        status=RefundStatus.PROCESSING,
        reason=reason,
        created_by=actor.id if actor else None,
    )
    db.add(refund)
    db.flush()

    result = get_provider().refund(
        provider_ref=payment.provider_ref or "", amount=total, reason=reason
    )
    if not result.ok:
        refund.status = RefundStatus.FAILED
        refund.failure_reason = result.message or "Provider declined the refund"
        db.flush()
        raise DomainError(refund.failure_reason, status_code=502, code="refund_failed")

    refund.status = RefundStatus.SUCCEEDED
    refund.provider_ref = result.provider_ref
    refund.completed_at = _now()

    supplier_order.refunded_merchandise += merchandise_amount
    supplier_order.refunded_delivery += delivery_amount
    supplier_order.refunded_commission += commission_reversal
    order.refunded_total += total

    ledger.post_once(
        db,
        kind="refund",
        reference=refund.id,
        memo=f"Refund for {order.code}",
        postings=[
            ledger.Posting("psp_clearing", credit=total),
            ledger.Posting(
                "supplier_payable", debit=merchandise_amount - commission_reversal
            ),
            ledger.Posting("platform_revenue", debit=commission_reversal),
            ledger.Posting("delivery_revenue", debit=delivery_amount),
        ],
    )

    notifications.notify(
        db,
        user_id=order.customer_id,
        template="refund_processed",
        payload={"order_code": order.code, "amount": total},
    )
    order_service.recompute_order_status(db, order)
    db.flush()
    return refund


def refund_rejected_items(
    db: Session,
    *,
    supplier_order: SupplierOrder,
    items,
    reason: str,
    actor: User | None,
    refund_delivery: bool,
) -> Refund | None:
    merchandise = sum(item.unit_price * item.qty for item in items)
    if merchandise == 0 and not refund_delivery:
        return None
    delivery = refundable_delivery(supplier_order) if refund_delivery else 0
    if merchandise == 0 and delivery == 0:
        return None
    return create_refund(
        db,
        supplier_order=supplier_order,
        merchandise_amount=merchandise,
        delivery_amount=delivery,
        reason=reason,
        actor=actor,
    )
