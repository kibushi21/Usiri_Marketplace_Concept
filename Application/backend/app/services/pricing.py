from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..models import ProductVariant

BP_DIVISOR = 10_000


def commission_for(merchandise_total: int, bp: int) -> int:
    """Round half up to the nearest shilling."""
    return (merchandise_total * bp + BP_DIVISOR // 2) // BP_DIVISOR


def delivery_fee_for(merchandise_total: int, config: dict[str, Any]) -> int:
    threshold = int(config["free_delivery_threshold"])
    if threshold and merchandise_total >= threshold:
        return 0
    return int(config["delivery_fee_flat"])


@dataclass
class QuoteLine:
    variant: ProductVariant
    qty: int

    @property
    def unit_price(self) -> int:
        return self.variant.price_tzs

    @property
    def line_total(self) -> int:
        return self.unit_price * self.qty

    @property
    def supplier_id(self) -> str:
        return self.variant.product.supplier_id


@dataclass
class SupplierQuote:
    supplier_id: str
    merchandise_total: int = 0
    delivery_fee: int = 0
    commission_bp: int = 0
    commission_amount: int = 0
    supplier_payable: int = 0
    lines: list[QuoteLine] = field(default_factory=list)


def build_quote(lines: list[QuoteLine], config: dict[str, Any], suppliers_by_id: dict) -> dict[str, Any]:
    groups: dict[str, SupplierQuote] = {}
    for line in lines:
        supplier_id = line.supplier_id
        group = groups.get(supplier_id)
        if group is None:
            supplier = suppliers_by_id[supplier_id]
            group = SupplierQuote(
                supplier_id=supplier_id,
                commission_bp=int(supplier.commission_bp if supplier.commission_bp is not None else config["commission_bp"]),
            )
            groups[supplier_id] = group
        group.lines.append(line)
        group.merchandise_total += line.line_total

    for group in groups.values():
        group.delivery_fee = delivery_fee_for(group.merchandise_total, config)
        group.commission_amount = commission_for(group.merchandise_total, group.commission_bp)
        group.supplier_payable = group.merchandise_total - group.commission_amount

    subtotal = sum(line.line_total for line in lines)
    delivery_total = sum(group.delivery_fee for group in groups.values())
    return {
        "suppliers": groups,
        "subtotal": subtotal,
        "delivery_total": delivery_total,
        "total": subtotal + delivery_total,
        "commission_total": sum(group.commission_amount for group in groups.values()),
        "line_count": sum(line.qty for line in lines),
    }
