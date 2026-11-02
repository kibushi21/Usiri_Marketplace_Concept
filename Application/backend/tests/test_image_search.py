from __future__ import annotations


def _upload(client, filename: str, data: bytes = b"\x89PNG\r\n\x1a\n demo", content_type: str = "image/png", **form):
    return client.post(
        "/api/catalogue/image-search",
        files={"file": (filename, data, content_type)},
        data=form,
    )


def test_filename_keywords_match_catalogue_products(client):
    response = _upload(client, "stainless-steel-kettle.png")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["provider"] == "mock"
    assert "kettle" in body["tags"]
    assert body["total"] > 0
    assert body["items"][0]["slug"] == "electric-kettle-1.8l"
    assert "kitchen" in body["note"].lower() or "demo" in body["note"].lower()


def test_customer_hint_is_used_when_filename_is_generic(client):
    response = _upload(client, "IMG_2041.jpg", content_type="image/jpeg", hint="kettle")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["tags"] == ["kettle"]
    assert body["items"][0]["slug"] == "electric-kettle-1.8l"


def test_no_keywords_returns_empty_with_guidance(client):
    response = _upload(client, "IMG_2041.jpg", content_type="image/jpeg")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["tags"] == []
    assert body["total"] == 0
    assert body["items"] == []
    assert body["note"]


def test_non_image_upload_is_rejected(client):
    response = _upload(client, "notes.txt", data=b"hello", content_type="text/plain")
    assert response.status_code == 415


def test_oversized_image_is_rejected(client):
    big = b"x" * (5 * 1024 * 1024 + 1)
    response = _upload(client, "kettle.png", data=big)
    assert response.status_code == 413
