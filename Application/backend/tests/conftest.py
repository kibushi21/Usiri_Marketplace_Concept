from __future__ import annotations

import os
from pathlib import Path

TEST_DB = Path(__file__).resolve().parent.parent / "var" / "test.db"
os.environ["USIRI_DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["USIRI_ENVIRONMENT"] = "test"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.seed import seed

PASSWORD = "Usiri#2026"


@pytest.fixture(autouse=True)
def fresh_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def customer(client):
    return auth(client, "demo@usiri.co.tz")


@pytest.fixture
def admin(client):
    return auth(client, "admin@usiri.co.tz")


@pytest.fixture
def finance(client):
    return auth(client, "finance@usiri.co.tz")


@pytest.fixture
def finance2(client):
    return auth(client, "finance2@usiri.co.tz")


@pytest.fixture
def support(client):
    return auth(client, "support@usiri.co.tz")


def auth(client: TestClient, email: str, password: str = PASSWORD) -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def variant_of(client: TestClient, slug: str, index: int = 0) -> tuple[str, int]:
    product = client.get(f"/api/catalogue/products/{slug}").json()
    variant = product["variants"][index]
    return variant["id"], variant["price"]


def default_address(client: TestClient, headers: dict[str, str]) -> str:
    return client.get("/api/auth/me", headers=headers).json()["addresses"][0]["id"]


def place_order(
    client: TestClient,
    headers: dict[str, str],
    items: list[tuple[str, int]],
    *,
    idempotency_key: str | None = None,
    address_id: str | None = None,
) -> dict:
    for variant_id, qty in items:
        response = client.post(
            "/api/cart/items", headers=headers, json={"variant_id": variant_id, "qty": qty}
        )
        assert response.status_code == 201, response.text
    extra = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
    response = client.post(
        "/api/checkout",
        headers={**headers, **extra},
        json={"address_id": address_id or default_address(client, headers)},
    )
    assert response.status_code == 201, response.text
    return response.json()["order"]


def pay(
    client: TestClient,
    headers: dict[str, str],
    order_id: str,
    *,
    outcome: str = "succeeded",
    method: str = "mobile_money",
) -> dict:
    response = client.post(
        f"/api/orders/{order_id}/payments",
        headers=headers,
        json={"method": method, "msisdn": "+255712000001"},
    )
    assert response.status_code == 201, response.text
    payment = response.json()["payment"]
    if outcome:
        result = client.post(
            f"/api/payments/{payment['id']}/simulate", headers=headers, json={"outcome": outcome}
        )
        assert result.status_code == 200, result.text
        return result.json()["payment"]
    return payment


def supplier_headers(client: TestClient, email: str) -> dict[str, str]:
    return auth(client, email)


def supplier_order_for(
    client: TestClient, headers: dict[str, str], order_id: str
) -> dict:
    items = client.get("/api/supplier/orders", headers=headers).json()["items"]
    matches = [item for item in items if item["order_id"] == order_id]
    assert matches, "supplier order not found"
    return matches[0]


def fulfil(
    client: TestClient,
    headers: dict[str, str],
    supplier_order_id: str,
    *,
    tracking: str = "TRK-TEST-001",
) -> None:
    accept = client.post(
        f"/api/supplier/orders/{supplier_order_id}/accept", headers=headers, json={}
    )
    assert accept.status_code == 200, accept.text
    ready = client.post(f"/api/supplier/orders/{supplier_order_id}/ready", headers=headers)
    assert ready.status_code == 200, ready.text
    ship = client.post(
        f"/api/supplier/orders/{supplier_order_id}/ship",
        headers=headers,
        json={"tracking_number": tracking, "carrier": "Usiri rider"},
    )
    assert ship.status_code == 200, ship.text
    deliver = client.post(
        f"/api/supplier/orders/{supplier_order_id}/deliver",
        headers=headers,
        json={"pod_ref": "POD-TEST"},
    )
    assert deliver.status_code == 200, deliver.text
