from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..errors import Conflict, DomainError
from ..models import IdempotencyRecord


def fingerprint(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(encoded.encode()).hexdigest()


def run(
    db: Session,
    *,
    scope: str,
    key: str | None,
    actor_id: str | None,
    payload: Any,
    action: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    if not key:
        return action()
    if len(key) > 120:
        raise DomainError("Idempotency key is too long", code="invalid_idempotency_key")

    record = db.scalar(
        select(IdempotencyRecord).where(
            IdempotencyRecord.scope == scope, IdempotencyRecord.key == key
        )
    )
    digest = fingerprint(payload)
    if record is not None:
        if record.request_hash != digest:
            raise Conflict(
                "This idempotency key was already used with a different request",
                code="idempotency_conflict",
            )
        return record.response

    response = action()
    db.add(
        IdempotencyRecord(
            scope=scope,
            key=key,
            actor_id=actor_id,
            request_hash=digest,
            status_code=201,
            response=response,
        )
    )
    db.flush()
    return response
