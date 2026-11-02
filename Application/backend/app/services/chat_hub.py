from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("usiri.chat")


class ChatHub:
    """In-process fan-out for open conversation sockets.

    Each backend process owns its sockets; a multi-worker deployment would need
    a shared broker such as Redis pub/sub.
    """

    def __init__(self) -> None:
        self._rooms: dict[str, set[WebSocket]] = defaultdict(set)

    async def join(self, conversation_id: str, websocket: WebSocket) -> None:
        self._rooms[conversation_id].add(websocket)

    def leave(self, conversation_id: str, websocket: WebSocket) -> None:
        room = self._rooms.get(conversation_id)
        if room is None:
            return
        room.discard(websocket)
        if not room:
            self._rooms.pop(conversation_id, None)

    async def broadcast(self, conversation_id: str, payload: dict[str, Any]) -> None:
        room = self._rooms.get(conversation_id)
        if not room:
            return
        for websocket in list(room):
            try:
                await websocket.send_json(payload)
            except Exception:  # noqa: BLE001 - transport errors vary by server
                logger.debug("dropping closed chat socket for %s", conversation_id)
                self.leave(conversation_id, websocket)


hub = ChatHub()
