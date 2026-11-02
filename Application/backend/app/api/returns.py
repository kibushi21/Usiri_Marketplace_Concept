from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import CustomerUser, Db
from ..errors import NotFound
from ..models import Order, OrderItem, Return
from ..services import returns as return_service
from .schemas import ReturnCreateIn
from .serializers import return_out

router = APIRouter(tags=["returns"])

RETURN_REASONS = {
    "not_delivered",
    "damaged",
    "wrong_item",
    "not_as_described",
    "changed_mind",
    "faulty",
}


@router.post("/orders/{order_id}/returns", status_code=status.HTTP_201_CREATED)
def create_return(order_id: str, payload: ReturnCreateIn, user: CustomerUser, db: Db):
    order = db.get(Order, order_id)
    if order is None or order.customer_id != user.id:
        raise NotFound("Order not found")
    if payload.reason not in RETURN_REASONS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Choose a valid return reason")
    item = db.get(OrderItem, payload.item_id)
    if item is None or item.order_id != order.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Item does not belong to this order")
    ret = return_service.request_return(
        db, customer=user, item=item, qty=payload.qty, reason=payload.reason, details=payload.details
    )
    db.commit()
    return return_out(ret, item=item)


@router.get("/returns")
def list_returns(user: CustomerUser, db: Db):
    returns = return_service.list_customer_returns(db, user)
    return {"items": [_with_item(db, ret) for ret in returns]}


@router.get("/returns/{return_id}")
def get_return(return_id: str, user: CustomerUser, db: Db):
    ret = db.get(Return, return_id)
    if ret is None or ret.customer_id != user.id:
        raise NotFound("Return not found")
    return _with_item(db, ret)


def _with_item(db: Session, ret: Return) -> dict:
    item = db.get(OrderItem, ret.item_id)
    return return_out(ret, item=item)
