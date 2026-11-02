from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ..models import (
    Address,
    ChatMessage,
    ChatParty,
    Conversation,
    Department,
    Notification,
    Order,
    OrderItem,
    Payout,
    Product,
    ProductVariant,
    Refund,
    Return,
    Shipment,
    Supplier,
    SupplierOrder,
    Ticket,
    TicketMessage,
    User,
)
from ..services import chat as chat_service
from ..services.refunds import remaining_supplier_payable


def iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.isoformat()


def user_out(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "full_name": user.full_name,
        "role": user.role,
        "locale": user.locale,
        "supplier_id": user.supplier_id,
        "email_verified": user.email_verified,
    }


def address_out(address: Address) -> dict[str, Any]:
    return {
        "id": address.id,
        "label": address.label,
        "recipient_name": address.recipient_name,
        "phone": address.phone,
        "region": address.region,
        "district": address.district,
        "ward": address.ward,
        "street": address.street,
        "landmark": address.landmark,
        "is_default": address.is_default,
    }


def department_out(department: Department, categories: list) -> dict[str, Any]:
    return {
        "id": department.id,
        "slug": department.slug,
        "name": department.name,
        "name_sw": department.name_sw,
        "description": department.description,
        "categories": [
            {"id": category.id, "slug": category.slug, "name": category.name, "name_sw": category.name_sw}
            for category in categories
        ],
    }


def variant_out(variant: ProductVariant) -> dict[str, Any]:
    return {
        "id": variant.id,
        "sku": variant.sku,
        "name": variant.name,
        "price": variant.price_tzs,
        "available": variant.available,
        "weight_g": variant.weight_g,
    }


def variant_stock_out(variant: ProductVariant) -> dict[str, Any]:
    return {
        "id": variant.id,
        "sku": variant.sku,
        "name": variant.name,
        "price": variant.price_tzs,
        "on_hand": variant.on_hand,
        "reserved": variant.reserved,
        "available": variant.available,
        "active": variant.active,
        "weight_g": variant.weight_g,
    }


def product_summary(product: Product) -> dict[str, Any]:
    variants = [v for v in product.variants if v.active]
    prices = [v.price_tzs for v in variants] or [0]
    return {
        "id": product.id,
        "slug": product.slug,
        "name": product.name,
        "brand": product.brand,
        "department": product.department_id,
        "department_slug": getattr(product, "department_slug", None),
        "department_name": getattr(product, "department_name", None),
        "supplier": product.supplier.trading_name,
        "supplier_id": product.supplier_id,
        "price_from": min(prices),
        "price_to": max(prices),
        "variant_count": len(variants),
        "in_stock": any(v.available > 0 for v in variants),
        "origin": product.origin,
    }


def product_detail(product: Product) -> dict[str, Any]:
    data = product_summary(product)
    data.update(
        {
            "description": product.description,
            "attributes": product.attributes,
            "variants": [variant_out(v) for v in product.variants if v.active],
            "supplier_region": product.supplier.region,
            "supplier_rating": product.supplier.rating_x10 / 10,
        }
    )
    return data


def supplier_product_out(product: Product) -> dict[str, Any]:
    data = product_summary(product)
    data.update(
        {
            "description": product.description,
            "attributes": product.attributes,
            "variants": [variant_stock_out(v) for v in product.variants],
            "status": product.status,
            "supplier_region": product.supplier.region,
            "supplier_rating": product.supplier.rating_x10 / 10,
            "created_at": iso(product.created_at),
        }
    )
    return data


def supplier_out(supplier: Supplier) -> dict[str, Any]:
    return {
        "id": supplier.id,
        "code": supplier.code,
        "legal_name": supplier.legal_name,
        "trading_name": supplier.trading_name,
        "status": supplier.status,
        "region": supplier.region,
        "city": supplier.city,
        "rating": supplier.rating_x10 / 10,
        "commission_bp": supplier.commission_bp,
        "payout_method": supplier.payout_method,
        "payout_provider": supplier.payout_provider,
        "contact_name": supplier.contact_name,
        "contact_email": supplier.contact_email,
        "contact_phone": supplier.contact_phone,
    }


def item_out(item: OrderItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "supplier_order_id": item.supplier_order_id,
        "variant_id": item.variant_id,
        "product_name": item.product_name,
        "variant_name": item.variant_name,
        "sku": item.sku,
        "unit_price": item.unit_price,
        "qty": item.qty,
        "line_total": item.line_total,
        "status": item.status,
        "rejection_reason": item.rejection_reason,
        "refunded_qty": item.refunded_qty,
        "returnable": item.status == "delivered" and item.qty > item.refunded_qty,
    }


def _tracking_actor(actor: str) -> str:
    if actor.startswith("ops:"):
        return "operations"
    if actor in {"carrier", "system"}:
        return actor
    return "supplier"


def shipment_out(shipment: Shipment) -> dict[str, Any]:
    return {
        "id": shipment.id,
        "supplier_order_id": shipment.supplier_order_id,
        "carrier": shipment.carrier,
        "mode": shipment.carrier_mode,
        "tracking_number": shipment.tracking_number,
        "status": shipment.status,
        "fee": shipment.fee,
        "booked_at": iso(shipment.booked_at),
        "delivered_at": iso(shipment.delivered_at),
        "pod_ref": shipment.pod_ref,
        "events": [
            {
                "id": event.id,
                "status": event.status,
                "note": event.note,
                "actor": _tracking_actor(event.actor),
                "occurred_at": iso(event.occurred_at),
            }
            for event in shipment.events
        ],
    }


def supplier_order_out(so: SupplierOrder, *, include_supplier: bool = True) -> dict[str, Any]:
    data = {
        "id": so.id,
        "code": so.code,
        "order_id": so.order_id,
        "supplier_id": so.supplier_id,
        "status": so.status,
        "merchandise_total": so.merchandise_total,
        "delivery_fee": so.delivery_fee,
        "commission_bp": so.commission_bp,
        "commission_amount": so.commission_amount,
        "supplier_payable": so.supplier_payable,
        "remaining_payable": remaining_supplier_payable(so),
        "refunded_merchandise": so.refunded_merchandise,
        "refunded_delivery": so.refunded_delivery,
        "payout_status": so.payout_status,
        "accepted_at": iso(so.accepted_at),
        "delivered_at": iso(so.delivered_at),
        "eligible_at": iso(so.eligible_at),
        "rejection_reason": so.rejection_reason,
        "items": [item_out(item) for item in so.items],
        "shipments": [shipment_out(shipment) for shipment in so.shipments],
    }
    if include_supplier and so.supplier is not None:
        data["supplier"] = {
            "id": so.supplier.id,
            "name": so.supplier.trading_name,
            "region": so.supplier.region,
            "phone": so.supplier.contact_phone,
        }
    return data


def order_stage(order: Order) -> str:
    if order.status == "pending_payment":
        return "awaiting_payment"
    if order.status == "cancelled":
        return "cancelled"
    if order.status == "completed":
        return "completed"
    statuses = {so.status for so in order.supplier_orders}
    if "awaiting_acceptance" in statuses:
        return "awaiting_supplier"
    if statuses & {"accepted", "ready"}:
        return "preparing"
    if "in_transit" in statuses:
        return "in_transit"
    if statuses and statuses <= {"delivered", "completed"}:
        return "delivered"
    return "fulfilling"


def order_out(order: Order, *, detail: bool = False) -> dict[str, Any]:
    data = {
        "id": order.id,
        "code": order.code,
        "customer_id": order.customer_id,
        "customer_name": order.customer.full_name if order.customer else None,
        "status": order.status,
        "stage": order_stage(order),
        "payment_status": order.payment_status,
        "currency": order.currency,
        "subtotal": order.subtotal,
        "delivery_total": order.delivery_total,
        "total": order.total,
        "refunded_total": order.refunded_total,
        "placed_at": iso(order.placed_at),
        "paid_at": iso(order.paid_at),
        "completed_at": iso(order.completed_at),
        "cancelled_at": iso(order.cancelled_at),
        "cancellation_reason": order.cancellation_reason,
        "notes": order.notes,
        "delivery_address": {
            "recipient_name": order.ship_recipient,
            "phone": order.ship_phone,
            "region": order.ship_region,
            "district": order.ship_district,
            "ward": order.ship_ward,
            "street": order.ship_street,
            "landmark": order.ship_landmark,
        },
        "supplier_orders": [supplier_order_out(so) for so in order.supplier_orders],
        "item_count": sum(item.qty for item in order.items),
    }
    if detail:
        data["items"] = [item_out(item) for item in order.items]
    return data


def payment_out(payment) -> dict[str, Any]:
    return {
        "id": payment.id,
        "order_id": payment.order_id,
        "provider": payment.provider,
        "provider_ref": payment.provider_ref,
        "amount": payment.amount,
        "currency": payment.currency,
        "method": payment.method,
        "msisdn": payment.msisdn,
        "status": payment.status,
        "initiated_at": iso(payment.initiated_at),
        "completed_at": iso(payment.completed_at),
        "failure_reason": payment.failure_reason,
    }


def refund_out(refund: Refund) -> dict[str, Any]:
    return {
        "id": refund.id,
        "order_id": refund.order_id,
        "supplier_order_id": refund.supplier_order_id,
        "amount": refund.amount,
        "merchandise_amount": refund.merchandise_amount,
        "delivery_amount": refund.delivery_amount,
        "commission_reversal": refund.commission_reversal,
        "status": refund.status,
        "reason": refund.reason,
        "created_at": iso(refund.created_at),
        "completed_at": iso(refund.completed_at),
    }


def supplier_order_with_order(so: SupplierOrder) -> dict[str, Any]:
    data = supplier_order_out(so)
    order = so.order
    if order is not None:
        data["order"] = {
            "id": order.id,
            "code": order.code,
            "status": order.status,
            "payment_status": order.payment_status,
            "placed_at": iso(order.placed_at),
            "customer_name": order.customer.full_name if order.customer else None,
            "delivery_address": {
                "recipient_name": order.ship_recipient,
                "phone": order.ship_phone,
                "region": order.ship_region,
                "district": order.ship_district,
                "ward": order.ship_ward,
                "street": order.ship_street,
                "landmark": order.ship_landmark,
            },
        }
    return data


def payout_out(payout: Payout, orders: list[SupplierOrder] | None = None) -> dict[str, Any]:
    data = {
        "id": payout.id,
        "supplier_id": payout.supplier_id,
        "amount": payout.amount,
        "status": payout.status,
        "period_start": iso(payout.period_start),
        "period_end": iso(payout.period_end),
        "requested_by": payout.requested_by,
        "approved_by": payout.approved_by,
        "approved_at": iso(payout.approved_at),
        "paid_at": iso(payout.paid_at),
        "provider_ref": payout.provider_ref,
        "notes": payout.notes,
        "rejection_reason": payout.rejection_reason,
        "created_at": iso(payout.created_at),
    }
    if orders is not None:
        data["orders"] = [
            {"id": so.id, "code": so.code, "payable": remaining_supplier_payable(so)}
            for so in orders
        ]
    return data


def return_out(ret: Return, *, item: OrderItem | None = None) -> dict[str, Any]:
    data = {
        "id": ret.id,
        "code": ret.code,
        "order_id": ret.order_id,
        "supplier_order_id": ret.supplier_order_id,
        "item_id": ret.item_id,
        "qty": ret.qty,
        "reason": ret.reason,
        "details": ret.details,
        "status": ret.status,
        "decision_note": ret.decision_note,
        "refund_amount": ret.refund_amount,
        "requested_at": iso(ret.created_at),
        "decided_at": iso(ret.decided_at),
        "received_at": iso(ret.received_at),
        "refund_id": ret.refund_id,
    }
    if item is not None:
        data["item"] = {
            "product_name": item.product_name,
            "variant_name": item.variant_name,
            "unit_price": item.unit_price,
        }
    return data


def ticket_out(ticket: Ticket, messages: list[TicketMessage] | None = None) -> dict[str, Any]:
    data = {
        "id": ticket.id,
        "code": ticket.code,
        "order_id": ticket.order_id,
        "customer_id": ticket.customer_id,
        "subject": ticket.subject,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "assigned_to": ticket.assigned_to,
        "created_at": iso(ticket.created_at),
        "closed_at": iso(ticket.closed_at),
    }
    if messages is not None:
        data["messages"] = [
            {
                "id": message.id,
                "author_id": message.author_id,
                "body": message.body,
                "internal": message.internal,
                "created_at": iso(message.created_at),
            }
            for message in messages
        ]
    return data


def notification_out(notification: Notification) -> dict[str, Any]:
    return {
        "id": notification.id,
        "channel": notification.channel,
        "template": notification.template,
        "payload": notification.payload,
        "status": notification.status,
        "created_at": iso(notification.created_at),
        "read_at": iso(notification.read_at),
    }


def chat_message_out(message: ChatMessage) -> dict[str, Any]:
    if message.author_party == ChatParty.SYSTEM:
        author_name = "Usiri"
    elif message.author is not None:
        author_name = message.author.full_name
    else:
        author_name = "Usiri"
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "author_id": message.author_id,
        "author_name": author_name,
        "author_party": message.author_party,
        "body": message.body,
        "kind": message.kind,
        "created_at": iso(message.created_at),
    }


def conversation_out(
    conversation: Conversation, *, viewer: User, detail: bool = False
) -> dict[str, Any]:
    supplier_order = conversation.supplier_order
    order = supplier_order.order if supplier_order else None
    supplier = supplier_order.supplier if supplier_order else conversation.supplier
    shipment = chat_service.shipment_for(conversation)
    viewer_party = chat_service.party_for(conversation, viewer)
    messages = list(conversation.messages)
    last = messages[-1] if messages else None

    if conversation.assigned_party == ChatParty.LOGISTICS:
        assigned_name = "Usiri logistics desk"
    elif supplier is not None:
        assigned_name = supplier.trading_name
    else:
        assigned_name = "Supplier"

    data = {
        "id": conversation.id,
        "code": conversation.code,
        "order_id": conversation.order_id,
        "order_code": order.code if order else None,
        "supplier_order_id": conversation.supplier_order_id,
        "supplier_order_code": supplier_order.code if supplier_order else None,
        "supplier_id": conversation.supplier_id,
        "supplier_name": supplier.trading_name if supplier else "Supplier",
        "customer_id": conversation.customer_id,
        "customer_name": conversation.customer.full_name if conversation.customer else "Customer",
        "assigned_party": conversation.assigned_party,
        "assigned_name": assigned_name,
        "handoff_at": iso(conversation.handoff_at),
        "handoff_note": conversation.handoff_note,
        "last_message_at": iso(conversation.last_message_at),
        "created_at": iso(conversation.created_at),
        "shipment": (
            {
                "carrier": shipment.carrier,
                "tracking_number": shipment.tracking_number,
                "status": shipment.status,
            }
            if shipment
            else None
        ),
        "can_reply": viewer_party in {ChatParty.CUSTOMER, ChatParty.SUPPLIER}
        or (viewer_party == ChatParty.LOGISTICS and conversation.assigned_party == ChatParty.LOGISTICS),
        "can_handoff": viewer_party == ChatParty.SUPPLIER
        and chat_service.can_handoff(conversation),
        "can_take_over": viewer_party == ChatParty.LOGISTICS
        and conversation.assigned_party == ChatParty.SUPPLIER,
        "can_return": viewer_party == ChatParty.LOGISTICS
        and conversation.assigned_party == ChatParty.LOGISTICS,
        "last_message": chat_message_out(last) if last else None,
    }
    if detail:
        data["messages"] = [chat_message_out(message) for message in messages]
    return data
