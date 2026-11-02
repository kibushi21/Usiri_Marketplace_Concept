from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Request, status
from sqlalchemy import select

from ..deps import CurrentUser, CustomerUser, Db, client_ip
from ..errors import Conflict, Forbidden, NotFound
from ..models import Order, Payment, Refund, Role, User
from ..security import verify_webhook_signature
from ..services import audit, idempotency, notifications, tracking
from ..services import chat as chat_service
from ..services import orders as order_service
from ..services import payments as payment_service
from ..services.platform_config import load_config
from . import cart as cart_api
from .schemas import CheckoutIn, PayIn, SimulateIn
from .serializers import order_out, payment_out, refund_out

router = APIRouter(tags=["orders"])
webhook_router = APIRouter(tags=["webhooks"])


def _payment_out(payment: Payment) -> dict:
    data = payment_out(payment)
    data["redirect_url"] = (payment.raw or {}).get("redirect_url")
    return data


@router.post("/checkout/quote")
def quote_checkout(user: CustomerUser, db: Db):
    cart = cart_api.get_cart(db, user.id)
    payload = cart_api.cart_payload(db, cart)
    issues: list[str] = []
    if not payload["items"]:
        issues.append("Your cart is empty")
    for item in payload["items"]:
        issues.extend(item["warnings"])
    db.commit()
    return {**payload, "can_checkout": not issues, "issues": issues}


@router.post("/checkout", status_code=status.HTTP_201_CREATED)
def checkout(
    payload: CheckoutIn,
    user: CustomerUser,
    db: Db,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    cart = cart_api.get_cart(db, user.id)
    lines = order_service.cart_lines(db, cart.id)
    key_payload = payload.model_dump()

    def action() -> dict:
        if not lines:
            raise Conflict("Your cart is empty", code="empty_cart")
        address = order_service.resolve_address(db, user, payload)
        order = order_service.create_order(db, user, payload, lines, address)
        for supplier_order in order.supplier_orders:
            chat_service.ensure_for_supplier_order(db, supplier_order)
        for item in list(cart.items):
            db.delete(item)
        notifications.notify(
            db,
            user_id=user.id,
            template="order_placed",
            payload={"order_code": order.code, "total": order.total},
        )
        notifications.notify_ops(
            db, "order_placed", {"order_code": order.code, "total": order.total}
        )
        audit.record(
            db,
            actor=user,
            action="order.created",
            entity_type="order",
            entity_id=order.id,
            after={"code": order.code, "total": order.total},
            ip=client_ip(request),
        )
        return {
            "order": order_out(order),
            "payment_required": True,
            "reservation_expires_in_minutes": load_config(db)["reservation_ttl_minutes"],
        }

    result = idempotency.run(
        db, scope="checkout", key=idempotency_key, actor_id=user.id, payload=key_payload, action=action
    )
    db.commit()
    return result


@router.get("/orders")
def list_orders(user: CurrentUser, db: Db):
    if user.role == Role.CUSTOMER:
        orders = order_service.list_customer_orders(db, user)
    elif user.role == Role.SUPPLIER:
        supplier_orders = order_service.list_supplier_orders(db, user.supplier_id or "")
        return {"items": [order_out(so.order) for so in supplier_orders]}
    else:
        return {"items": []}
    return {"items": [order_out(order) for order in orders]}


@router.get("/orders/{order_id}")
def get_order(order_id: str, user: CurrentUser, db: Db):
    order = order_service.get_order(db, order_id)
    if user.role == Role.CUSTOMER and order.customer_id != user.id:
        raise Forbidden("This order belongs to another customer")
    if user.role == Role.SUPPLIER and not any(
        so.supplier_id == user.supplier_id for so in order.supplier_orders
    ):
        raise Forbidden("This order does not involve your supplier account")
    if user.role not in Role.ALL:
        raise Forbidden()
    if user.role == Role.CUSTOMER and tracking.advance_for_order(db, order):
        db.commit()
    return order_out(order, detail=True)


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str, user: CustomerUser, db: Db, reason: str = "Customer changed their mind"):
    order = order_service.get_customer_order(db, user, order_id)
    if order.status == "pending_payment":
        order_service.cancel_unpaid(db, order, actor=user, reason=reason)
    elif order.status == "paid":
        order_service.cancel_paid(db, order, actor=user, reason=reason)
    else:
        raise Conflict("This order can no longer be cancelled online", code="not_cancellable")
    audit.record(
        db, actor=user, action="order.cancelled", entity_type="order", entity_id=order.id
    )
    db.commit()
    return order_out(order_service.get_order(db, order.id), detail=True)


@router.post("/orders/{order_id}/payments", status_code=status.HTTP_201_CREATED)
def pay_order(
    order_id: str,
    payload: PayIn,
    user: CurrentUser,
    db: Db,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    order = order_service.get_order(db, order_id)
    if order.customer_id != user.id:
        raise Forbidden("This order belongs to another customer")

    def action() -> dict:
        payment = payment_service.initiate(
            db, order, method=payload.method, msisdn=payload.msisdn
        )
        audit.record(
            db,
            actor=user,
            action="payment.initiated",
            entity_type="payment",
            entity_id=payment.id,
            after={"order": order.code, "amount": payment.amount},
        )
        return {"payment": _payment_out(payment), "order": order_out(order)}

    result = idempotency.run(
        db,
        scope="payment_initiation",
        key=idempotency_key,
        actor_id=user.id,
        payload={"order_id": order_id, **payload.model_dump()},
        action=action,
    )
    db.commit()
    return result


def _payment_for_actor(db, payment_id: str, user: User) -> Payment:
    payment = db.get(Payment, payment_id)
    if payment is None:
        raise NotFound("Payment not found")
    order = db.get(Order, payment.order_id)
    if order is None:
        raise NotFound("Order not found")
    if user.role == Role.CUSTOMER and order.customer_id != user.id:
        raise Forbidden("This payment belongs to another customer")
    if user.role == Role.SUPPLIER:
        raise Forbidden()
    return payment


@router.get("/payments/{payment_id}")
def get_payment(payment_id: str, user: CurrentUser, db: Db):
    payment = _payment_for_actor(db, payment_id, user)
    return {"payment": _payment_out(payment), "order": order_out(order_service.get_order(db, payment.order_id))}


@router.post("/payments/{payment_id}/verify")
def verify_payment(payment_id: str, user: CurrentUser, db: Db):
    payment = _payment_for_actor(db, payment_id, user)
    payment_service.verify_and_apply(db, payment)
    audit.record(
        db,
        actor=user,
        action="payment.verified",
        entity_type="payment",
        entity_id=payment.id,
        after={"status": payment.status},
    )
    db.commit()
    return {"payment": _payment_out(payment), "order": order_out(order_service.get_order(db, payment.order_id))}


@router.post("/payments/{payment_id}/simulate")
def simulate_payment(payment_id: str, payload: SimulateIn, user: CurrentUser, db: Db):
    payment = _payment_for_actor(db, payment_id, user)
    payment_service.simulate(db, payment, payload.outcome)
    audit.record(
        db,
        actor=user,
        action="payment.simulated",
        entity_type="payment",
        entity_id=payment.id,
        after={"status": payment.status, "outcome": payload.outcome},
    )
    db.commit()
    return {"payment": _payment_out(payment), "order": order_out(order_service.get_order(db, payment.order_id))}


@router.get("/orders/{order_id}/refunds")
def order_refunds(order_id: str, user: CurrentUser, db: Db):
    order = order_service.get_order(db, order_id)
    if user.role == Role.CUSTOMER and order.customer_id != user.id:
        raise Forbidden("This order belongs to another customer")
    refunds = db.scalars(
        select(Refund).where(Refund.order_id == order_id).order_by(Refund.created_at.desc())
    ).all()
    return {"items": [refund_out(refund) for refund in refunds]}


@webhook_router.post("/webhooks/psp")
async def psp_webhook(
    request: Request,
    db: Db,
    x_psp_signature: str | None = Header(default=None, alias="X-PSP-Signature"),
):
    raw = await request.body()
    signature_ok = verify_webhook_signature(raw.decode(errors="replace"), x_psp_signature or "")
    if not signature_ok:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")
    try:
        body = await request.json()
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Malformed payload") from exc
    provider_ref = body.get("provider_ref")
    if not provider_ref:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Missing provider_ref")
    payment = payment_service.handle_webhook(db, provider_ref=provider_ref, signature_ok=True)
    db.commit()
    return {"received": True, "payment_status": payment.status}
