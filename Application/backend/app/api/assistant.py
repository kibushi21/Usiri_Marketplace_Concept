from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials

from ..adapters.assistant import AssistantUnavailable
from ..deps import Db, bearer, client_ip, get_current_user
from ..models import Role
from ..services import assistant as assistant_service
from .schemas import AssistantChatIn
from .serializers import product_summary

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat")
def chat(
    payload: AssistantChatIn,
    db: Db,
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
):
    if payload.audience == "ops":
        if credentials is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
        user = get_current_user(credentials, db)
        if user.role not in Role.STAFF:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Staff access required")

    try:
        result = assistant_service.ask(
            db,
            question=payload.message,
            history=[entry.model_dump() for entry in payload.history],
            audience=payload.audience,
            client_key=client_ip(request) or "anonymous",
        )
    except assistant_service.RateLimited as exc:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many messages. Try again in a minute.",
        ) from exc
    except AssistantUnavailable as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc

    result["products"] = [product_summary(product) for product in result["products"]]
    return result
