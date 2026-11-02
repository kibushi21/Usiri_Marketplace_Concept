from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..adapters.psp import get_provider
from ..errors import Conflict, DomainError, NotFound
from ..models import (
    Order,
    OrderStatus,
    Payment,
    PaymentStatus,
    SupplierOrder,
)
from . import inventory, ledger, notifications
from .platform_config import get_value


def _now() -> datetime:
    return datetime.now(UTC)


def ensure_reservations(db: Session, order: Order) -> None:
    if inventory.has_live_reservations(db, order.id):
        return
    ttl = int(get_value(db, "reservation_ttl_minutes"))
    for item in order.items:
        variant = inventory.get_variant_for_update(db, item.variant_id)
        if variant is None:
            raise Conflict("A product in this order is no longer available", code="product_unavailable")
        inventory.reserve(db, variant=variant, qty=item.qty, order_id=order.id, ttl_minutes=ttl)


def initiate(db: Session, order: Order, *, method: str, msisdn: str | None) -> Payment:
    if order.status != OrderStatus.PENDING_PAYMENT:
        raise Conflict("This order is not awaiting payment", code="order_not_payable")
    if order.payment_status == PaymentStatus.PAID:
        raise Conflict("This order is already paid", code="already_paid")

    ensure_reservations(db, order)

    for existing in db.scalars(
        select(Payment).where(Payment.order_id == order.id, Payment.status == "pending")
    ):
        existing.status = "expired"

    payment = Payment(
        order_id=order.id,
        amount=order.total,
        currency=order.currency,
        method=method,
        msisdn=msisdn,
        status="initiated",
        provider=get_provider().name,
    )
    db.add(payment)
    db.flush()

    result = get_provider().initiate(
        payment_id=payment.id,
        amount=payment.amount,
        currency=payment.currency,
        method=method,
        msisdn=msisdn,
        reference=order.code,
    )
    if not result.ok:
        payment.status = "failed"
        payment.failure_reason = result.message or "Provider rejected the payment request"
        db.flush()
        raise DomainError(payment.failure_reason, status_code=502, code="psp_error")

    payment.provider_ref = result.provider_ref
    payment.status = result.status or "pending"
    payment.raw = result.raw or {}
    db.flush()
    return payment


def _post_capture(db: Session, order: Order, payment: Payment) -> None:
    supplier_orders = list(order.supplier_orders)
    payable = sum(so.supplier_payable for so in supplier_orders)
    commission = sum(so.commission_amount for so in supplier_orders)
    delivery = sum(so.delivery_fee for so in supplier_orders)
    ledger.post_once(
        db,
        kind="payment_capture",
        reference=payment.id,
        memo=f"Payment captured for {order.code}",
        postings=[
            ledger.Posting("psp_clearing", debit=payment.amount),
            ledger.Posting("supplier_payable", credit=payable),
            ledger.Posting("platform_revenue", credit=commission),
            ledger.Posting("delivery_revenue", credit=delivery),
        ],
    )


def apply_provider_status(db: Session, payment: Payment, status: str) -> Payment:
    if payment.status != "pending":
        return payment

    order = db.get(Order, payment.order_id)
    if order is None:
        raise NotFound("Order not found")

    if status == "succeeded":
        if order.status == OrderStatus.CANCELLED:
            payment.status = "succeeded_unmatched"
            payment.failure_reason = "Funds captured after the order was cancelled; reconcile and refund"
            notifications.notify_ops(
                db,
                "payment_unmatched",
                {"order_code": order.code, "amount": payment.amount, "provider_ref": payment.provider_ref},
            )
            db.flush()
            return payment
        if order.payment_status == PaymentStatus.PAID:
            payment.status = "duplicate"
            db.flush()
            return payment
        if payment.amount != order.total:
            raise DomainError("Captured amount does not match the order total", status_code=409, code="amount_mismatch")
        payment.status = "succeeded"
        payment.completed_at = _now()
        order.payment_status = PaymentStatus.PAID
        order.status = OrderStatus.PAID
        order.paid_at = _now()
        inventory.commit_order(db, order.id)
        _post_capture(db, order, payment)
        notifications.notify(
            db,
            user_id=order.customer_id,
            template="payment_succeeded",
            payload={"order_code": order.code, "amount": payment.amount},
        )
        for so in order.supplier_orders:
            notifications.notify_supplier_team(
                db,
                so.supplier_id,
                "supplier_order_created",
                {"supplier_order_code": so.code, "order_code": order.code},
            )
        notifications.notify_ops(
            db, "payment_captured", {"order_code": order.code, "amount": payment.amount}
        )
    elif status == "failed":
        payment.status = "failed"
        payment.failure_reason = "Payment was declined or timed out"
        notifications.notify(
            db,
            user_id=order.customer_id,
            template="payment_failed",
            payload={"order_code": order.code},
        )

    db.flush()
    return payment


def verify_and_apply(db: Session, payment: Payment) -> Payment:
    if payment.status not in {"pending"}:
        return payment
    if not payment.provider_ref:
        raise DomainError("Payment has no provider reference", status_code=409, code="psp_reference_missing")
    result = get_provider().verify(provider_ref=payment.provider_ref, expected_amount=payment.amount)
    return apply_provider_status(db, payment, result.status or "pending")


def handle_webhook(db: Session, *, provider_ref: str, signature_ok: bool) -> Payment:
    if not signature_ok:
        raise DomainError("Invalid signature", status_code=401, code="invalid_signature")
    payment = db.scalar(select(Payment).where(Payment.provider_ref == provider_ref))
    if payment is None:
        raise NotFound("Unknown provider reference")
    return verify_and_apply(db, payment)


def simulate(db: Session, payment: Payment, outcome: str) -> Payment:
    from ..adapters.psp import MockPaymentProvider

    provider = get_provider()
    if not isinstance(provider, MockPaymentProvider):
        raise Conflict("Simulation is only available with the sandbox provider", code="not_sandbox")
    if outcome not in {"succeeded", "failed"}:
        raise Conflict("Outcome must be succeeded or failed", code="invalid_outcome")
    if payment.status != "pending" or not payment.provider_ref:
        raise Conflict("Payment is not awaiting a result", code="not_pending")
    provider.set_status(payment.provider_ref, outcome)
    return verify_and_apply(db, payment)


def payment_for_order(db: Session, order_id: str) -> Payment | None:
    return db.scalar(select(Payment).where(Payment.order_id == order_id).order_by(Payment.initiated_at.desc()))


def commission_reversal_for(so: SupplierOrder, merchandise_refund: int) -> int:
    from .pricing import BP_DIVISOR

    return (merchandise_refund * so.commission_bp + BP_DIVISOR // 2) // BP_DIVISOR
