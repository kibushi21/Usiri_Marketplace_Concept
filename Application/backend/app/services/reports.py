from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import (
    ItemStatus,
    Order,
    OrderItem,
    PaymentStatus,
    Payout,
    Product,
    ProductVariant,
    Refund,
    RefundStatus,
    Return,
    ReturnStatus,
    Supplier,
    SupplierOrder,
    SupplierOrderStatus,
)
from . import ledger


def summary(db: Session) -> dict:
    paid_orders = db.scalar(
        select(func.count(Order.id)).where(Order.payment_status != PaymentStatus.UNPAID)
    ) or 0
    gmv = db.scalar(
        select(func.coalesce(func.sum(Order.total), 0)).where(
            Order.payment_status != PaymentStatus.UNPAID
        )
    ) or 0
    refunded = db.scalar(
        select(func.coalesce(func.sum(Refund.amount), 0)).where(
            Refund.status == RefundStatus.SUCCEEDED
        )
    ) or 0
    pending_payouts = db.scalar(
        select(func.count(Payout.id)).where(Payout.status.in_(["pending_approval", "approved"]))
    ) or 0
    pending_payout_value = db.scalar(
        select(func.coalesce(func.sum(Payout.amount), 0)).where(
            Payout.status.in_(["pending_approval", "approved"])
        )
    ) or 0
    open_returns = db.scalar(
        select(func.count(Return.id)).where(
            Return.status.in_([ReturnStatus.REQUESTED, ReturnStatus.APPROVED])
        )
    ) or 0

    statuses = {
        row[0]: row[1]
        for row in db.execute(select(Order.status, func.count(Order.id)).group_by(Order.status))
    }
    supplier_statuses = {
        row[0]: row[1]
        for row in db.execute(
            select(SupplierOrder.status, func.count(SupplierOrder.id)).group_by(
                SupplierOrder.status
            )
        )
    }
    awaiting_suppliers = db.scalar(
        select(func.count(SupplierOrder.id)).where(
            SupplierOrder.status == SupplierOrderStatus.AWAITING_ACCEPTANCE
        )
    ) or 0

    low_stock = db.execute(
        select(Product.name, ProductVariant.sku, ProductVariant.on_hand, ProductVariant.reserved)
        .join(Product, Product.id == ProductVariant.product_id)
        .where(ProductVariant.on_hand - ProductVariant.reserved <= 3, ProductVariant.active.is_(True))
        .limit(20)
    ).all()

    top_products = db.execute(
        select(
            OrderItem.product_name,
            func.sum(OrderItem.qty),
            func.sum(OrderItem.line_total),
        )
        .join(Order, Order.id == OrderItem.order_id)
        .where(
            Order.payment_status != PaymentStatus.UNPAID,
            OrderItem.status != ItemStatus.REJECTED,
        )
        .group_by(OrderItem.product_name)
        .order_by(func.sum(OrderItem.line_total).desc())
        .limit(5)
    ).all()

    return {
        "orders_paid": paid_orders,
        "gmv": int(gmv),
        "refunds": int(refunded),
        "net_gmv": int(gmv) - int(refunded),
        "commission_earned": ledger.account_balance(db, "platform_revenue"),
        "delivery_earned": ledger.account_balance(db, "delivery_revenue"),
        "supplier_payable": ledger.account_balance(db, "supplier_payable"),
        "cash_at_psp": ledger.account_balance(db, "psp_clearing"),
        "orders_by_status": statuses,
        "supplier_orders_by_status": supplier_statuses,
        "awaiting_supplier_acceptance": awaiting_suppliers,
        "pending_payouts": pending_payouts,
        "pending_payout_value": int(pending_payout_value),
        "open_returns": open_returns,
        "low_stock": [
            {"product": row[0], "sku": row[1], "on_hand": row[2], "reserved": row[3]}
            for row in low_stock
        ],
        "top_products": [
            {"product": row[0], "qty": int(row[1]), "value": int(row[2])} for row in top_products
        ],
    }


def supplier_summary(db: Session, supplier_id: str) -> dict:
    rows = db.execute(
        select(SupplierOrder.status, func.count(SupplierOrder.id), func.coalesce(func.sum(SupplierOrder.supplier_payable), 0))
        .where(SupplierOrder.supplier_id == supplier_id)
        .group_by(SupplierOrder.status)
    ).all()
    commission = db.scalar(
        select(func.coalesce(func.sum(SupplierOrder.commission_amount), 0)).where(
            SupplierOrder.supplier_id == supplier_id
        )
    ) or 0
    products = db.scalar(
        select(func.count(Product.id)).where(Product.supplier_id == supplier_id)
    ) or 0
    return {
        "by_status": {row[0]: {"orders": row[1], "value": int(row[2])} for row in rows},
        "commission": int(commission),
        "products": products,
    }


def supplier_directory(db: Session) -> list[dict]:
    suppliers = db.scalars(select(Supplier).order_by(Supplier.trading_name)).all()
    result = []
    for supplier in suppliers:
        count = db.scalar(
            select(func.count(Product.id)).where(Product.supplier_id == supplier.id)
        ) or 0
        result.append(
            {
                "id": supplier.id,
                "code": supplier.code,
                "name": supplier.trading_name,
                "legal_name": supplier.legal_name,
                "status": supplier.status,
                "region": supplier.region,
                "products": count,
                "rating": supplier.rating_x10 / 10,
            }
        )
    return result
