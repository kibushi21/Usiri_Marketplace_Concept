from __future__ import annotations

from fastapi.testclient import TestClient


def _ask(
    client: TestClient,
    message: str,
    *,
    audience: str = "customer",
    headers: dict[str, str] | None = None,
):
    return client.post(
        "/api/assistant/chat",
        headers=headers or {},
        json={"message": message, "audience": audience, "history": []},
    )


def test_customer_product_question_returns_catalogue_matches(client):
    response = _ask(client, "Show me stainless steel kettles")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["provider"] == "mock"
    assert data["model"] is None
    assert data["audience"] == "customer"
    assert data["products"][0]["slug"] == "electric-kettle-1.8l"
    assert "Electric Kettle" in data["reply"]
    assert "no language model" in data["note"].lower()


def test_answers_use_current_store_settings(client):
    delivery = _ask(client, "How much is delivery?").json()
    assert "7,000" in delivery["reply"]
    assert "150,000" in delivery["reply"]

    returns = _ask(client, "What is the return window?").json()
    assert "7 days" in returns["reply"]


def test_market_question_is_answered_honestly(client):
    data = _ask(client, "What are the best selling products in Tanzania?").json()
    assert "Tanzania-wide" in data["reply"]
    assert "no market sales data" in data["reply"]
    assert data["products"] == []


def test_ops_assistant_requires_staff(client, customer, support):
    assert _ask(client, "How do payouts work?", audience="ops").status_code == 401

    forbidden = _ask(client, "How do payouts work?", audience="ops", headers=customer)
    assert forbidden.status_code == 403

    data = _ask(client, "How do payouts work?", audience="ops", headers=support).json()
    assert data["audience"] == "ops"
    assert "maker-checker" in data["reply"]


def test_assistant_rejects_invalid_requests(client):
    empty = client.post("/api/assistant/chat", json={"message": ""})
    assert empty.status_code == 422

    too_long = client.post("/api/assistant/chat", json={"message": "x" * 1001})
    assert too_long.status_code == 422

    bad_audience = client.post(
        "/api/assistant/chat", json={"message": "hello", "audience": "supplier"}
    )
    assert bad_audience.status_code == 422
