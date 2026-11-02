from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import PlatformConfig

DEFAULTS: dict[str, Any] = {
    "platform_name": "Usiri",
    "currency": "TZS",
    "commission_bp": 800,
    "delivery_fee_flat": 7000,
    "free_delivery_threshold": 150_000,
    "reservation_ttl_minutes": 30,
    "return_window_days": 7,
    "payout_hold_days": 3,
    "payout_minimum": 20_000,
    "supplier_accept_sla_hours": 24,
    "max_qty_per_line": 20,
    "support_email": "msaada@usiri.co.tz",
    "support_phone": "+255 000 000 000",
    "carrier_default": "Usiri rider network",
    "refund_delivery_on_supplier_rejection": True,
    "refund_delivery_on_return": False,
}

CONFIG_LABELS: dict[str, str] = {
    "commission_bp": "Commission (basis points of merchandise)",
    "delivery_fee_flat": "Flat delivery fee per supplier shipment (TZS)",
    "free_delivery_threshold": "Free delivery basket threshold (TZS)",
    "reservation_ttl_minutes": "Stock reservation lifetime (minutes)",
    "return_window_days": "Return window after delivery (days)",
    "payout_hold_days": "Payout hold after delivery (days)",
    "payout_minimum": "Minimum payout amount (TZS)",
    "supplier_accept_sla_hours": "Supplier acceptance SLA (hours)",
    "max_qty_per_line": "Maximum quantity per line",
}


def load_config(db: Session) -> dict[str, Any]:
    config = dict(DEFAULTS)
    for row in db.scalars(select(PlatformConfig)):
        try:
            config[row.key] = json.loads(row.value)
        except json.JSONDecodeError:
            config[row.key] = row.value
    return config


def get_value(db: Session, key: str) -> Any:
    row = db.get(PlatformConfig, key)
    if row is None:
        return DEFAULTS[key]
    try:
        return json.loads(row.value)
    except json.JSONDecodeError:
        return row.value


def set_value(db: Session, key: str, value: Any, actor_id: str | None = None) -> None:
    if key not in DEFAULTS:
        raise ValueError(f"Unknown configuration key: {key}")
    row = db.get(PlatformConfig, key)
    encoded = json.dumps(value)
    if row is None:
        db.add(PlatformConfig(key=key, value=encoded, updated_by=actor_id))
    else:
        row.value = encoded
        row.updated_by = actor_id
    db.flush()
