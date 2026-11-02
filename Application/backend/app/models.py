from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import ClassVar

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def new_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class IdMixin:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)


# ---------------------------------------------------------------- accounts


class Role:
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    OPS_ADMIN = "ops_admin"
    OPS_FINANCE = "ops_finance"
    OPS_SUPPORT = "ops_support"
    SUPERADMIN = "superadmin"

    ALL: ClassVar[set[str]] = {
        CUSTOMER,
        SUPPLIER,
        OPS_ADMIN,
        OPS_FINANCE,
        OPS_SUPPORT,
        SUPERADMIN,
    }
    STAFF: ClassVar[set[str]] = {OPS_ADMIN, OPS_FINANCE, OPS_SUPPORT, SUPERADMIN}
    LOGISTICS_DESK: ClassVar[set[str]] = {OPS_ADMIN, OPS_SUPPORT, SUPERADMIN}


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(24), default=Role.CUSTOMER, index=True)
    status: Mapped[str] = mapped_column(String(24), default="active")
    locale: Mapped[str] = mapped_column(String(8), default="sw")
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    supplier_id: Mapped[str | None] = mapped_column(ForeignKey("suppliers.id"), index=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    addresses: Mapped[list[Address]] = relationship(back_populates="user")


class Consent(IdMixin, Base):
    __tablename__ = "consents"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    purpose: Mapped[str] = mapped_column(String(64))
    granted: Mapped[bool] = mapped_column(Boolean)
    policy_version: Mapped[str] = mapped_column(String(16), default="2026-10")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Address(IdMixin, TimestampMixin, Base):
    __tablename__ = "addresses"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    label: Mapped[str] = mapped_column(String(64), default="Home")
    recipient_name: Mapped[str] = mapped_column(String(160))
    phone: Mapped[str] = mapped_column(String(32))
    region: Mapped[str] = mapped_column(String(64))
    district: Mapped[str] = mapped_column(String(64))
    ward: Mapped[str | None] = mapped_column(String(64))
    street: Mapped[str] = mapped_column(String(255))
    landmark: Mapped[str | None] = mapped_column(String(255))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship(back_populates="addresses")


# ---------------------------------------------------------------- supply


class SupplierStatus:
    PENDING = "pending_verification"
    VERIFIED = "verified"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


class Supplier(IdMixin, TimestampMixin, Base):
    __tablename__ = "suppliers"

    code: Mapped[str] = mapped_column(String(24), unique=True)
    legal_name: Mapped[str] = mapped_column(String(200))
    trading_name: Mapped[str] = mapped_column(String(200))
    tin: Mapped[str | None] = mapped_column(String(32))
    brela_number: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default=SupplierStatus.PENDING, index=True)
    commission_bp: Mapped[int | None] = mapped_column(Integer)
    payout_method: Mapped[str] = mapped_column(String(32), default="mobile_money")
    payout_account_name: Mapped[str | None] = mapped_column(String(160))
    payout_account_number: Mapped[str | None] = mapped_column(String(64))
    payout_provider: Mapped[str | None] = mapped_column(String(64))
    region: Mapped[str] = mapped_column(String(64), default="Dar es Salaam")
    city: Mapped[str] = mapped_column(String(64), default="Dar es Salaam")
    contact_name: Mapped[str | None] = mapped_column(String(160))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(32))
    rating_x10: Mapped[int] = mapped_column(Integer, default=0)  # 48 means 4.8 / 5
    kyc_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    documents: Mapped[list[SupplierDocument]] = relationship(back_populates="supplier")
    products: Mapped[list[Product]] = relationship(back_populates="supplier")


class SupplierDocument(IdMixin, Base):
    __tablename__ = "supplier_documents"

    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    doc_type: Mapped[str] = mapped_column(String(40))
    file_ref: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(24), default="pending")
    reviewed_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    supplier: Mapped[Supplier] = relationship(back_populates="documents")


# ---------------------------------------------------------------- catalogue


class Department(IdMixin, Base):
    __tablename__ = "departments"

    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    name_sw: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Category(IdMixin, Base):
    __tablename__ = "categories"

    department_id: Mapped[str] = mapped_column(ForeignKey("departments.id"), index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    name_sw: Mapped[str] = mapped_column(String(120))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class ProductStatus:
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class Product(IdMixin, TimestampMixin, Base):
    __tablename__ = "products"

    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.id"), index=True)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"), index=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    brand: Mapped[str | None] = mapped_column(String(120))
    origin: Mapped[str | None] = mapped_column(String(120), default="Tanzania")
    status: Mapped[str] = mapped_column(String(24), default=ProductStatus.DRAFT, index=True)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)

    supplier: Mapped[Supplier] = relationship(back_populates="products")
    variants: Mapped[list[ProductVariant]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    images: Mapped[list[ProductImage]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class ProductVariant(IdMixin, TimestampMixin, Base):
    __tablename__ = "product_variants"

    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(160), default="Default")
    price_tzs: Mapped[int] = mapped_column(BigInteger)
    on_hand: Mapped[int] = mapped_column(Integer, default=0)
    reserved: Mapped[int] = mapped_column(Integer, default=0)
    weight_g: Mapped[int] = mapped_column(Integer, default=500)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    product: Mapped[Product] = relationship(back_populates="variants")

    @property
    def available(self) -> int:
        return max(self.on_hand - self.reserved, 0)


class ProductImage(IdMixin, Base):
    __tablename__ = "product_images"

    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    url: Mapped[str] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped[Product] = relationship(back_populates="images")


# ---------------------------------------------------------------- cart


class Cart(IdMixin, TimestampMixin, Base):
    __tablename__ = "carts"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    items: Mapped[list[CartItem]] = relationship(
        back_populates="cart", cascade="all, delete-orphan"
    )


class CartItem(IdMixin, Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "variant_id", name="uq_cart_variant"),)

    cart_id: Mapped[str] = mapped_column(ForeignKey("carts.id"), index=True)
    variant_id: Mapped[str] = mapped_column(ForeignKey("product_variants.id"), index=True)
    qty: Mapped[int] = mapped_column(Integer, default=1)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    cart: Mapped[Cart] = relationship(back_populates="items")
    variant: Mapped[ProductVariant] = relationship()


class Reservation(IdMixin, Base):
    __tablename__ = "reservations"

    variant_id: Mapped[str] = mapped_column(ForeignKey("product_variants.id"), index=True)
    order_id: Mapped[str | None] = mapped_column(ForeignKey("orders.id"), index=True)
    qty: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="held", index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# ---------------------------------------------------------------- orders


class OrderStatus:
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    FULFILLING = "fulfilling"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus:
    UNPAID = "unpaid"
    PAID = "paid"
    PARTIALLY_REFUNDED = "partially_refunded"
    REFUNDED = "refunded"


class SupplierOrderStatus:
    AWAITING_ACCEPTANCE = "awaiting_acceptance"
    ACCEPTED = "accepted"
    READY = "ready"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ItemStatus:
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    RETURNED = "returned"


class Order(IdMixin, TimestampMixin, Base):
    __tablename__ = "orders"

    code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(24), default=OrderStatus.PENDING_PAYMENT, index=True)
    payment_status: Mapped[str] = mapped_column(String(24), default=PaymentStatus.UNPAID, index=True)
    currency: Mapped[str] = mapped_column(String(3), default="TZS")
    subtotal: Mapped[int] = mapped_column(BigInteger, default=0)
    delivery_total: Mapped[int] = mapped_column(BigInteger, default=0)
    total: Mapped[int] = mapped_column(BigInteger, default=0)
    refunded_total: Mapped[int] = mapped_column(BigInteger, default=0)
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    ship_recipient: Mapped[str] = mapped_column(String(160))
    ship_phone: Mapped[str] = mapped_column(String(32))
    ship_region: Mapped[str] = mapped_column(String(64))
    ship_district: Mapped[str] = mapped_column(String(64))
    ship_ward: Mapped[str | None] = mapped_column(String(64))
    ship_street: Mapped[str] = mapped_column(String(255))
    ship_landmark: Mapped[str | None] = mapped_column(String(255))

    customer: Mapped[User] = relationship()
    items: Mapped[list[OrderItem]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    supplier_orders: Mapped[list[SupplierOrder]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class SupplierOrder(IdMixin, TimestampMixin, Base):
    __tablename__ = "supplier_orders"

    code: Mapped[str] = mapped_column(String(28), unique=True, index=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    status: Mapped[str] = mapped_column(
        String(28), default=SupplierOrderStatus.AWAITING_ACCEPTANCE, index=True
    )
    merchandise_total: Mapped[int] = mapped_column(BigInteger, default=0)
    delivery_fee: Mapped[int] = mapped_column(BigInteger, default=0)
    commission_bp: Mapped[int] = mapped_column(Integer, default=800)
    commission_amount: Mapped[int] = mapped_column(BigInteger, default=0)
    supplier_payable: Mapped[int] = mapped_column(BigInteger, default=0)
    refunded_merchandise: Mapped[int] = mapped_column(BigInteger, default=0)
    refunded_delivery: Mapped[int] = mapped_column(BigInteger, default=0)
    refunded_commission: Mapped[int] = mapped_column(BigInteger, default=0)
    payout_status: Mapped[str] = mapped_column(String(20), default="unpaid", index=True)
    payout_id: Mapped[str | None] = mapped_column(ForeignKey("payouts.id"), index=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    eligible_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    order: Mapped[Order] = relationship(back_populates="supplier_orders")
    supplier: Mapped[Supplier] = relationship()
    items: Mapped[list[OrderItem]] = relationship(back_populates="supplier_order")
    shipments: Mapped[list[Shipment]] = relationship(back_populates="supplier_order")


class OrderItem(IdMixin, Base):
    __tablename__ = "order_items"

    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    supplier_order_id: Mapped[str] = mapped_column(ForeignKey("supplier_orders.id"), index=True)
    variant_id: Mapped[str] = mapped_column(ForeignKey("product_variants.id"), index=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    product_name: Mapped[str] = mapped_column(String(200))
    variant_name: Mapped[str] = mapped_column(String(160))
    sku: Mapped[str] = mapped_column(String(64))
    unit_price: Mapped[int] = mapped_column(BigInteger)
    qty: Mapped[int] = mapped_column(Integer)
    line_total: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(20), default=ItemStatus.PENDING, index=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    refunded_qty: Mapped[int] = mapped_column(Integer, default=0)

    order: Mapped[Order] = relationship(back_populates="items")
    supplier_order: Mapped[SupplierOrder] = relationship(back_populates="items")
    variant: Mapped[ProductVariant] = relationship()

    @property
    def refunded_amount(self) -> int:
        return self.unit_price * self.refunded_qty


# ---------------------------------------------------------------- logistics


class Shipment(IdMixin, TimestampMixin, Base):
    __tablename__ = "shipments"

    supplier_order_id: Mapped[str] = mapped_column(ForeignKey("supplier_orders.id"), index=True)
    carrier: Mapped[str] = mapped_column(String(80))
    carrier_mode: Mapped[str] = mapped_column(String(16), default="manual")
    tracking_number: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    fee: Mapped[int] = mapped_column(BigInteger, default=0)
    booked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    picked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pod_ref: Mapped[str | None] = mapped_column(String(120))
    failure_reason: Mapped[str | None] = mapped_column(Text)

    supplier_order: Mapped[SupplierOrder] = relationship(back_populates="shipments")
    events: Mapped[list[ShipmentEvent]] = relationship(
        back_populates="shipment", order_by="ShipmentEvent.occurred_at"
    )


class ShipmentEvent(IdMixin, Base):
    __tablename__ = "shipment_events"

    shipment_id: Mapped[str] = mapped_column(ForeignKey("shipments.id"), index=True)
    status: Mapped[str] = mapped_column(String(24))
    note: Mapped[str | None] = mapped_column(Text)
    actor: Mapped[str] = mapped_column(String(120), default="system")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    shipment: Mapped[Shipment] = relationship(back_populates="events")


# ---------------------------------------------------------------- money


class Payment(IdMixin, Base):
    __tablename__ = "payments"

    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    provider: Mapped[str] = mapped_column(String(40), default="mock")
    provider_ref: Mapped[str | None] = mapped_column(String(120), index=True)
    amount: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[str] = mapped_column(String(3), default="TZS")
    method: Mapped[str] = mapped_column(String(24), default="mobile_money")
    msisdn: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(20), default="initiated", index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(120), index=True)
    initiated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[str | None] = mapped_column(Text)
    raw: Mapped[dict] = mapped_column(JSON, default=dict)


class RefundStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Refund(IdMixin, Base):
    __tablename__ = "refunds"

    payment_id: Mapped[str] = mapped_column(ForeignKey("payments.id"), index=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    supplier_order_id: Mapped[str | None] = mapped_column(
        ForeignKey("supplier_orders.id"), index=True
    )
    return_id: Mapped[str | None] = mapped_column(ForeignKey("returns.id"), index=True)
    amount: Mapped[int] = mapped_column(BigInteger)
    merchandise_amount: Mapped[int] = mapped_column(BigInteger, default=0)
    delivery_amount: Mapped[int] = mapped_column(BigInteger, default=0)
    commission_reversal: Mapped[int] = mapped_column(BigInteger, default=0)
    status: Mapped[str] = mapped_column(String(20), default=RefundStatus.PENDING, index=True)
    provider_ref: Mapped[str | None] = mapped_column(String(120))
    reason: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[str | None] = mapped_column(Text)


class LedgerAccount(IdMixin, Base):
    __tablename__ = "ledger_accounts"

    code: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(20))  # asset | liability | revenue | expense | equity


class LedgerTransaction(IdMixin, Base):
    __tablename__ = "ledger_transactions"

    kind: Mapped[str] = mapped_column(String(40), index=True)
    reference: Mapped[str] = mapped_column(String(80), index=True)
    memo: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LedgerEntry(IdMixin, Base):
    __tablename__ = "ledger_entries"

    transaction_id: Mapped[str] = mapped_column(ForeignKey("ledger_transactions.id"), index=True)
    account_code: Mapped[str] = mapped_column(ForeignKey("ledger_accounts.code"), index=True)
    debit: Mapped[int] = mapped_column(BigInteger, default=0)
    credit: Mapped[int] = mapped_column(BigInteger, default=0)


Index("ix_ledger_account_tx", LedgerEntry.transaction_id, LedgerEntry.account_code)


class Payout(IdMixin, TimestampMixin, Base):
    __tablename__ = "payouts"

    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    amount: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(24), default="pending_approval", index=True)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    requested_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    approved_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provider_ref: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    rejection_reason: Mapped[str | None] = mapped_column(Text)


# ---------------------------------------------------------------- service


class ReturnStatus:
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    RECEIVED = "received"
    REFUNDED = "refunded"
    CLOSED = "closed"


class Return(IdMixin, TimestampMixin, Base):
    __tablename__ = "returns"

    code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    supplier_order_id: Mapped[str] = mapped_column(ForeignKey("supplier_orders.id"), index=True)
    item_id: Mapped[str] = mapped_column(ForeignKey("order_items.id"), index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    qty: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(60))
    details: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default=ReturnStatus.REQUESTED, index=True)
    decision_note: Mapped[str | None] = mapped_column(Text)
    decided_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    refund_id: Mapped[str | None] = mapped_column(String(36))
    refund_amount: Mapped[int] = mapped_column(BigInteger, default=0)


class Ticket(IdMixin, TimestampMixin, Base):
    __tablename__ = "tickets"

    code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    order_id: Mapped[str | None] = mapped_column(ForeignKey("orders.id"), index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    subject: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(40), default="general")
    priority: Mapped[str] = mapped_column(String(16), default="normal")
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)
    assigned_to: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TicketMessage(IdMixin, Base):
    __tablename__ = "ticket_messages"

    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.id"), index=True)
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    internal: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# ---------------------------------------------------------------- chat


class ChatParty:
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    LOGISTICS = "logistics"
    SYSTEM = "system"


class ChatMessageKind:
    TEXT = "text"
    SYSTEM = "system"
    HANDOFF = "handoff"


class Conversation(IdMixin, TimestampMixin, Base):
    """One shared thread per supplier order.

    The customer and supplier talk from checkout; the ops logistics desk reads
    every thread and becomes the assigned party after the supplier hands over.
    """

    __tablename__ = "conversations"

    code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    supplier_order_id: Mapped[str] = mapped_column(
        ForeignKey("supplier_orders.id"), unique=True, index=True
    )
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    assigned_party: Mapped[str] = mapped_column(String(16), default=ChatParty.SUPPLIER)
    handoff_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    handoff_note: Mapped[str | None] = mapped_column(Text)
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    supplier_order: Mapped[SupplierOrder] = relationship()
    supplier: Mapped[Supplier] = relationship()
    customer: Mapped[User] = relationship(foreign_keys=[customer_id])
    messages: Mapped[list[ChatMessage]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(IdMixin, Base):
    __tablename__ = "chat_messages"

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id"), index=True
    )
    author_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    author_party: Mapped[str] = mapped_column(String(16))
    body: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(16), default=ChatMessageKind.TEXT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
    author: Mapped[User | None] = relationship()


# ---------------------------------------------------------------- platform


class AuditLog(IdMixin, Base):
    __tablename__ = "audit_logs"

    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    actor_role: Mapped[str | None] = mapped_column(String(24))
    action: Mapped[str] = mapped_column(String(80), index=True)
    entity_type: Mapped[str] = mapped_column(String(60), index=True)
    entity_id: Mapped[str | None] = mapped_column(String(64), index=True)
    before: Mapped[dict | None] = mapped_column(JSON)
    after: Mapped[dict | None] = mapped_column(JSON)
    ip: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PlatformConfig(Base):
    __tablename__ = "platform_config"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class Notification(IdMixin, Base):
    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    channel: Mapped[str] = mapped_column(String(16), default="in_app")
    template: Mapped[str] = mapped_column(String(60))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(16), default="queued")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class IdempotencyRecord(IdMixin, Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (UniqueConstraint("scope", "key", name="uq_idempotency_scope_key"),)

    scope: Mapped[str] = mapped_column(String(80))
    key: Mapped[str] = mapped_column(String(120))
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    request_hash: Mapped[str] = mapped_column(String(64))
    status_code: Mapped[int] = mapped_column(Integer)
    response: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
