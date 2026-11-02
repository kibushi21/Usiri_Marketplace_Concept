from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from ..models import AuditLog, User


def record(
    db: Session,
    *,
    actor: User | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    ip: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        actor_id=actor.id if actor else None,
        actor_role=actor.role if actor else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before=before,
        after=after,
        ip=ip,
    )
    db.add(entry)
    db.flush()
    return entry


def snapshot(obj: Any, fields: list[str]) -> dict[str, Any]:
    return {field: getattr(obj, field, None) for field in fields}
