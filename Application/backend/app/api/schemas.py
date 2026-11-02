from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=160)
    phone: str | None = None
    locale: Literal["sw", "en"] = "sw"
    consent_marketing: bool = False


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class AddressIn(BaseModel):
    label: str = "Home"
    recipient_name: str
    phone: str
    region: str
    district: str
    ward: str | None = None
    street: str
    landmark: str | None = None
    is_default: bool = False


class CartAddIn(BaseModel):
    variant_id: str
    qty: int = Field(default=1, ge=1, le=20)


class CartUpdateIn(BaseModel):
    qty: int = Field(ge=0, le=20)


class CheckoutIn(BaseModel):
    address_id: str | None = None
    recipient_name: str | None = None
    phone: str | None = None
    region: str | None = None
    district: str | None = None
    ward: str | None = None
    street: str | None = None
    landmark: str | None = None
    label: str | None = None
    notes: str | None = None


class PayIn(BaseModel):
    method: Literal["mobile_money", "card", "bank"] = "mobile_money"
    msisdn: str | None = None


class SimulateIn(BaseModel):
    outcome: Literal["succeeded", "failed"]


class AcceptIn(BaseModel):
    accepted_item_ids: list[str] | None = None
    rejection_reason: str = "Item is out of stock"


class RejectIn(BaseModel):
    reason: str = "Items are not available"


class ShipIn(BaseModel):
    carrier: str | None = None
    tracking_number: str | None = None
    fee: int | None = Field(default=None, ge=0)


class DeliverIn(BaseModel):
    pod_ref: str | None = None
    note: str | None = None


class ShipmentTrackingIn(BaseModel):
    status: Literal[
        "picked_up",
        "in_transit",
        "out_for_delivery",
        "delayed",
        "delivery_attempted",
        "returned_to_sender",
    ]
    note: str | None = Field(default=None, max_length=500)


class ReturnCreateIn(BaseModel):
    item_id: str
    qty: int = Field(ge=1, le=20)
    reason: str
    details: str | None = None


class ReturnDecisionIn(BaseModel):
    approve: bool
    note: str | None = None


class PayoutRequestIn(BaseModel):
    supplier_id: str
    notes: str | None = None


class PayoutDecisionIn(BaseModel):
    note: str | None = None
    reason: str | None = None


class ConfigUpdateIn(BaseModel):
    values: dict[str, Any]


class TicketCreateIn(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    category: Literal["order", "delivery", "payment", "return", "product", "general"] = "general"
    order_id: str | None = None
    message: str = Field(min_length=3)


class TicketReplyIn(BaseModel):
    body: str = Field(min_length=1)
    internal: bool = False


class TicketUpdateIn(BaseModel):
    status: Literal["open", "in_progress", "resolved", "closed"] | None = None
    priority: Literal["low", "normal", "high", "urgent"] | None = None
    assigned_to: str | None = None


class VariantIn(BaseModel):
    name: str = "Default"
    sku: str | None = None
    price: int = Field(ge=1000)
    on_hand: int = Field(default=0, ge=0)
    weight_g: int = Field(default=500, ge=50)


class ProductIn(BaseModel):
    name: str = Field(min_length=3, max_length=200)
    description: str = ""
    brand: str | None = None
    department_id: str
    category_id: str | None = None
    supplier_id: str | None = None
    variants: list[VariantIn] = Field(min_length=1)


class StockUpdateIn(BaseModel):
    on_hand: int | None = Field(default=None, ge=0)
    price: int | None = Field(default=None, ge=1000)
    active: bool | None = None


class SupplierCommissionIn(BaseModel):
    commission_bp: int | None = Field(default=None, ge=0, le=3000)
    status: Literal["pending_verification", "verified", "suspended", "rejected"] | None = None
    note: str | None = None


class AssistantMessageIn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class AssistantChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: list[AssistantMessageIn] = Field(default_factory=list, max_length=8)
    audience: Literal["customer", "ops"] = "customer"


class ChatMessageIn(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class ChatHandoffIn(BaseModel):
    note: str | None = Field(default=None, max_length=500)


class ChatAssignIn(BaseModel):
    party: Literal["supplier", "logistics"]
    note: str | None = Field(default=None, max_length=500)
