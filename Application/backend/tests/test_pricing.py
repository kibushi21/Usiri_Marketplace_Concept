from __future__ import annotations

from types import SimpleNamespace

from app.services.pricing import (
    QuoteLine,
    build_quote,
    commission_for,
    delivery_fee_for,
)

CONFIG = {
    "commission_bp": 800,
    "delivery_fee_flat": 7000,
    "free_delivery_threshold": 150_000,
}


def test_commission_rounds_half_up():
    assert commission_for(100_000, 800) == 8_000
    assert commission_for(12_345, 800) == 988  # 987.6
    assert commission_for(0, 800) == 0


def test_delivery_fee_waived_above_threshold():
    assert delivery_fee_for(149_999, CONFIG) == 7000
    assert delivery_fee_for(150_000, CONFIG) == 0


def test_quote_groups_suppliers_and_charges_delivery_per_shipment():
    supplier_a = SimpleNamespace(id="a", commission_bp=None)
    supplier_b = SimpleNamespace(id="b", commission_bp=1000)

    def line(supplier, price, qty):
        product = SimpleNamespace(supplier_id=supplier.id, supplier=supplier)
        variant = SimpleNamespace(price_tzs=price, product=product)
        return QuoteLine(variant=variant, qty=qty)

    lines = [line(supplier_a, 40_000, 2), line(supplier_b, 25_000, 1)]
    quote = build_quote(lines, CONFIG, {"a": supplier_a, "b": supplier_b})

    assert quote["subtotal"] == 105_000
    assert quote["delivery_total"] == 14_000
    assert quote["total"] == 119_000
    assert quote["suppliers"]["a"].commission_amount == 6_400  # 8%
    assert quote["suppliers"]["b"].commission_amount == 2_500  # supplier override 10%
    assert quote["suppliers"]["a"].supplier_payable == 73_600
    assert quote["suppliers"]["b"].supplier_payable == 22_500


def test_free_delivery_applies_per_supplier_not_basket():
    supplier = SimpleNamespace(id="a", commission_bp=None)

    def line(price, qty):
        product = SimpleNamespace(supplier_id="a", supplier=supplier)
        variant = SimpleNamespace(price_tzs=price, product=product)
        return QuoteLine(variant=variant, qty=qty)

    quote = build_quote([line(100_000, 1), line(60_000, 1)], CONFIG, {"a": supplier})
    assert quote["delivery_total"] == 0
    assert quote["total"] == 160_000
