from __future__ import annotations

import re

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from ..deps import Db, SupplierUser
from ..errors import Conflict, Forbidden, NotFound
from ..models import (
    Category,
    Department,
    Order,
    OrderItem,
    Payout,
    Product,
    ProductStatus,
    ProductVariant,
    Return,
    Shipment,
    Supplier,
    SupplierOrder,
)
from ..services import audit, reports
from ..services import chat as chat_service
from ..services import payouts as payout_service
from ..services import supplier_orders as supplier_service
from ..services.platform_config import load_config
from .chats import broadcast_chat_message
from .schemas import AcceptIn, DeliverIn, ProductIn, RejectIn, ShipIn, StockUpdateIn
from .serializers import (
    payout_out,
    return_out,
    supplier_order_with_order,
    supplier_out,
    supplier_product_out,
)

router = APIRouter(prefix="/supplier", tags=["supplier"])


def _supplier(db, user) -> Supplier:
    supplier = db.get(Supplier, user.supplier_id)
    if supplier is None:
        raise NotFound("Supplier profile not found")
    return supplier


@router.get("/dashboard")
def dashboard(user: SupplierUser, db: Db):
    supplier = _supplier(db, user)
    orders = db.scalars(
        select(SupplierOrder)
        .where(SupplierOrder.supplier_id == supplier.id)
        .options(selectinload(SupplierOrder.items), selectinload(SupplierOrder.order))
        .order_by(SupplierOrder.created_at.desc())
        .limit(8)
    ).all()
    return {
        "supplier": supplier_out(supplier),
        "balance": payout_service.supplier_balance(db, supplier.id),
        "summary": reports.supplier_summary(db, supplier.id),
        "recent_orders": [supplier_order_with_order(so) for so in orders],
        "config": {
            "payout_hold_days": load_config(db)["payout_hold_days"],
            "commission_bp": supplier.commission_bp
            if supplier.commission_bp is not None
            else load_config(db)["commission_bp"],
        },
    }


@router.get("/orders")
def list_orders(user: SupplierUser, db: Db, status_filter: str | None = None):
    supplier = _supplier(db, user)
    query = (
        select(SupplierOrder)
        .where(SupplierOrder.supplier_id == supplier.id)
        .options(
            selectinload(SupplierOrder.items),
            selectinload(SupplierOrder.shipments).selectinload(Shipment.events),
            selectinload(SupplierOrder.order),
        )
        .order_by(SupplierOrder.created_at.desc())
    )
    if status_filter:
        query = query.where(SupplierOrder.status == status_filter)
    orders = db.scalars(query).all()
    return {"items": [supplier_order_with_order(so) for so in orders]}


@router.get("/orders/{supplier_order_id}")
def get_order(supplier_order_id: str, user: SupplierUser, db: Db):
    so = supplier_service.get_supplier_order(db, supplier_order_id)
    supplier_service.assert_owner(so, user)
    return supplier_order_with_order(so)


@router.post("/orders/{supplier_order_id}/accept")
def accept_order(supplier_order_id: str, payload: AcceptIn, user: SupplierUser, db: Db):
    so = supplier_service.get_supplier_order(db, supplier_order_id)
    supplier_service.assert_owner(so, user)
    before = {"status": so.status}
    supplier_service.accept(
        db,
        so=so,
        actor=user,
        accepted_item_ids=payload.accepted_item_ids,
        rejection_reason=payload.rejection_reason,
    )
    audit.record(
        db,
        actor=user,
        action="supplier_order.accepted",
        entity_type="supplier_order",
        entity_id=so.id,
        before=before,
        after={"status": so.status},
    )
    db.commit()
    return supplier_order_with_order(supplier_service.get_supplier_order(db, so.id))


@router.post("/orders/{supplier_order_id}/reject")
def reject_order(supplier_order_id: str, payload: RejectIn, user: SupplierUser, db: Db):
    so = supplier_service.get_supplier_order(db, supplier_order_id)
    supplier_service.assert_owner(so, user)
    supplier_service.reject(db, so=so, actor=user, reason=payload.reason)
    audit.record(
        db,
        actor=user,
        action="supplier_order.rejected",
        entity_type="supplier_order",
        entity_id=so.id,
        after={"reason": payload.reason},
    )
    db.commit()
    return supplier_order_with_order(supplier_service.get_supplier_order(db, so.id))


@router.post("/orders/{supplier_order_id}/ready")
def ready_order(supplier_order_id: str, user: SupplierUser, db: Db):
    so = supplier_service.get_supplier_order(db, supplier_order_id)
    supplier_service.assert_owner(so, user)
    supplier_service.mark_ready(db, so=so, actor=user)
    db.commit()
    return supplier_order_with_order(supplier_service.get_supplier_order(db, so.id))


@router.post("/orders/{supplier_order_id}/ship")
def ship_order(
    supplier_order_id: str,
    payload: ShipIn,
    user: SupplierUser,
    db: Db,
    background_tasks: BackgroundTasks,
):
    so = supplier_service.get_supplier_order(db, supplier_order_id)
    supplier_service.assert_owner(so, user)
    shipment = supplier_service.ship(
        db,
        so=so,
        actor=user,
        carrier=payload.carrier,
        tracking_number=payload.tracking_number,
        fee=payload.fee,
    )
    conversation, message = chat_service.system_for_order(
        db,
        so,
        f"Shipment booked with {shipment.carrier}. "
        f"Tracking {shipment.tracking_number or 'pending'}. "
        "The supplier can hand delivery questions to the Usiri logistics desk from here.",
    )
    audit.record(
        db,
        actor=user,
        action="shipment.dispatched",
        entity_type="supplier_order",
        entity_id=so.id,
        after={"tracking": shipment.tracking_number, "carrier": shipment.carrier},
    )
    db.commit()
    broadcast_chat_message(
        background_tasks, conversation_id=conversation.id, message=message
    )
    return supplier_order_with_order(supplier_service.get_supplier_order(db, so.id))


@router.post("/orders/{supplier_order_id}/deliver")
def deliver_order(
    supplier_order_id: str,
    payload: DeliverIn,
    user: SupplierUser,
    db: Db,
    background_tasks: BackgroundTasks,
):
    so = supplier_service.get_supplier_order(db, supplier_order_id)
    supplier_service.assert_owner(so, user)
    supplier_service.deliver(db, so=so, actor=user, pod_ref=payload.pod_ref, note=payload.note)
    conversation, message = chat_service.system_for_order(
        db,
        so,
        "Delivery recorded. The payout hold has started.",
    )
    audit.record(
        db,
        actor=user,
        action="shipment.delivered",
        entity_type="supplier_order",
        entity_id=so.id,
        after={"pod": payload.pod_ref},
    )
    db.commit()
    broadcast_chat_message(
        background_tasks, conversation_id=conversation.id, message=message
    )
    return supplier_order_with_order(supplier_service.get_supplier_order(db, so.id))


def _slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return base[:120] or "product"


@router.get("/products")
def list_products(user: SupplierUser, db: Db):
    supplier = _supplier(db, user)
    products = db.scalars(
        select(Product)
        .where(Product.supplier_id == supplier.id)
        .options(selectinload(Product.variants), joinedload(Product.supplier))
        .order_by(Product.created_at.desc())
    ).all()
    return {"items": [supplier_product_out(p) for p in products]}


@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductIn, user: SupplierUser, db: Db):
    supplier = _supplier(db, user)
    department = db.get(Department, payload.department_id)
    if department is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unknown department")
    if payload.category_id:
        category = db.get(Category, payload.category_id)
        if category is None or category.department_id != department.id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Category does not belong to the department")

    slug = _slugify(payload.name)
    existing = db.scalar(select(Product).where(Product.slug == slug))
    if existing:
        slug = f"{slug}-{supplier.code.lower()}"

    product = Product(
        supplier_id=supplier.id,
        department_id=department.id,
        category_id=payload.category_id,
        slug=slug,
        name=payload.name,
        description=payload.description,
        brand=payload.brand,
        status=ProductStatus.ACTIVE
        if supplier.status == "verified"
        else ProductStatus.DRAFT,
        attributes={"department": department.slug, "origin": "Tanzania"},
    )
    db.add(product)
    db.flush()
    for index, variant in enumerate(payload.variants):
        db.add(
            ProductVariant(
                product_id=product.id,
                sku=variant.sku or f"USR-{product.id[:6].upper()}-{index + 1:02d}",
                name=variant.name,
                price_tzs=variant.price,
                on_hand=variant.on_hand,
                weight_g=variant.weight_g,
            )
        )
    audit.record(
        db,
        actor=user,
        action="product.created",
        entity_type="product",
        entity_id=product.id,
        after={"name": product.name, "slug": product.slug},
    )
    db.commit()
    product = db.scalar(
        select(Product)
        .where(Product.id == product.id)
        .options(selectinload(Product.variants), joinedload(Product.supplier))
    )
    note = "Published to the catalogue" if product.status == ProductStatus.ACTIVE else "Submitted for catalogue review"
    return {**supplier_product_out(product), "note": note}


@router.patch("/variants/{variant_id}")
def update_variant(variant_id: str, payload: StockUpdateIn, user: SupplierUser, db: Db):
    variant = db.get(ProductVariant, variant_id)
    if variant is None:
        raise NotFound("Variant not found")
    if variant.product.supplier_id != user.supplier_id:
        raise Forbidden("This product belongs to another supplier")
    before = {"on_hand": variant.on_hand, "price": variant.price_tzs, "active": variant.active}
    if payload.on_hand is not None:
        if payload.on_hand < variant.reserved:
            raise Conflict(
                f"{variant.reserved} units are reserved by open orders", code="stock_below_reserved"
            )
        variant.on_hand = payload.on_hand
    if payload.price is not None:
        variant.price_tzs = payload.price
    if payload.active is not None:
        variant.active = payload.active
    audit.record(
        db,
        actor=user,
        action="variant.updated",
        entity_type="variant",
        entity_id=variant.id,
        before=before,
        after={"on_hand": variant.on_hand, "price": variant.price_tzs, "active": variant.active},
    )
    db.commit()
    return {
        "id": variant.id,
        "sku": variant.sku,
        "name": variant.name,
        "price": variant.price_tzs,
        "on_hand": variant.on_hand,
        "reserved": variant.reserved,
        "available": variant.available,
        "active": variant.active,
    }


@router.get("/payouts")
def list_payouts(user: SupplierUser, db: Db):
    payouts = db.scalars(
        select(Payout)
        .where(Payout.supplier_id == user.supplier_id)
        .order_by(Payout.created_at.desc())
    ).all()
    return {"items": [payout_out(p) for p in payouts]}


@router.get("/returns")
def list_returns(user: SupplierUser, db: Db):
    returns = db.scalars(
        select(Return)
        .join(SupplierOrder, SupplierOrder.id == Return.supplier_order_id)
        .where(SupplierOrder.supplier_id == user.supplier_id)
        .order_by(Return.created_at.desc())
    ).all()
    items = []
    for ret in returns:
        item = db.get(OrderItem, ret.item_id)
        order = db.get(Order, ret.order_id)
        data = return_out(ret, item=item)
        data["order_code"] = order.code if order else None
        items.append(data)
    return {"items": items}
