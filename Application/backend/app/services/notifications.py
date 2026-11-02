from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Notification, Role, User


def notify(
    db: Session,
    *,
    user_id: str,
    template: str,
    payload: dict | None = None,
    channel: str = "in_app",
) -> Notification:
    notification = Notification(
        user_id=user_id,
        channel=channel,
        template=template,
        payload=payload or {},
        status="sent" if channel == "in_app" else "queued",
    )
    db.add(notification)
    db.flush()
    return notification


def notify_supplier_team(db: Session, supplier_id: str, template: str, payload: dict) -> None:
    staff = db.query(User).filter(User.supplier_id == supplier_id, User.role == Role.SUPPLIER).all()
    for member in staff:
        notify(db, user_id=member.id, template=template, payload=payload)


def notify_ops(db: Session, template: str, payload: dict) -> None:
    staff = db.query(User).filter(User.role.in_(Role.STAFF)).all()
    for member in staff:
        notify(db, user_id=member.id, template=template, payload=payload)
