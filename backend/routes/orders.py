from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

OrderStatus = Literal["created", "paid", "fulfilled", "cancelled"]


@dataclass(frozen=True)
class OrderSummary:
    order_id: str
    customer_id: str
    status: OrderStatus
    item_count: int


def create_order(customer_id: str, item_count: int) -> OrderSummary:
    if not customer_id:
        raise ValueError("customer_id is required")
    if item_count <= 0:
        raise ValueError("item_count must be greater than zero")

    return OrderSummary(
        order_id="order_test_001",
        customer_id=customer_id,
        status="created",
        item_count=item_count,
    )
