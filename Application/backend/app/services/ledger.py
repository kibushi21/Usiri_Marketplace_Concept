from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import LedgerAccount, LedgerEntry, LedgerTransaction


class LedgerError(ValueError):
    pass


ACCOUNTS: dict[str, tuple[str, str]] = {
    "psp_clearing": ("Payment provider clearing", "asset"),
    "supplier_payable": ("Supplier payable", "liability"),
    "platform_revenue": ("Commission revenue", "revenue"),
    "delivery_revenue": ("Delivery revenue", "revenue"),
    "refund_expense": ("Refunds and adjustments", "expense"),
    "tax_payable": ("Tax payable", "liability"),
}


@dataclass
class Posting:
    account: str
    debit: int = 0
    credit: int = 0


def ensure_accounts(db: Session) -> None:
    existing = {row.code for row in db.scalars(select(LedgerAccount))}
    for code, (name, kind) in ACCOUNTS.items():
        if code not in existing:
            db.add(LedgerAccount(code=code, name=name, kind=kind))
    db.flush()


def post(
    db: Session,
    *,
    kind: str,
    reference: str,
    postings: list[Posting],
    memo: str | None = None,
) -> LedgerTransaction:
    debits = sum(p.debit for p in postings)
    credits = sum(p.credit for p in postings)
    for posting in postings:
        if posting.debit < 0 or posting.credit < 0:
            raise LedgerError("Ledger amounts cannot be negative")
        if posting.debit and posting.credit:
            raise LedgerError("A ledger line is either a debit or a credit")
        if posting.account not in ACCOUNTS:
            raise LedgerError(f"Unknown ledger account {posting.account}")
    if debits != credits:
        raise LedgerError(f"Unbalanced transaction: debits {debits} != credits {credits}")
    if debits == 0:
        raise LedgerError("Empty transaction")

    transaction = LedgerTransaction(kind=kind, reference=reference, memo=memo)
    db.add(transaction)
    db.flush()
    for posting in postings:
        if posting.debit == 0 and posting.credit == 0:
            continue
        db.add(
            LedgerEntry(
                transaction_id=transaction.id,
                account_code=posting.account,
                debit=posting.debit,
                credit=posting.credit,
            )
        )
    db.flush()
    return transaction


def post_once(db: Session, *, kind: str, reference: str, postings: list[Posting], memo: str | None = None):
    existing = db.scalar(
        select(LedgerTransaction).where(
            LedgerTransaction.kind == kind, LedgerTransaction.reference == reference
        )
    )
    if existing:
        return existing
    return post(db, kind=kind, reference=reference, postings=postings, memo=memo)


def account_balance(db: Session, code: str) -> int:
    account = db.scalar(select(LedgerAccount).where(LedgerAccount.code == code))
    if account is None:
        return 0
    totals = db.execute(
        select(func.coalesce(func.sum(LedgerEntry.debit), 0), func.coalesce(func.sum(LedgerEntry.credit), 0))
        .where(LedgerEntry.account_code == code)
    ).one()
    debit, credit = int(totals[0]), int(totals[1])
    if account.kind in {"asset", "expense"}:
        return debit - credit
    return credit - debit


def is_balanced(db: Session) -> bool:
    totals = db.execute(
        select(func.coalesce(func.sum(LedgerEntry.debit), 0), func.coalesce(func.sum(LedgerEntry.credit), 0))
    ).one()
    return int(totals[0]) == int(totals[1])
