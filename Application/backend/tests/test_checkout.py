from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Order, ProductVariant, Reservation, utcnow
from app.models import Reservation as ReservationModel
from app.services import inventory, ledger

from .conftest import default_address, pay, place_order, variant_of


def test_multi_supplier_checkout_splits_shipments(client, customer):
    kettle, kettle_price = variant_of(client, "electric-kettle-1.8l")
    butter, butter_price = variant_of(client, "baobab-body-butter-250ml")
    order = place_order(client, customer, [(kettle, 1), (butter, 2)])

    assert len(order["supplier_orders"]) == 2
    assert order["subtotal"] == kettle_price + butter_price * 2
    assert order["delivery_total"] == 14_000
    assert order["total"] == order["subtotal"] + 14_000
    assert order["status"] == "pending_payment"
    assert order["stage"] == "awaiting_payment"

    with SessionLocal() as db:
        held = db.scalars(select(Reservation).where(Reservation.order_id == order["id"])).all()
        assert len(held) == 2
        assert all(item.status == "held" for item in held)
        variant = db.get(ProductVariant, kettle)
        assert variant.reserved == 1
        assert variant.on_hand == 28  # stock is only committed after payment


def test_checkout_is_idempotent(client, customer):
    kettle, _ = variant_of(client, "electric-kettle-1.8l")
    first = place_order(client, customer, [(kettle, 1)], idempotency_key="checkout-key-1")

    response = client.post(
        "/api/checkout",
        headers={**customer, "Idempotency-Key": "checkout-key-1"},
        json={"address_id": default_address(client, customer)},
    )
    assert response.status_code == 201
    assert response.json()["order"]["id"] == first["id"]

    with SessionLocal() as db:
        assert len(db.scalars(select(Order)).all()) == 1

    response = client.post(
        "/api/checkout",
        headers={**customer, "Idempotency-Key": "checkout-key-1"},
        json={"address_id": "different-address"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "idempotency_conflict"


def test_cannot_oversell(client, customer):
    butter, _ = variant_of(client, "baobab-body-butter-250ml")
    with SessionLocal() as db:
        variant = db.get(ProductVariant, butter)
        variant.on_hand = 1
        db.commit()

    response = client.post(
        "/api/cart/items", headers=customer, json={"variant_id": butter, "qty": 2}
    )
    assert response.status_code == 409
    assert "Only 1 left" in response.json()["detail"]


def test_reservation_expiry_cancels_unpaid_order_and_releases_stock(client, customer):
    butter, _ = variant_of(client, "baobab-body-butter-250ml")
    order = place_order(client, customer, [(butter, 3)])

    with SessionLocal() as db:
        variant = db.get(ProductVariant, butter)
        assert variant.reserved == 3
        for reservation in db.scalars(
            select(ReservationModel).where(ReservationModel.order_id == order["id"])
        ):
            reservation.expires_at = utcnow() - timedelta(minutes=1)
        db.commit()
        inventory.expire_reservations(db)
        db.commit()

        refreshed = db.get(Order, order["id"])
        assert refreshed.status == "cancelled"
        assert db.get(ProductVariant, butter).reserved == 0


def test_cancel_unpaid_releases_reservation(client, customer):
    butter, _ = variant_of(client, "baobab-body-butter-250ml")
    order = place_order(client, customer, [(butter, 2)])

    response = client.post(f"/api/orders/{order['id']}/cancel", headers=customer)
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

    with SessionLocal() as db:
        assert db.get(ProductVariant, butter).reserved == 0


def test_cancel_after_payment_refunds_and_restocks(client, customer, finance):
    kettle, price = variant_of(client, "electric-kettle-1.8l")
    order = place_order(client, customer, [(kettle, 1)])
    pay(client, customer, order["id"])

    with SessionLocal() as db:
        assert db.get(ProductVariant, kettle).on_hand == 27

    response = client.post(f"/api/orders/{order['id']}/cancel", headers=customer)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "cancelled"
    assert body["payment_status"] == "refunded"
    assert body["refunded_total"] == price + 7000

    with SessionLocal() as db:
        assert db.get(ProductVariant, kettle).on_hand == 28
        assert ledger.is_balanced(db)
        assert ledger.account_balance(db, "supplier_payable") == 0
        assert ledger.account_balance(db, "platform_revenue") == 0
        assert ledger.account_balance(db, "delivery_revenue") == 0

    refunds = client.get(f"/api/orders/{order['id']}/refunds", headers=finance).json()["items"]
    assert len(refunds) == 1
    assert refunds[0]["amount"] == price + 7000


def test_config_changes_apply_to_new_orders(client, admin, customer):
    kettle, kettle_price = variant_of(client, "electric-kettle-1.8l")
    response = client.put(
        "/api/ops/config",
        headers=admin,
        json={"values": {"commission_bp": 1200, "delivery_fee_flat": 9000}},
    )
    assert response.status_code == 200, response.text

    order = place_order(client, customer, [(kettle, 1)])
    assert order["delivery_total"] == 9000
    supplier_order = order["supplier_orders"][0]
    assert supplier_order["commission_bp"] == 1200
    assert supplier_order["commission_amount"] == round(kettle_price * 0.12)
    # payment is still required before revenue is recognised
    assert order["payment_status"] == "unpaid"
