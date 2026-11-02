from __future__ import annotations

import json

from app.adapters.psp import get_provider
from app.security import new_webhook_signature

from .conftest import (
    auth,
    place_order,
    supplier_headers,
    supplier_order_for,
    variant_of,
)


def test_authentication_is_required(client):
    assert client.get("/api/cart").status_code == 401
    assert client.get("/api/orders").status_code == 401
    assert client.post("/api/checkout", json={}).status_code == 401


def test_customer_cannot_reach_operations(client, customer):
    assert client.get("/api/ops/dashboard", headers=customer).status_code == 403
    assert client.get("/api/ops/ledger", headers=customer).status_code == 403
    assert client.get("/api/supplier/orders", headers=customer).status_code == 403


def test_support_cannot_pay_suppliers(client, support):
    assert client.get("/api/ops/payouts", headers=support).status_code == 403
    assert client.get("/api/ops/ledger", headers=support).status_code == 403
    assert client.get("/api/ops/dashboard", headers=support).status_code == 200


def test_staff_cannot_shop(client, admin):
    kettle, _ = variant_of(client, "electric-kettle-1.8l")
    response = client.post("/api/cart/items", headers=admin, json={"variant_id": kettle, "qty": 1})
    assert response.status_code == 403


def test_supplier_is_scoped_to_own_orders(client, customer):
    kettle, _ = variant_of(client, "electric-kettle-1.8l")
    order = place_order(client, customer, [(kettle, 1)])
    mwanga = supplier_headers(client, "mwanga@suppliers.usiri.co.tz")
    sanaa = supplier_headers(client, "sanaa@suppliers.usiri.co.tz")
    own = supplier_order_for(client, mwanga, order["id"])

    assert client.get(f"/api/supplier/orders/{own['id']}", headers=sanaa).status_code == 403
    assert (
        client.post(f"/api/supplier/orders/{own['id']}/accept", headers=sanaa, json={}).status_code
        == 403
    )
    assert client.get(f"/api/orders/{order['id']}", headers=sanaa).status_code == 403


def test_customer_cannot_read_another_customers_order(client, customer):
    kettle, _ = variant_of(client, "electric-kettle-1.8l")
    order = place_order(client, customer, [(kettle, 1)])
    other = auth(client, "daniel@example.co.tz")
    assert client.get(f"/api/orders/{order['id']}", headers=other).status_code == 403


def test_pending_supplier_products_are_not_public(client):
    pending = auth(client, "arusha@suppliers.usiri.co.tz")
    departments = client.get("/api/catalogue/departments").json()
    response = client.post(
        "/api/supplier/products",
        headers=pending,
        json={
            "name": "Hand-carved Serving Board",
            "department_id": departments[0]["id"],
            "variants": [{"name": "Standard", "price": 45000, "on_hand": 5}],
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["slug"] not in [
        p["slug"] for p in client.get("/api/catalogue/products").json()["items"]
    ]


def test_webhook_signature_and_idempotency(client, customer):
    kettle, _ = variant_of(client, "electric-kettle-1.8l")
    order = place_order(client, customer, [(kettle, 1)])
    payment = client.post(
        f"/api/orders/{order['id']}/payments", headers=customer, json={"method": "mobile_money"}
    ).json()["payment"]

    body = json.dumps({"provider_ref": payment["provider_ref"], "status": "succeeded"})
    bad = client.post(
        "/api/webhooks/psp",
        content=body,
        headers={"X-PSP-Signature": "not-the-signature", "Content-Type": "application/json"},
    )
    assert bad.status_code == 401

    # the callback body is only a hint: the server confirms with the provider first
    still_pending = client.post(
        "/api/webhooks/psp",
        content=body,
        headers={"X-PSP-Signature": new_webhook_signature(body), "Content-Type": "application/json"},
    )
    assert still_pending.status_code == 200
    assert still_pending.json()["payment_status"] == "pending"

    get_provider().set_status(payment["provider_ref"], "succeeded")
    signed = client.post(
        "/api/webhooks/psp",
        content=body,
        headers={"X-PSP-Signature": new_webhook_signature(body), "Content-Type": "application/json"},
    )
    assert signed.status_code == 200
    assert signed.json()["payment_status"] == "succeeded"

    replay = client.post(
        "/api/webhooks/psp",
        content=body,
        headers={"X-PSP-Signature": new_webhook_signature(body), "Content-Type": "application/json"},
    )
    assert replay.status_code == 200
    detail = client.get(f"/api/orders/{order['id']}", headers=customer).json()
    assert detail["payment_status"] == "paid"


def test_registration_rules(client):
    duplicate = client.post(
        "/api/auth/register",
        json={"email": "demo@usiri.co.tz", "password": "Long-enough-1", "full_name": "Copy Cat"},
    )
    assert duplicate.status_code == 409

    weak = client.post(
        "/api/auth/register",
        json={"email": "new@example.co.tz", "password": "short", "full_name": "New Person"},
    )
    assert weak.status_code == 422

    created = client.post(
        "/api/auth/register",
        json={"email": "new@example.co.tz", "password": "Long-enough-1", "full_name": "New Person"},
    )
    assert created.status_code == 201
    token = created.json()["access_token"]
    assert client.get("/api/cart", headers={"Authorization": f"Bearer {token}"}).json()["items"] == []


def test_admin_actions_are_audited(client, admin):
    before = client.put(
        "/api/ops/config", headers=admin, json={"values": {"delivery_fee_flat": 7500}}
    )
    assert before.status_code == 200
    log = client.get("/api/ops/audit", headers=admin, params={"action": "config.updated"}).json()
    assert log["items"]
    assert log["items"][0]["after"]["delivery_fee_flat"] == 7500
    unknown = client.put("/api/ops/config", headers=admin, json={"values": {"nope": 1}})
    assert unknown.status_code == 400


def test_supplier_can_manage_own_stock(client):
    mwanga = supplier_headers(client, "mwanga@suppliers.usiri.co.tz")
    products = client.get("/api/supplier/products", headers=mwanga).json()["items"]
    variant = products[0]["variants"][0]
    response = client.patch(
        f"/api/supplier/variants/{variant['id']}", headers=mwanga, json={"on_hand": 7}
    )
    assert response.status_code == 200
    assert response.json()["on_hand"] == 7

    sanaa = supplier_headers(client, "sanaa@suppliers.usiri.co.tz")
    forbidden = client.patch(
        f"/api/supplier/variants/{variant['id']}", headers=sanaa, json={"on_hand": 1}
    )
    assert forbidden.status_code == 403


def test_customer_support_ticket_thread(client, customer, support):
    order = place_order(client, customer, [(variant_of(client, "electric-kettle-1.8l")[0], 1)])
    ticket = client.post(
        "/api/support/tickets",
        headers=customer,
        json={"subject": "Where is my order?", "category": "order", "order_id": order["id"], "message": "Please advise"},
    )
    assert ticket.status_code == 201
    ticket_id = ticket.json()["id"]

    assert client.post(
        f"/api/support/tickets/{ticket_id}/messages",
        headers=support,
        json={"body": "We are checking with the supplier."},
    ).status_code == 201
    assert client.patch(
        f"/api/ops/tickets/{ticket_id}", headers=support, json={"status": "in_progress", "priority": "high"}
    ).status_code == 200

    detail = client.get(f"/api/support/tickets/{ticket_id}", headers=customer).json()
    assert len(detail["messages"]) == 2
    assert detail["priority"] == "high"

    internal = client.post(
        f"/api/support/tickets/{ticket_id}/messages",
        headers=customer,
        json={"body": "secret", "internal": True},
    )
    assert internal.status_code == 403
