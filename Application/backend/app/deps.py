from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .db import get_db
from .models import Role, User
from .security import decode_token

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
    try:
        payload = decode_token(credentials.credentials)
    except Exception as exc:  # jwt errors of several shapes
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token") from exc
    user = db.get(User, payload.get("sub"))
    if user is None or user.status != "active":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Account is not active")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
Db = Annotated[Session, Depends(get_db)]


def require_roles(*roles: str) -> Callable[[User], User]:
    allowed = set(roles)

    def dependency(user: CurrentUser) -> User:
        if user.role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not permitted for this role")
        return user

    return dependency


def require_staff(user: CurrentUser) -> User:
    if user.role not in Role.STAFF:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Staff access required")
    return user


def require_supplier(user: CurrentUser) -> User:
    if user.role != Role.SUPPLIER or not user.supplier_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Supplier account required")
    return user


StaffUser = Annotated[User, Depends(require_staff)]
SupplierUser = Annotated[User, Depends(require_supplier)]
CustomerUser = Annotated[User, Depends(require_roles(Role.CUSTOMER))]


def client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None
