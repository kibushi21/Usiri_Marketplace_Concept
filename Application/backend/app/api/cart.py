from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..deps import CustomerUser, Db
from ..models import (
    Cart,
    CartItem,
    Product,
    ProductStatus,
    ProductVariant,
    SupplierStatus,
)
from ..services import orders as order_service
from ..services.platform_config import load_config
from .schemas import CartAddIn, CartUpdateIn

router = APIRouter(prefix="/cart", tags=["cart"])


def get_cart(db: Session, user_id: str) -> Cart:
    cart = db.scalar(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(
            selectinload(Cart.items)
            .selectinload(CartItem.variant)
            .selectinload(ProductVariant.product)
            .selectinload(Product.supplier)
        )
    )
    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.flush()
    return cart


def cart_payload(db: Session, cart: Cart) -> dict:
    config = load_config(db)
    lines = order_service.cart_lines(db, cart.id)
    priced = order_service.quote(db, lines) if lines else {
        "subtotal": 0,
        "delivery_total": 0,
        "total": 0,
        "suppliers": {},
    }
    items = []
    for item in cart.items:
        variant = item.variant
        product = variant.product
        warnings = []
        if not variant.active or product.status != ProductStatus.ACTIVE:
            warnings.append("This product is no longer available")
        elif product.supplier.status != SupplierStatus.VERIFIED:
            warnings.append("This supplier is temporarily unavailable")
        elif variant.available < item.qty:
            warnings.append(f"Only {variant.available} left")
        items.append(
            {
                "id": item.id,
                "variant_id": variant.id,
                "qty": item.qty,
                "product_id": product.id,
                "product_slug": product.slug,
                "product_name": product.name,
                "variant_name": variant.name,
                "unit_price": variant.price_tzs,
                "line_total": variant.price_tzs * item.qty,
                "available": variant.available,
                "supplier_id": product.supplier_id,
                "supplier_name": product.supplier.trading_name,
                "warnings": warnings,
            }
        )
    supplier_totals = [
        {
            "supplier_id": group.supplier_id,
            "supplier_name": next(
                (i["supplier_name"] for i in items if i["supplier_id"] == group.supplier_id), ""
            ),
            "merchandise_total": group.merchandise_total,
            "delivery_fee": group.delivery_fee,
        }
        for group in priced["suppliers"].values()
    ]
    return {
        "id": cart.id,
        "items": items,
        "item_count": sum(item.qty for item in cart.items),
        "subtotal": priced["subtotal"],
        "delivery_total": priced["delivery_total"],
        "total": priced["total"],
        "supplier_groups": supplier_totals,
        "free_delivery_threshold": config["free_delivery_threshold"],
        "has_warnings": any(item["warnings"] for item in items),
    }


@router.get("")
def view_cart(user: CustomerUser, db: Db):
    cart = get_cart(db, user.id)
    db.commit()
    return cart_payload(db, cart)


@router.post("/items", status_code=status.HTTP_201_CREATED)
def add_item(payload: CartAddIn, user: CustomerUser, db: Db):
    variant = db.get(ProductVariant, payload.variant_id)
    if variant is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product variant not found")
    product = variant.product
    if not variant.active or product.status != ProductStatus.ACTIVE:
        raise HTTPException(status.HTTP_409_CONFLICT, "This product is not available")
    if product.supplier.status != SupplierStatus.VERIFIED:
        raise HTTPException(status.HTTP_409_CONFLICT, "This supplier is temporarily unavailable")
    config = load_config(db)
    max_qty = int(config["max_qty_per_line"])

    cart = get_cart(db, user.id)
    item = db.scalar(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.variant_id == variant.id)
    )
    new_qty = payload.qty + (item.qty if item else 0)
    if new_qty > max_qty:
        raise HTTPException(status.HTTP_409_CONFLICT, f"You can order at most {max_qty} of one item")
    if variant.available < new_qty:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Only {variant.available} left in stock")
    if item:
        item.qty = new_qty
    else:
        db.add(CartItem(cart_id=cart.id, variant_id=variant.id, qty=payload.qty))
    db.commit()
    return cart_payload(db, get_cart(db, user.id))


@router.patch("/items/{item_id}")
def update_item(item_id: str, payload: CartUpdateIn, user: CustomerUser, db: Db):
    cart = get_cart(db, user.id)
    item = db.get(CartItem, item_id)
    if item is None or item.cart_id != cart.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cart item not found")
    if payload.qty == 0:
        db.delete(item)
    else:
        if item.variant.available < payload.qty:
            raise HTTPException(
                status.HTTP_409_CONFLICT, f"Only {item.variant.available} left in stock"
            )
        item.qty = payload.qty
    db.commit()
    return cart_payload(db, get_cart(db, user.id))


@router.delete("/items/{item_id}")
def remove_item(item_id: str, user: CustomerUser, db: Db):
    cart = get_cart(db, user.id)
    item = db.get(CartItem, item_id)
    if item is None or item.cart_id != cart.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cart item not found")
    db.delete(item)
    db.commit()
    return cart_payload(db, get_cart(db, user.id))


@router.delete("")
def clear_cart(user: CustomerUser, db: Db):
    cart = get_cart(db, user.id)
    for item in list(cart.items):
        db.delete(item)
    db.commit()
    return {"items": [], "item_count": 0, "subtotal": 0, "delivery_total": 0, "total": 0}
