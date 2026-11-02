from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..adapters.psp import get_provider
from ..errors import Conflict, DomainError, Forbidden, NotFound
from ..models import (
    Payout,
    Supplier,
    SupplierOrder,
    SupplierOrderStatus,
    User,
)
from . import ledger, notifications, refunds
from .platform_config import get_value
from .supplier_orders import eligible_orders, payout_eligible


def _now() -> datetime:
    return datetime.now(UTC)


def get_payout(db: Session, payout_id: str) -> Payout:
    payout = db.get(Payout, payout_id)
    if payout is None:
        raise NotFound("Payout not found")
    return payout


def payout_orders(db: Session, payout_id: str) -> list[SupplierOrder]:
    return list(db.scalars(select(SupplierOrder).where(SupplierOrder.payout_id == payout_id)))


def request(db: Session, *, supplier: Supplier, actor: User, notes: str | None = None) -> Payout:
    orders = eligible_orders(db, supplier.id)
    amount = sum(refunds.remaining_supplier_payable(so) for so in orders)
    amount = max(amount, 0)
    minimum = int(get_value(db, "payout_minimum"))
    if not orders or amount < minimum:
        raise Conflict(
            f"No eligible balance above the {minimum:,} TZS minimum".replace(",", " "),
            code="no_eligible_balance",
        )

    payout = Payout(
        supplier_id=supplier.id,
        amount=amount,
        status="pending_approval",
        period_start=min(so.delivered_at for so in orders if so.delivered_at),
        period_end=max(so.delivered_at for so in orders if so.delivered_at),
        requested_by=actor.id,
        notes=notes,
    )
    db.add(payout)
    db.flush()
    for so in orders:
        so.payout_id = payout.id
        so.payout_status = "requested"

    notifications.notify_supplier_team(
        db, supplier.id, "payout_requested", {"payout_id": payout.id, "amount": amount}
    )
    db.flush()
    return payout


def approve(db: Session, *, payout: Payout, actor: User, note: str | None = None) -> Payout:
    if payout.status != "pending_approval":
        raise Conflict("This payout is not awaiting approval", code="invalid_transition")
    if payout.requested_by == actor.id:
        raise Forbidden("The maker and the checker must be different people")
    payout.status = "approved"
    payout.approved_by = actor.id
    payout.approved_at = _now()
    if note:
        payout.notes = f"{payout.notes or ''}\n{note}".strip()
    db.flush()
    return payout


def reject(db: Session, *, payout: Payout, actor: User, reason: str) -> Payout:
    if payout.status not in {"pending_approval", "approved"}:
        raise Conflict("This payout can no longer be rejected", code="invalid_transition")
    payout.status = "rejected"
    payout.rejection_reason = reason
    for so in payout_orders(db, payout.id):
        so.payout_id = None
        so.payout_status = "unpaid"
    notifications.notify_supplier_team(
        db, payout.supplier_id, "payout_rejected", {"payout_id": payout.id, "reason": reason}
    )
    db.flush()
    return payout


def execute(db: Session, *, payout: Payout, actor: User) -> Payout:
    if payout.status != "approved":
        raise Conflict("Only approved payouts can be sent", code="invalid_transition")
    supplier = db.get(Supplier, payout.supplier_id)
    if supplier is None:
        raise NotFound("Supplier not found")

    result = get_provider().payout(
        destination={
            "method": supplier.payout_method,
            "provider": supplier.payout_provider,
            "account_name": supplier.payout_account_name,
            "account_number": supplier.payout_account_number,
        },
        amount=payout.amount,
        reference=payout.id,
    )
    if not result.ok:
        raise DomainError(result.message or "Payout failed", status_code=502, code="payout_failed")

    payout.status = "paid"
    payout.paid_at = _now()
    payout.provider_ref = result.provider_ref

    ledger.post_once(
        db,
        kind="payout",
        reference=payout.id,
        memo=f"Payout to {supplier.trading_name}",
        postings=[
            ledger.Posting("supplier_payable", debit=payout.amount),
            ledger.Posting("psp_clearing", credit=payout.amount),
        ],
    )

    for so in payout_orders(db, payout.id):
        so.payout_status = "paid"
        if so.status == SupplierOrderStatus.DELIVERED:
            so.status = SupplierOrderStatus.COMPLETED
            so.completed_at = _now()

    notifications.notify_supplier_team(
        db, supplier.id, "payout_paid", {"payout_id": payout.id, "amount": payout.amount}
    )
    db.flush()
    return payout


def supplier_balance(db: Session, supplier_id: str) -> dict:
    orders = db.scalars(
        select(SupplierOrder).where(
            SupplierOrder.supplier_id == supplier_id,
            SupplierOrder.status.in_(
                [SupplierOrderStatus.DELIVERED, SupplierOrderStatus.COMPLETED]
            ),
        )
    ).all()
    eligible = [so for so in orders if payout_eligible(so)]
    eligible_total = sum(max(refunds.remaining_supplier_payable(so), 0) for so in eligible)
    pending = sum(
        max(refunds.remaining_supplier_payable(so), 0)
        for so in orders
        if so.payout_status in {"requested", "approved"}
    )
    paid = sum(
        db.scalars(
            select(Payout.amount).where(
                Payout.supplier_id == supplier_id, Payout.status == "paid"
            )
        ).all()
    )
    return {
        "eligible": eligible_total,
        "in_payout": pending,
        "settled": paid,
        "orders_awaiting_hold": len(
            [
                so
                for so in orders
                if so.payout_status == "unpaid" and so.payout_id is None and not payout_eligible(so)
            ]
        ),
    }
