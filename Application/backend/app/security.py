from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from .config import get_settings
from .models import User

_hasher = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1, hash_len=32, salt_len=16)


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def create_access_token(user: User) -> tuple[str, datetime]:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    payload: dict[str, Any] = {
        "sub": user.id,
        "role": user.role,
        "name": user.full_name,
        "sid": user.supplier_id,
        "iat": datetime.now(UTC),
        "exp": expires_at,
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_at


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def new_webhook_signature(payload: str, secret: str | None = None) -> str:
    import hashlib
    import hmac

    key = (secret or get_settings().psp_webhook_secret).encode()
    return hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()


def verify_webhook_signature(payload: str, signature: str) -> bool:
    expected = new_webhook_signature(payload)
    return secrets.compare_digest(expected, signature or "")
