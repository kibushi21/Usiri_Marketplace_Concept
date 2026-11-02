from __future__ import annotations

import pytest
from starlette.websockets import WebSocketDisconnect

from .conftest import (
    auth,
    pay,
    place_order,
    supplier_headers,
    supplier_order_for,
    variant_of,
)

SUPPLIER_EMAIL = "mwanga@suppliers.usiri.co.tz"


def paid_order(client, customer) -> tuple[dict, dict[str, str], dict]:
    kettle, _ = variant_of(client, "electric-kettle-1.8l")
    order = place_order(client, customer, [(kettle, 1)])
    pay(client, customer, order["id"])
    mwanga = supplier_headers(client, SUPPLIER_EMAIL)
    return order, mwanga, supplier_order_for(client, mwanga, order["id"])


def dispatch(client, headers: dict[str, str], supplier_order_id: str) -> None:
    accept = client.post(
        f"/api/supplier/orders/{supplier_order_id}/accept", headers=headers, json={}
    )
    assert accept.status_code == 200, accept.text
    ready = client.post(
        f"/api/supplier/orders/{supplier_order_id}/ready", headers=headers
    )
    assert ready.status_code == 200, ready.text
    ship = client.post(
        f"/api/supplier/orders/{supplier_order_id}/ship",
        headers=headers,
        json={"tracking_number": "TRK-CHAT-001", "carrier": "Usiri rider"},
    )
    assert ship.status_code == 200, ship.text


def conversations(client, headers: dict[str, str]) -> list[dict]:
    response = client.get("/api/chats", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["items"]


def only_conversation(client, headers: dict[str, str], order_id: str) -> dict:
    matches = [item for item in conversations(client, headers) if item["order_id"] == order_id]
    assert len(matches) == 1, matches
    return matches[0]


def test_checkout_opens_one_shared_thread(client, customer, support):
    order, mwanga, _ = paid_order(client, customer)

    customer_view = only_conversation(client, customer, order["id"])
    assert customer_view["code"].startswith("CH-")
    assert customer_view["order_code"] == order["code"]
    assert customer_view["assigned_party"] == "supplier"
    assert customer_view["last_message"]["kind"] == "system"
    assert customer_view["can_reply"] is True

    supplier_view = only_conversation(client, mwanga, order["id"])
    assert supplier_view["id"] == customer_view["id"]
    assert supplier_view["can_handoff"] is False

    desk_view = only_conversation(client, support, order["id"])
    assert desk_view["id"] == customer_view["id"]
    assert desk_view["can_take_over"] is True

    finance = auth(client, "finance@usiri.co.tz")
    assert client.get("/api/chats", headers=finance).status_code == 403

    other = auth(client, "daniel@example.co.tz")
    assert client.get(f"/api/chats/{customer_view['id']}", headers=other).status_code == 404


def test_customer_and_supplier_exchange_messages(client, customer, support):
    order, mwanga, _ = paid_order(client, customer)
    conversation = only_conversation(client, customer, order["id"])

    sent = client.post(
        f"/api/chats/{conversation['id']}/messages",
        headers=customer,
        json={"body": "Can you add a warranty card?"},
    )
    assert sent.status_code == 201, sent.text
    assert sent.json()["message"]["author_party"] == "customer"

    reply = client.post(
        f"/api/chats/{conversation['id']}/messages",
        headers=mwanga,
        json={"body": "Yes, the card ships in the box."},
    )
    assert reply.status_code == 201, reply.text
    assert reply.json()["message"]["author_party"] == "supplier"

    blocked = client.post(
        f"/api/chats/{conversation['id']}/messages",
        headers=support,
        json={"body": "Desk here."},
    )
    assert blocked.status_code == 409
    assert blocked.json()["code"] == "desk_not_assigned"

    detail = client.get(f"/api/chats/{conversation['id']}", headers=customer).json()
    bodies = [item["body"] for item in detail["messages"]]
    assert "Can you add a warranty card?" in bodies
    assert "Yes, the card ships in the box." in bodies

    empty = client.post(
        f"/api/chats/{conversation['id']}/messages",
        headers=customer,
        json={"body": "   "},
    )
    assert empty.status_code == 409
    assert empty.json()["code"] == "empty_message"


def test_desk_takes_over_and_returns(client, customer, support):
    order, _, _ = paid_order(client, customer)
    conversation = only_conversation(client, customer, order["id"])

    take = client.post(
        f"/api/chats/{conversation['id']}/assign",
        headers=support,
        json={"party": "logistics", "note": "Rider delay"},
    )
    assert take.status_code == 200, take.text
    assert take.json()["conversation"]["assigned_party"] == "logistics"
    assert take.json()["message"]["kind"] == "handoff"

    reply = client.post(
        f"/api/chats/{conversation['id']}/messages",
        headers=support,
        json={"body": "The rider is 20 minutes away."},
    )
    assert reply.status_code == 201, reply.text
    assert reply.json()["message"]["author_party"] == "logistics"

    hand_back = client.post(
        f"/api/chats/{conversation['id']}/assign",
        headers=support,
        json={"party": "supplier"},
    )
    assert hand_back.status_code == 200, hand_back.text
    assert hand_back.json()["conversation"]["assigned_party"] == "supplier"

    blocked = client.post(
        f"/api/chats/{conversation['id']}/messages",
        headers=support,
        json={"body": "Back again."},
    )
    assert blocked.status_code == 409
    assert blocked.json()["code"] == "desk_not_assigned"

    customer_assign = client.post(
        f"/api/chats/{conversation['id']}/assign",
        headers=customer,
        json={"party": "logistics"},
    )
    assert customer_assign.status_code == 403


def test_supplier_hands_off_after_dispatch(client, customer, support):
    order, mwanga, supplier_order = paid_order(client, customer)
    conversation = only_conversation(client, customer, order["id"])

    early = client.post(
        f"/api/chats/{conversation['id']}/handoff",
        headers=mwanga,
        json={"note": "Please follow up"},
    )
    assert early.status_code == 409
    assert early.json()["code"] == "not_dispatched"

    customer_handoff = client.post(
        f"/api/chats/{conversation['id']}/handoff",
        headers=customer,
        json={},
    )
    assert customer_handoff.status_code == 403

    dispatch(client, mwanga, supplier_order["id"])
    supplier_view = only_conversation(client, mwanga, order["id"])
    assert supplier_view["can_handoff"] is True
    assert supplier_view["shipment"]["status"] == "booked"

    handed = client.post(
        f"/api/chats/{conversation['id']}/handoff",
        headers=mwanga,
        json={"note": "Rider has the kettle"},
    )
    assert handed.status_code == 200, handed.text
    payload = handed.json()
    assert payload["conversation"]["assigned_party"] == "logistics"
    assert payload["conversation"]["handoff_note"] == "Rider has the kettle"
    assert payload["conversation"]["handoff_at"] is not None
    assert payload["message"]["kind"] == "handoff"

    replay = client.post(
        f"/api/chats/{conversation['id']}/handoff",
        headers=mwanga,
        json={},
    )
    assert replay.status_code == 409
    assert replay.json()["code"] == "already_assigned"

    desk_view = only_conversation(client, support, order["id"])
    assert desk_view["assigned_party"] == "logistics"
    assert desk_view["can_reply"] is True


def test_chat_websocket_pushes_messages(client, customer, support):
    order, mwanga, _ = paid_order(client, customer)
    conversation = only_conversation(client, customer, order["id"])
    token = customer["Authorization"].split()[1]

    with client.websocket_connect(
        f"/api/chats/{conversation['id']}/ws?token={token}"
    ) as socket:
        ready = socket.receive_json()
        assert ready == {"type": "ready", "conversation_id": conversation["id"]}

        sent = client.post(
            f"/api/chats/{conversation['id']}/messages",
            headers=mwanga,
            json={"body": "Your order leaves the warehouse today."},
        )
        assert sent.status_code == 201, sent.text

        pushed = socket.receive_json()
        assert pushed["type"] == "message"
        assert pushed["conversation_id"] == conversation["id"]
        assert pushed["message"]["body"] == "Your order leaves the warehouse today."
        assert pushed["message"]["author_party"] == "supplier"

        socket.send_text("ping")
        assert socket.receive_json() == {"type": "pong"}

    with pytest.raises(WebSocketDisconnect) as closed, client.websocket_connect(
        f"/api/chats/{conversation['id']}/ws?token=not-a-token"
    ) as rejected:
        rejected.receive_json()
    assert closed.value.code == 4401
