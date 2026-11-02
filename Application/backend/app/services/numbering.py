from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session


def _next_sequence(db: Session, column, prefix: str, width: int = 6) -> str:
    latest = db.scalar(
        select(column)
        .where(column.like(f"{prefix}%"))
        .order_by(column.desc())
        .limit(1)
    )
    number = 1
    if latest:
        try:
            number = int(latest[len(prefix):]) + 1
        except ValueError:
            number = 1
    return f"{prefix}{number:0{width}d}"


def _year() -> int:
    return datetime.now(UTC).year


def next_order_code(db: Session) -> str:
    from ..models import Order

    return _next_sequence(db, Order.code, f"UM-{_year()}-")


def next_supplier_order_code(db: Session) -> str:
    from ..models import SupplierOrder

    return _next_sequence(db, SupplierOrder.code, f"SO-{_year()}-")


def next_return_code(db: Session) -> str:
    from ..models import Return

    return _next_sequence(db, Return.code, f"RT-{_year()}-")


def next_ticket_code(db: Session) -> str:
    from ..models import Ticket

    return _next_sequence(db, Ticket.code, f"TK-{_year()}-")


def next_supplier_code(db: Session) -> str:
    from ..models import Supplier

    return _next_sequence(db, Supplier.code, "SUP-", width=4)


def next_conversation_code(db: Session) -> str:
    from ..models import Conversation

    return _next_sequence(db, Conversation.code, f"CH-{_year()}-")
