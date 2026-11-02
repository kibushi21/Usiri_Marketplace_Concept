from __future__ import annotations

import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .api import (
    assistant,
    auth,
    cart,
    catalogue,
    chats,
    ops,
    orders,
    returns,
    supplier,
    support,
)
from .config import get_settings
from .db import Base, SessionLocal, engine
from .errors import DomainError
from .seed import seed
from .services import inventory, tracking
from .services.platform_config import load_config

logger = logging.getLogger("usiri")
settings = get_settings()

SWEEP_INTERVAL_SECONDS = 60


async def _sweeper() -> None:
    while True:
        try:
            with SessionLocal() as db:
                released = inventory.expire_reservations(db)
                advanced = tracking.advance_due(db)
                if released or advanced:
                    db.commit()
                    if released:
                        logger.info("released %s expired reservations", released)
                    if advanced:
                        logger.info("recorded %s carrier tracking events", advanced)
        except Exception:  # pragma: no cover - background resilience
            logger.exception("reservation sweeper failed")
        await asyncio.sleep(SWEEP_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.environment != "production":
        Base.metadata.create_all(engine)
        with SessionLocal() as db:
            seed(db)
    task = asyncio.create_task(_sweeper())
    try:
        yield
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Usiri marketplace API — managed, multi-supplier, Tanzania first.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Idempotency-Key"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(_: Request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(_: Request, exc: IntegrityError):
    logger.warning("integrity error: %s", exc)
    return JSONResponse(
        status_code=409,
        content={"detail": "That action conflicts with an existing record", "code": "conflict"},
    )


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok", "environment": settings.environment}


@app.get("/api/meta", tags=["meta"])
def meta():
    with SessionLocal() as db:
        config = load_config(db)
    return {
        "platform": config["platform_name"],
        "currency": config["currency"],
        "delivery_fee_flat": config["delivery_fee_flat"],
        "free_delivery_threshold": config["free_delivery_threshold"],
        "return_window_days": config["return_window_days"],
        "reservation_ttl_minutes": config["reservation_ttl_minutes"],
        "support_email": config["support_email"],
        "support_phone": config["support_phone"],
        "providers": {
            "payments": settings.psp_provider,
            "carrier": settings.carrier_provider,
            "assistant": settings.llm_provider,
        },
    }


for module in (assistant, auth, catalogue, cart, chats, orders, returns, support, supplier, ops):
    app.include_router(module.router, prefix="/api")
app.include_router(orders.webhook_router, prefix="/api")
