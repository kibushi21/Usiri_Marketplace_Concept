from __future__ import annotations

from datetime import timedelta

from app.db import SessionLocal
from app.models import utcnow
from app.services import tracking

from .conftest import (
    pay,
    place_order,
    supplier_headers,
    supplier_order_for,
    variant_of,
)

KETTLE = "electric-kettle-1.8l"


def _shipped_order(client, customer):
    kettle, _ = variant_of(client, KETTLE)
    order = place_order(client, customer, [(kettle, 1)])
    pay(client, customer, order["id"])
    mwanga = supplier_headers(client, "mwanga@suppliers.usiri.co.tz")
    so = supplier_order_for(client, mwanga, order["id"])
    accept = client.post(f"/api/supplier/orders/{so['id']}/accept", headers=mwanga, json={})
    assert accept.status_code == 200, accept.text
    ready = client.post(f"/api/supplier/orders/{so['id']}/ready", headers=mwanga)
    assert ready.status_code == 200, ready.text
    ship = client.post(f"/api/supplier/orders/{so['id']}/ship", headers=mwanga, json={})
    assert ship.status_code == 200, ship.text
    return order, ship.json()["shipments"][0]


def test_customer_tracks_each_supplier_batch(client, customer):
    order, shipment = _shipped_order(client, customer)
    assert shipment["tracking_number"].startswith("TRK-")
    assert shipment["mode"] == "api"

    with SessionLocal() as db:
        assert tracking.advance_due(db, now=utcnow() + timedelta(minutes=10)) > 0
        db.commit()

    detail = client.get(f"/api/orders/{order['id']}", headers=customer).json()
    so = detail["supplier_orders"][0]
    batch = so["shipments"][0]
    statuses = [event["status"] for event in batch["events"]]
    assert statuses == ["booked", "picked_up", "in_transit", "out_for_delivery"]
    assert batch["status"] == "out_for_delivery"
    assert all(event["actor"] == "carrier" for event in batch["events"])
    assert so["supplier"]["name"]


def test_ops_override_is_recorded_and_freezes_simulation(client, customer, support):
    order, shipment = _shipped_order(client, customer)

    forbidden = client.post(
        f"/api/ops/shipments/{shipment['id']}/tracking",
        headers=customer,
        json={"status": "delayed"},
    )
    assert forbidden.status_code == 403

    response = client.post(
        f"/api/ops/shipments/{shipment['id']}/tracking",
        headers=support,
        json={"status": "delayed", "note": "Heavy rain on the Dar es Salaam route"},
    )
    assert response.status_code == 200, response.text
    updated = response.json()
    assert updated["status"] == "delayed"
    assert updated["events"][-1]["actor"] == "operations"
    assert updated["events"][-1]["note"] == "Heavy rain on the Dar es Salaam route"

    with SessionLocal() as db:
        assert tracking.advance_due(db, now=utcnow() + timedelta(hours=3)) == 0

    detail = client.get(f"/api/orders/{order['id']}", headers=customer).json()
    batch = detail["supplier_orders"][0]["shipments"][0]
    assert batch["status"] == "delayed"
    assert "out_for_delivery" not in [event["status"] for event in batch["events"]]

    audit = client.get("/api/ops/audit?limit=50", headers=support).json()["items"]
    assert any(entry["action"] == "shipment.tracking_updated" for entry in audit)


def test_tracking_is_closed_after_delivery(client, customer, support):
    _, shipment = _shipped_order(client, customer)
    supplier_order_id = shipment["supplier_order_id"]
    delivered = client.post(
        f"/api/supplier/orders/{supplier_order_id}/deliver",
        headers=supplier_headers(client, "mwanga@suppliers.usiri.co.tz"),
        json={"pod_ref": "POD-TRACK-1"},
    )
    assert delivered.status_code == 200, delivered.text

    response = client.post(
        f"/api/ops/shipments/{shipment['id']}/tracking",
        headers=support,
        json={"status": "delayed"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "tracking_closed"
