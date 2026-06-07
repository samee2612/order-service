from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from backend.models.order import Order


@dataclass(frozen=True)
class CreateOrderItem:
    sku: str
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True)
class CreateOrderRequest:
    customer_id: str
    items: tuple[CreateOrderItem, ...]
    payment_method_id: str
    shipping_address_id: str


@dataclass(frozen=True)
class CancelOrderRequest:
    cancellation_reason: str


@dataclass(frozen=True)
class OrderResponse:
    order_id: str
    customer_id: str
    status: str
    item_count: int
    total_amount: str
    checkout_next_step: str

    @classmethod
    def from_order(cls, order: Order) -> "OrderResponse":
        return cls(
            order_id=order.order_id,
            customer_id=order.customer_id,
            status=order.status,
            item_count=order.item_count,
            total_amount=f"{order.total_amount:.2f}",
            checkout_next_step="collect_payment" if order.status == "created" else "view_order",
        )
