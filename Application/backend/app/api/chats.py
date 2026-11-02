from __future__ import annotations

from typing import Any

import jwt
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from ..db import SessionLocal
from ..deps import CurrentUser, Db
from ..errors import Conflict, Forbidden, NotFound
from ..models import ChatMessage, ChatParty, Role, User
from ..security import decode_token
from ..services import audit, notifications
from ..services import chat as chat_service
from ..services.chat_hub import hub
from .schemas import ChatAssignIn, ChatHandoffIn, ChatMessageIn
from .serializers import chat_message_out, conversation_out

router = APIRouter(tags=["chat"])


def broadcast_chat_message(
    background_tasks: BackgroundTasks,
    *,
    conversation_id: str,
    message: ChatMessage,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "type": "message",
        "conversation_id": conversation_id,
        "message": chat_message_out(message),
    }
    if extra:
        payload.update(extra)
    background_tasks.add_task(hub.broadcast, conversation_id, payload)
    return payload


def _require_chat_role(user: User) -> None:
    if user.role not in {Role.CUSTOMER, Role.SUPPLIER} and user.role not in Role.LOGISTICS_DESK:
        raise Forbidden("Chat is not available for this role")


@router.get("/chats")
def list_chats(user: CurrentUser, db: Db):
    _require_chat_role(user)
    conversations = chat_service.list_for_user(db, user)
    items = [conversation_out(conversation, viewer=user) for conversation in conversations]
    db.commit()
    return {"items": items}


@router.get("/chats/{conversation_id}")
def get_chat(conversation_id: str, user: CurrentUser, db: Db):
    _require_chat_role(user)
    conversation = chat_service.get_for_user(db, user, conversation_id)
    return conversation_out(conversation, viewer=user, detail=True)


@router.post("/chats/{conversation_id}/messages", status_code=status.HTTP_201_CREATED)
def send_message(
    conversation_id: str,
    payload: ChatMessageIn,
    user: CurrentUser,
    db: Db,
    background_tasks: BackgroundTasks,
):
    conversation = chat_service.get_for_user(db, user, conversation_id)
    party = chat_service.party_for(conversation, user)
    if party == ChatParty.LOGISTICS and conversation.assigned_party != ChatParty.LOGISTICS:
        raise Conflict(
            "Take over the conversation before replying", code="desk_not_assigned"
        )

    message = chat_service.add_message(
        db,
        conversation=conversation,
        author=user,
        party=party or ChatParty.CUSTOMER,
        body=payload.body,
    )
    body = chat_message_out(message)
    db.commit()
    broadcast_chat_message(
        background_tasks, conversation_id=conversation.id, message=message
    )
    return {"message": body}


@router.post("/chats/{conversation_id}/handoff")
def handoff_chat(
    conversation_id: str,
    payload: ChatHandoffIn,
    user: CurrentUser,
    db: Db,
    background_tasks: BackgroundTasks,
):
    conversation = chat_service.get_for_user(db, user, conversation_id)
    if chat_service.party_for(conversation, user) != ChatParty.SUPPLIER:
        raise Forbidden("Only the supplier can hand this conversation over")

    message = chat_service.handoff(
        db, conversation=conversation, actor=user, note=payload.note
    )
    notifications.notify_ops(
        db,
        "chat_handoff",
        {
            "conversation": conversation.code,
            "order_code": conversation.supplier_order.order.code
            if conversation.supplier_order and conversation.supplier_order.order
            else None,
        },
    )
    audit.record(
        db,
        actor=user,
        action="chat.handed_off",
        entity_type="conversation",
        entity_id=conversation.id,
        after={"assigned_party": conversation.assigned_party, "note": conversation.handoff_note},
    )
    data = chat_message_out(message)
    db.commit()
    broadcast_chat_message(
        background_tasks,
        conversation_id=conversation.id,
        message=message,
        extra={"assigned_party": conversation.assigned_party},
    )
    return {
        "conversation": conversation_out(conversation, viewer=user, detail=True),
        "message": data,
    }


@router.post("/chats/{conversation_id}/assign")
def assign_chat(
    conversation_id: str,
    payload: ChatAssignIn,
    user: CurrentUser,
    db: Db,
    background_tasks: BackgroundTasks,
):
    conversation = chat_service.get_for_user(db, user, conversation_id)
    if chat_service.party_for(conversation, user) != ChatParty.LOGISTICS:
        raise Forbidden("Only the logistics desk can reassign this conversation")

    before = conversation.assigned_party
    message = chat_service.assign(
        db,
        conversation=conversation,
        actor=user,
        party=payload.party,
        note=payload.note,
    )
    audit.record(
        db,
        actor=user,
        action="chat.assigned",
        entity_type="conversation",
        entity_id=conversation.id,
        before={"assigned_party": before},
        after={"assigned_party": conversation.assigned_party},
    )
    data = chat_message_out(message) if message else None
    db.commit()
    if message is not None:
        broadcast_chat_message(
            background_tasks,
            conversation_id=conversation.id,
            message=message,
            extra={"assigned_party": conversation.assigned_party},
        )
    return {
        "conversation": conversation_out(conversation, viewer=user, detail=True),
        "message": data,
    }


@router.websocket("/chats/{conversation_id}/ws")
async def chat_socket(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(default=""),
):
    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError:
        payload = None

    with SessionLocal() as db:
        user = db.get(User, payload.get("sub")) if payload else None
        if user is None or user.status != "active":
            await websocket.close(code=4401)
            return
        try:
            conversation = chat_service.get_for_user(db, user, conversation_id)
        except (NotFound, Forbidden):
            await websocket.close(code=4403)
            return
        conversation_id = conversation.id

    await websocket.accept()
    await hub.join(conversation_id, websocket)
    try:
        await websocket.send_json({"type": "ready", "conversation_id": conversation_id})
        while True:
            raw = await websocket.receive_text()
            if raw == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    finally:
        hub.leave(conversation_id, websocket)
