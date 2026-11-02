from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..errors import Conflict, Forbidden, NotFound
from ..models import (
    Address,
    CartItem,
    ItemStatus,
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus,
    ProductVariant,
    Reservation,
    Shipment,
    SupplierOrder,
    SupplierOrderStatus,
    SupplierStatus,
    User,
)
from . import inventory, notifications, numbering
from .platform_config import load_config
from .pricing import QuoteLine, build_quote


def _now() -> datetime:
    return datetime.now(UTC)


def cart_lines(db: Session, cart_id: str) -> list[QuoteLine]:
    items = db.scalars(
        select(CartItem)
        .where(CartItem.cart_id == cart_id)
        .options(selectinload(CartItem.variant).selectinload(ProductVariant.product))
        .order_by(CartItem.added_at)
    ).all()
    return [QuoteLine(variant=item.variant, qty=item.qty) for item in items]


def validate_lines(db: Session, lines: list[QuoteLine]) -> None:
    config = load_config(db)
    max_qty = int(config["max_qty_per_line"])
    if not lines:
        raise Conflict("Your cart is empty", code="empty_cart")
    for line in lines:
        variant = line.variant
        product = variant.product
        if not variant.active or product.status != "active":
            raise Conflict(f"{product.name} is not available", code="product_unavailable")
        if product.supplier.status != SupplierStatus.VERIFIED:
            raise Conflict(f"{product.name} is temporarily unavailable", code="supplier_unavailable")
        if line.qty < 1:
            raise Conflict("Quantity must be at least one", code="invalid_quantity")
        if line.qty > max_qty:
            raise Conflict(f"You can order at most {max_qty} of one item", code="quantity_limit")
        if variant.available < line.qty:
            raise Conflict(
                f"Only {variant.available} left of {product.name} ({variant.name})",
                code="insufficient_stock",
            )


def quote(db: Session, lines: list[QuoteLine]) -> dict:
    config = load_config(db)
    suppliers = {line.variant.product.supplier_id: line.variant.product.supplier for line in lines}
    return build_quote(lines, config, suppliers)


def resolve_address(db: Session, customer: User, payload) -> Address:
    if payload.address_id:
        address = db.get(Address, payload.address_id)
        if address is None or address.user_id != customer.id:
            raise NotFound("Address not found")
        return address
    required = [payload.recipient_name, payload.phone, payload.region, payload.district, payload.street]
    if not all(required):
        raise Conflict("A delivery address is required", code="address_required")
    address = Address(
        user_id=customer.id,
        label=payload.label or "Delivery",
        recipient_name=payload.recipient_name,
        phone=payload.phone,
        region=payload.region,
        district=payload.district,
        ward=payload.ward,
        street=payload.street,
        landmark=payload.landmark,
    )
    db.add(address)
    db.flush()
    return address


def create_order(db: Session, customer: User, payload, lines: list[QuoteLine], address: Address) -> Order:
    validate_lines(db, lines)
    priced = quote(db, lines)
    config = load_config(db)

    order = Order(
        code=numbering.next_order_code(db),
        customer_id=customer.id,
        status=OrderStatus.PENDING_PAYMENT,
        payment_status=PaymentStatus.UNPAID,
        subtotal=priced["subtotal"],
        delivery_total=priced["delivery_total"],
        total=priced["total"],
        notes=payload.notes,
        ship_recipient=address.recipient_name,
        ship_phone=address.phone,
        ship_region=address.region,
        ship_district=address.district,
        ship_ward=address.ward,
        ship_street=address.street,
        ship_landmark=address.landmark,
    )
    db.add(order)
    db.flush()

    for supplier_id, group in priced["suppliers"].items():
        supplier_order = SupplierOrder(
            code=numbering.next_supplier_order_code(db),
            order_id=order.id,
            supplier_id=supplier_id,
            status=SupplierOrderStatus.AWAITING_ACCEPTANCE,
            merchandise_total=group.merchandise_total,
            delivery_fee=group.delivery_fee,
            commission_bp=group.commission_bp,
            commission_amount=group.commission_amount,
            supplier_payable=group.supplier_payable,
        )
        db.add(supplier_order)
        db.flush()
        for line in group.lines:
            product = line.variant.product
            db.add(
                OrderItem(
                    order_id=order.id,
                    supplier_order_id=supplier_order.id,
                    variant_id=line.variant.id,
                    supplier_id=supplier_id,
                    product_name=product.name,
                    variant_name=line.variant.name,
                    sku=line.variant.sku,
                    unit_price=line.unit_price,
                    qty=line.qty,
                    line_total=line.line_total,
                    status=ItemStatus.PENDING,
                )
            )
    db.flush()
    db.refresh(order)

    ttl = int(config["reservation_ttl_minutes"])
    for line in lines:
        variant = inventory.get_variant_for_update(db, line.variant.id)
        if variant is None or variant.available < line.qty:
            raise Conflict("Stock changed while placing the order", code="insufficient_stock")
        inventory.reserve(db, variant=variant, qty=line.qty, order_id=order.id, ttl_minutes=ttl)

    db.flush()
    db.refresh(order)
    return order


def order_query():
    return select(Order).options(
        selectinload(Order.items),
        selectinload(Order.supplier_orders).selectinload(SupplierOrder.items),
        selectinload(Order.supplier_orders).selectinload(SupplierOrder.supplier),
        selectinload(Order.supplier_orders).selectinload(SupplierOrder.shipments).selectinload(
            Shipment.events
        ),
    )


def get_order(db: Session, order_id: str) -> Order:
    order = db.scalar(order_query().where(Order.id == order_id))
    if order is None:
        raise NotFound("Order not found")
    return order


def get_customer_order(db: Session, customer: User, order_id: str) -> Order:
    order = get_order(db, order_id)
    if order.customer_id != customer.id:
        raise Forbidden("This order belongs to another customer")
    return order


def list_customer_orders(db: Session, customer: User) -> list[Order]:
    return list(
        db.scalars(
            order_query().where(Order.customer_id == customer.id).order_by(Order.placed_at.desc())
        )
    )


def list_supplier_orders(db: Session, supplier_id: str) -> list[SupplierOrder]:
    return list(
        db.scalars(
            select(SupplierOrder)
            .where(SupplierOrder.supplier_id == supplier_id)
            .options(
                selectinload(SupplierOrder.items),
                selectinload(SupplierOrder.order),
                selectinload(SupplierOrder.shipments).selectinload(Shipment.events),
            )
            .order_by(SupplierOrder.created_at.desc())
        )
    )


def cancel_unpaid(db: Session, order: Order, *, actor: User, reason: str) -> Order:
    if order.status != OrderStatus.PENDING_PAYMENT:
        raise Conflict("Only orders awaiting payment can be cancelled this way", code="not_cancellable")
    order.status = OrderStatus.CANCELLED
    order.cancelled_at = _now()
    order.cancellation_reason = reason
    inventory.release_order(db, order.id)
    notifications.notify(
        db, user_id=order.customer_id, template="order_cancelled", payload={"order_code": order.code}
    )
    db.flush()
    return order


def cancel_paid(db: Session, order: Order, *, actor: User, reason: str) -> Order:
    """Cancel after capture but before any supplier accepts; refunds and restocks."""
    from . import refunds

    if order.status not in {OrderStatus.PAID}:
        raise Conflict("Only paid orders awaiting supplier acceptance can be cancelled", code="not_cancellable")
    if any(so.status != SupplierOrderStatus.AWAITING_ACCEPTANCE for so in order.supplier_orders):
        raise Conflict(
            "A supplier has already started preparing this order; please use returns",
            code="already_being_fulfilled",
        )
    for so in order.supplier_orders:
        refunds.create_refund(
            db,
            supplier_order=so,
            merchandise_amount=so.merchandise_total - so.refunded_merchandise,
            delivery_amount=so.delivery_fee - so.refunded_delivery,
            reason=f"Customer cancelled {order.code}: {reason}",
            actor=actor,
        )

    restock_order(db, order)
    for so in order.supplier_orders:
        so.status = SupplierOrderStatus.CANCELLED
        so.rejection_reason = reason
        for item in so.items:
            if item.status == ItemStatus.PENDING:
                item.status = ItemStatus.CANCELLED

    order.status = OrderStatus.CANCELLED
    order.cancelled_at = _now()
    order.cancellation_reason = reason
    notifications.notify(
        db, user_id=order.customer_id, template="order_cancelled", payload={"order_code": order.code}
    )
    db.flush()
    return order


def restock_order(db: Session, order: Order) -> None:
    for item in order.items:
        variant = inventory.get_variant_for_update(db, item.variant_id)
        if variant is not None and item.status == ItemStatus.PENDING:
            variant.on_hand += item.qty
    db.flush()


def recompute_order_status(db: Session, order: Order) -> None:
    if order.status in {OrderStatus.CANCELLED, OrderStatus.PENDING_PAYMENT}:
        return
    supplier_orders = list(order.supplier_orders)
    if not supplier_orders:
        return
    active = {
        SupplierOrderStatus.ACCEPTED,
        SupplierOrderStatus.READY,
        SupplierOrderStatus.IN_TRANSIT,
    }
    closed = {
        SupplierOrderStatus.DELIVERED,
        SupplierOrderStatus.COMPLETED,
        SupplierOrderStatus.CANCELLED,
    }
    if any(so.status in active for so in supplier_orders):
        order.status = OrderStatus.FULFILLING
    if all(so.status in closed for so in supplier_orders):
        delivered = any(so.status in {SupplierOrderStatus.DELIVERED, SupplierOrderStatus.COMPLETED} for so in supplier_orders)
        order.status = OrderStatus.COMPLETED if delivered else OrderStatus.CANCELLED
        if order.status == OrderStatus.COMPLETED:
            order.completed_at = _now()
        else:
            order.cancelled_at = _now()
            order.cancellation_reason = "All supplier orders were cancelled"
    if order.refunded_total >= order.total:
        order.payment_status = PaymentStatus.REFUNDED
    elif order.refunded_total > 0:
        order.payment_status = PaymentStatus.PARTIALLY_REFUNDED
    elif order.payment_status != PaymentStatus.PAID:
        order.payment_status = PaymentStatus.PAID
    db.flush()


def reservations_left(db: Session, order_id: str) -> int:
    return len(
        db.scalars(
            select(Reservation).where(
                Reservation.order_id == order_id, Reservation.status == "held"
            )
        ).all()
    )
