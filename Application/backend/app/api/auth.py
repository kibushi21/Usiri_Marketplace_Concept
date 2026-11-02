from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from ..deps import CurrentUser, Db, client_ip
from ..models import Cart, Consent, Role, User
from ..security import create_access_token, hash_password, verify_password
from ..services import audit
from .schemas import LoginIn, RegisterIn
from .serializers import iso, user_out

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Db, request: Request):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")
    user = User(
        email=email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role=Role.CUSTOMER,
        locale=payload.locale,
        email_verified=False,
    )
    db.add(user)
    db.flush()
    db.add(Cart(user_id=user.id))
    db.add(Consent(user_id=user.id, purpose="account_terms", granted=True))
    db.add(
        Consent(user_id=user.id, purpose="marketing", granted=payload.consent_marketing)
    )
    audit.record(
        db,
        actor=user,
        action="account.registered",
        entity_type="user",
        entity_id=user.id,
        ip=client_ip(request),
    )
    token, expires_at = create_access_token(user)
    db.commit()
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": iso(expires_at),
        "user": user_out(user),
    }


@router.post("/login")
def login(payload: LoginIn, db: Db, request: Request):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    if user.status != "active":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This account is suspended")
    from ..models import utcnow

    user.last_login_at = utcnow()
    audit.record(
        db,
        actor=user,
        action="account.login",
        entity_type="user",
        entity_id=user.id,
        ip=client_ip(request),
    )
    token, expires_at = create_access_token(user)
    db.commit()
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": iso(expires_at),
        "user": user_out(user),
    }


@router.get("/me")
def me(user: CurrentUser, db: Db):
    from ..models import Address

    addresses = db.scalars(select(Address).where(Address.user_id == user.id)).all()
    from .serializers import address_out

    return {
        "user": user_out(user),
        "addresses": [address_out(a) for a in addresses],
    }
