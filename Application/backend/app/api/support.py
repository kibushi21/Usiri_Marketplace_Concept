from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from ..deps import CurrentUser, CustomerUser, Db
from ..models import Notification, Role, Ticket, TicketMessage
from ..services import notifications as notification_service
from ..services import numbering
from .schemas import TicketCreateIn, TicketReplyIn
from .serializers import notification_out, ticket_out

router = APIRouter(tags=["support"])


@router.post("/support/tickets", status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreateIn, user: CustomerUser, db: Db):
    ticket = Ticket(
        code=numbering.next_ticket_code(db),
        order_id=payload.order_id,
        customer_id=user.id,
        subject=payload.subject,
        category=payload.category,
        status="open",
    )
    db.add(ticket)
    db.flush()
    db.add(TicketMessage(ticket_id=ticket.id, author_id=user.id, body=payload.message))
    notification_service.notify_ops(
        db, "ticket_created", {"code": ticket.code, "subject": ticket.subject}
    )
    db.commit()
    messages = db.scalars(
        select(TicketMessage).where(TicketMessage.ticket_id == ticket.id)
    ).all()
    return ticket_out(ticket, list(messages))


@router.get("/support/tickets")
def list_my_tickets(user: CustomerUser, db: Db):
    tickets = db.scalars(
        select(Ticket).where(Ticket.customer_id == user.id).order_by(Ticket.created_at.desc())
    ).all()
    return {"items": [ticket_out(t) for t in tickets]}


@router.get("/support/tickets/{ticket_id}")
def get_ticket(ticket_id: str, user: CurrentUser, db: Db):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket not found")
    if user.role == Role.CUSTOMER and ticket.customer_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket not found")
    messages = db.scalars(
        select(TicketMessage)
        .where(TicketMessage.ticket_id == ticket.id)
        .order_by(TicketMessage.created_at)
    ).all()
    if user.role == Role.CUSTOMER:
        messages = [m for m in messages if not m.internal]
    return ticket_out(ticket, list(messages))


@router.post("/support/tickets/{ticket_id}/messages", status_code=status.HTTP_201_CREATED)
def reply(ticket_id: str, payload: TicketReplyIn, user: CurrentUser, db: Db):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket not found")
    if user.role == Role.CUSTOMER and ticket.customer_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket not found")
    if payload.internal and user.role not in Role.STAFF:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only staff can post internal notes")
    message = TicketMessage(
        ticket_id=ticket.id, author_id=user.id, body=payload.body, internal=payload.internal
    )
    db.add(message)
    if user.role in Role.STAFF and ticket.status == "open":
        ticket.status = "in_progress"
        ticket.assigned_to = user.id
    elif user.role == Role.CUSTOMER and ticket.status == "resolved":
        ticket.status = "open"
    db.commit()
    return {"id": message.id, "created_at": message.created_at.isoformat()}


@router.get("/notifications")
def list_notifications(user: CurrentUser, db: Db):
    rows = db.scalars(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    ).all()
    return {
        "items": [notification_out(n) for n in rows],
        "unread": sum(1 for n in rows if n.read_at is None),
    }


@router.post("/notifications/{notification_id}/read")
def mark_read(notification_id: str, user: CurrentUser, db: Db):
    from ..models import utcnow

    notification = db.get(Notification, notification_id)
    if notification is None or notification.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
    notification.read_at = notification.read_at or utcnow()
    db.commit()
    return {"ok": True}


@router.post("/notifications/read-all")
def mark_all_read(user: CurrentUser, db: Db):
    from ..models import utcnow

    rows = db.scalars(
        select(Notification).where(Notification.user_id == user.id, Notification.read_at.is_(None))
    ).all()
    now = utcnow()
    for row in rows:
        row.read_at = now
    db.commit()
    return {"updated": len(rows)}
