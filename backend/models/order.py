from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

OrderStatus = Literal["created", "paid", "fulfilled", "cancelled", "refunded"]


@dataclass(frozen=True)
class OrderItem:
    sku: str
    quantity: int
    unit_price: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass(frozen=True)
class Order:
    order_id: str
    customer_id: str
    items: tuple[OrderItem, ...]
    status: OrderStatus
    total_amount: Decimal

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)
