from __future__ import annotations

from datetime import timedelta

from app.db import SessionLocal
from app.models import SupplierOrder, utcnow
from app.services import ledger

from .conftest import (
    fulfil,
    pay,
    place_order,
    supplier_headers,
    supplier_order_for,
    variant_of,
)

KETTLE = "electric-kettle-1.8l"
BUTTER = "baobab-body-butter-250ml"
DRESS = "cotton-wrap-dress"


def test_capture_and_partial_rejection_keep_the_ledger_balanced(client, customer):
    kettle, kettle_price = variant_of(client, KETTLE)
    butter, butter_price = variant_of(client, BUTTER)
    order = place_order(client, customer, [(kettle, 1), (butter, 2)])
    pay(client, customer, order["id"])

    with SessionLocal() as db:
        assert ledger.is_balanced(db)
        assert ledger.account_balance(db, "psp_clearing") == order["total"]
        assert ledger.account_balance(db, "supplier_payable") == (
            kettle_price + butter_price * 2
        ) - (kettle_price + butter_price * 2) * 8 // 100
        assert ledger.account_balance(db, "delivery_revenue") == 14_000

    zanzibar = supplier_headers(client, "zanzibar@suppliers.usiri.co.tz")
    so = supplier_order_for(client, zanzibar, order["id"])
    response = client.post(
        f"/api/supplier/orders/{so['id']}/reject",
        headers=zanzibar,
        json={"reason": "Out of stock"},
    )
    assert response.status_code == 200

    detail = client.get(f"/api/orders/{order['id']}", headers=customer).json()
    assert detail["payment_status"] == "partially_refunded"
    assert detail["refunded_total"] == butter_price * 2 + 7000

    with SessionLocal() as db:
        assert ledger.is_balanced(db)
        # the rejected supplier's payable and commission are reversed, delivery too
        assert ledger.account_balance(db, "delivery_revenue") == 7000
        assert ledger.account_balance(db, "supplier_payable") == 57_040
        assert ledger.account_balance(db, "platform_revenue") == 4_960


def test_return_window_qty_and_refund(client, customer, support):
    kettle, kettle_price = variant_of(client, KETTLE)
    order = place_order(client, customer, [(kettle, 1)])
    pay(client, customer, order["id"])
    mwanga = supplier_headers(client, "mwanga@suppliers.usiri.co.tz")
    so = supplier_order_for(client, mwanga, order["id"])
    fulfil(client, mwanga, so["id"])

    detail = client.get(f"/api/orders/{order['id']}", headers=customer).json()
    item = detail["items"][0]
    assert item["status"] == "delivered"
    assert item["returnable"] is True

    too_many = client.post(
        f"/api/orders/{order['id']}/returns",
        headers=customer,
        json={"item_id": item["id"], "qty": 2, "reason": "damaged"},
    )
    assert too_many.status_code == 409

    created = client.post(
        f"/api/orders/{order['id']}/returns",
        headers=customer,
        json={"item_id": item["id"], "qty": 1, "reason": "damaged", "details": "Cracked lid"},
    )
    assert created.status_code == 201, created.text
    ret = created.json()

    duplicate = client.post(
        f"/api/orders/{order['id']}/returns",
        headers=customer,
        json={"item_id": item["id"], "qty": 1, "reason": "damaged"},
    )
    assert duplicate.status_code == 409

    approve = client.post(
        f"/api/ops/returns/{ret['id']}/decide", headers=support, json={"approve": True}
    )
    assert approve.status_code == 200
    received = client.post(f"/api/ops/returns/{ret['id']}/receive", headers=support)
    assert received.status_code == 200, received.text
    assert received.json()["refund_amount"] == kettle_price

    with SessionLocal() as db:
        assert ledger.is_balanced(db)
        assert ledger.account_balance(db, "psp_clearing") == 7000  # only delivery stays
        assert ledger.account_balance(db, "supplier_payable") == 0

    # a second return is blocked because the item is already refunded
    again = client.post(
        f"/api/orders/{order['id']}/returns",
        headers=customer,
        json={"item_id": item["id"], "qty": 1, "reason": "damaged"},
    )
    assert again.status_code == 409


def test_return_window_closes(client, customer):
    kettle, _ = variant_of(client, KETTLE)
    order = place_order(client, customer, [(kettle, 1)])
    pay(client, customer, order["id"])
    mwanga = supplier_headers(client, "mwanga@suppliers.usiri.co.tz")
    so = supplier_order_for(client, mwanga, order["id"])
    fulfil(client, mwanga, so["id"])

    with SessionLocal() as db:
        row = db.get(SupplierOrder, so["id"])
        row.delivered_at = utcnow() - timedelta(days=9)
        db.commit()

    detail = client.get(f"/api/orders/{order['id']}", headers=customer).json()
    item_id = detail["items"][0]["id"]
    response = client.post(
        f"/api/orders/{order['id']}/returns",
        headers=customer,
        json={"item_id": item_id, "qty": 1, "reason": "changed_mind"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "return_window_closed"


def test_payout_requires_hold_then_maker_checker(client, customer, finance, finance2):
    dress, dress_price = variant_of(client, DRESS)
    order = place_order(client, customer, [(dress, 1)])
    pay(client, customer, order["id"])
    sanaa = supplier_headers(client, "sanaa@suppliers.usiri.co.tz")
    so = supplier_order_for(client, sanaa, order["id"])
    fulfil(client, sanaa, so["id"])

    supplier_id = so["supplier_id"]
    early = client.post("/api/ops/payouts", headers=finance, json={"supplier_id": supplier_id})
    assert early.status_code == 409
    assert early.json()["code"] == "no_eligible_balance"
    held = client.get("/api/ops/payouts/eligible", headers=finance).json()["items"]
    assert all(row["supplier"]["id"] != supplier_id for row in held)

    # wait out the hold window by moving the eligibility clock
    with SessionLocal() as db:
        row = db.get(SupplierOrder, so["id"])
        row.eligible_at = utcnow() - timedelta(minutes=1)
        db.commit()

    expected = dress_price - dress_price * 8 // 100
    eligible = client.get("/api/ops/payouts/eligible", headers=finance).json()["items"]
    supplier_row = next(row for row in eligible if row["supplier"]["id"] == supplier_id)
    assert supplier_row["balance"]["eligible"] == expected
    created = client.post("/api/ops/payouts", headers=finance, json={"supplier_id": supplier_id})
    assert created.status_code == 201, created.text
    payout = created.json()
    assert payout["amount"] == expected
    assert payout["status"] == "pending_approval"

    self_approval = client.post(
        f"/api/ops/payouts/{payout['id']}/approve", headers=finance, json={}
    )
    assert self_approval.status_code == 403

    approved = client.post(f"/api/ops/payouts/{payout['id']}/approve", headers=finance2, json={})
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    executed = client.post(f"/api/ops/payouts/{payout['id']}/execute", headers=finance)
    assert executed.status_code == 200
    assert executed.json()["status"] == "paid"

    with SessionLocal() as db:
        assert ledger.is_balanced(db)
        assert ledger.account_balance(db, "supplier_payable") == 0
        assert ledger.account_balance(db, "psp_clearing") == dress_price + 7000 - expected


def test_payment_failure_keeps_order_payable_and_stock_held(client, customer):
    kettle, _ = variant_of(client, KETTLE)
    order = place_order(client, customer, [(kettle, 1)])
    payment = pay(client, customer, order["id"], outcome="failed")
    assert payment["status"] == "failed"

    detail = client.get(f"/api/orders/{order['id']}", headers=customer).json()
    assert detail["status"] == "pending_payment"
    assert detail["payment_status"] == "unpaid"

    # a retry can still be paid
    second = pay(client, customer, order["id"])
    assert second["status"] == "succeeded"
    detail = client.get(f"/api/orders/{order['id']}", headers=customer).json()
    assert detail["status"] == "paid"
