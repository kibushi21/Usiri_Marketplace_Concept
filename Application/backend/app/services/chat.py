from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from ..errors import Conflict, Forbidden, NotFound
from ..models import (
    ChatMessage,
    ChatMessageKind,
    ChatParty,
    Conversation,
    Order,
    PaymentStatus,
    Role,
    Shipment,
    SupplierOrder,
    SupplierOrderStatus,
    User,
)
from . import numbering

WELCOME = (
    "Conversation opened for {code}. Ask {supplier} about this order. "
    "After dispatch, the supplier can hand delivery questions to the Usiri logistics desk."
)
MAX_BODY = 2000

PAID_STATUSES = (
    PaymentStatus.PAID,
    PaymentStatus.PARTIALLY_REFUNDED,
    PaymentStatus.REFUNDED,
)


def _now() -> datetime:
    return datetime.now(UTC)


def party_for(conversation: Conversation, user: User) -> str | None:
    if user.role == Role.CUSTOMER and conversation.customer_id == user.id:
        return ChatParty.CUSTOMER
    if (
        user.role == Role.SUPPLIER
        and user.supplier_id
        and conversation.supplier_id == user.supplier_id
    ):
        return ChatParty.SUPPLIER
    if user.role in Role.LOGISTICS_DESK:
        return ChatParty.LOGISTICS
    return None


def conversation_query():
    return select(Conversation).options(
        joinedload(Conversation.customer),
        joinedload(Conversation.supplier),
        joinedload(Conversation.supplier_order).joinedload(SupplierOrder.order),
        joinedload(Conversation.supplier_order).joinedload(SupplierOrder.supplier),
        joinedload(Conversation.supplier_order).selectinload(SupplierOrder.shipments),
        selectinload(Conversation.messages).joinedload(ChatMessage.author),
    )


def ensure_for_supplier_order(db: Session, so: SupplierOrder) -> Conversation:
    existing = db.scalar(
        select(Conversation).where(Conversation.supplier_order_id == so.id)
    )
    if existing is not None:
        return existing

    order = so.order
    if order is None:
        order = db.get(Order, so.order_id)
    supplier = so.supplier
    if order is None or supplier is None:
        raise Conflict("Cannot open a conversation for this order", code="chat_unavailable")

    conversation = Conversation(
        code=numbering.next_conversation_code(db),
        supplier_order_id=so.id,
        order_id=order.id,
        supplier_id=so.supplier_id,
        customer_id=order.customer_id,
        assigned_party=ChatParty.SUPPLIER,
        last_message_at=_now(),
    )
    db.add(conversation)
    db.flush()
    add_message(
        db,
        conversation=conversation,
        author=None,
        party=ChatParty.SYSTEM,
        body=WELCOME.format(code=so.code, supplier=supplier.trading_name),
        kind=ChatMessageKind.SYSTEM,
    )
    return conversation


def add_message(
    db: Session,
    *,
    conversation: Conversation,
    author: User | None,
    party: str,
    body: str,
    kind: str = ChatMessageKind.TEXT,
) -> ChatMessage:
    text = body.strip()
    if not text:
        raise Conflict("Write a message first", code="empty_message")
    if len(text) > MAX_BODY:
        raise Conflict(
            f"Messages are limited to {MAX_BODY} characters", code="message_too_long"
        )
    message = ChatMessage(
        conversation_id=conversation.id,
        author_id=author.id if author else None,
        author=author,
        author_party=party,
        body=text,
        kind=kind,
    )
    db.add(message)
    conversation.last_message_at = _now()
    db.flush()
    return message


def system_for_order(
    db: Session,
    so: SupplierOrder,
    body: str,
    *,
    kind: str = ChatMessageKind.SYSTEM,
) -> tuple[Conversation, ChatMessage]:
    conversation = ensure_for_supplier_order(db, so)
    message = add_message(
        db,
        conversation=conversation,
        author=None,
        party=ChatParty.SYSTEM,
        body=body,
        kind=kind,
    )
    return conversation, message


def _backfill(db: Session, user: User) -> None:
    statement = (
        select(SupplierOrder)
        .join(Order, Order.id == SupplierOrder.order_id)
        .where(Order.payment_status.in_(PAID_STATUSES))
        .options(
            joinedload(SupplierOrder.order),
            joinedload(SupplierOrder.supplier),
            selectinload(SupplierOrder.shipments),
        )
        .order_by(SupplierOrder.created_at.desc())
        .limit(200)
    )
    if user.role == Role.CUSTOMER:
        statement = statement.where(Order.customer_id == user.id)
    elif user.role == Role.SUPPLIER:
        statement = statement.where(SupplierOrder.supplier_id == user.supplier_id)
    elif user.role not in Role.LOGISTICS_DESK:
        raise Forbidden("Chat is not available for this role")

    for supplier_order in db.scalars(statement).unique().all():
        try:
            with db.begin_nested():
                ensure_for_supplier_order(db, supplier_order)
        except IntegrityError:
            # A concurrent request opened the same thread first; its row wins.
            continue


def list_for_user(db: Session, user: User) -> list[Conversation]:
    _backfill(db, user)
    statement = conversation_query()
    if user.role == Role.CUSTOMER:
        statement = statement.where(Conversation.customer_id == user.id)
    elif user.role == Role.SUPPLIER:
        statement = statement.where(Conversation.supplier_id == user.supplier_id)
    return list(
        db.scalars(statement.order_by(Conversation.last_message_at.desc())).unique().all()
    )


def get_for_user(db: Session, user: User, conversation_id: str) -> Conversation:
    conversation = db.scalar(
        conversation_query().where(Conversation.id == conversation_id)
    )
    if conversation is None or party_for(conversation, user) is None:
        raise NotFound("Conversation not found")
    return conversation


def can_handoff(conversation: Conversation) -> bool:
    if conversation.assigned_party != ChatParty.SUPPLIER:
        return False
    supplier_order = conversation.supplier_order
    if supplier_order is None or supplier_order.status == SupplierOrderStatus.CANCELLED:
        return False
    return any(shipment.status != "pending" for shipment in supplier_order.shipments)


def handoff(
    db: Session, *, conversation: Conversation, actor: User, note: str | None
) -> ChatMessage:
    if conversation.assigned_party != ChatParty.SUPPLIER:
        raise Conflict(
            "The logistics desk already handles this conversation", code="already_assigned"
        )
    if not can_handoff(conversation):
        raise Conflict(
            "Hand over once a shipment has been booked", code="not_dispatched"
        )
    supplier_order = conversation.supplier_order
    supplier_name = (
        supplier_order.supplier.trading_name
        if supplier_order and supplier_order.supplier
        else "The supplier"
    )
    note = (note or "").strip()[:500]
    conversation.assigned_party = ChatParty.LOGISTICS
    conversation.handoff_at = _now()
    conversation.handoff_note = note or None
    body = f"{supplier_name} handed this conversation to the Usiri logistics desk."
    if note:
        body = f"{body} Note: {note}"
    return add_message(
        db,
        conversation=conversation,
        author=actor,
        party=ChatParty.SUPPLIER,
        body=body,
        kind=ChatMessageKind.HANDOFF,
    )


def assign(
    db: Session,
    *,
    conversation: Conversation,
    actor: User,
    party: str,
    note: str | None,
) -> ChatMessage | None:
    if party not in {ChatParty.SUPPLIER, ChatParty.LOGISTICS}:
        raise Conflict("Unknown desk assignment", code="invalid_party")
    if conversation.assigned_party == party:
        return None

    note = (note or "").strip()[:500]
    conversation.assigned_party = party
    if party == ChatParty.LOGISTICS:
        conversation.handoff_at = _now()
        conversation.handoff_note = note or None
        body = "The Usiri logistics desk took over this conversation."
    else:
        conversation.handoff_note = note or None
        body = "The conversation was returned to the supplier."
    if note:
        body = f"{body} Note: {note}"
    return add_message(
        db,
        conversation=conversation,
        author=actor,
        party=ChatParty.LOGISTICS,
        body=body,
        kind=ChatMessageKind.HANDOFF,
    )


def shipment_for(conversation: Conversation) -> Shipment | None:
    supplier_order = conversation.supplier_order
    if supplier_order is None or not supplier_order.shipments:
        return None
    return supplier_order.shipments[-1]
