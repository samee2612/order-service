from __future__ import annotations

from backend.models.order import Order


class OrderRepositoryError(RuntimeError):
    pass


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}

    def save(self, order: Order) -> Order:
        self._orders[order.order_id] = order
        return order

    def get(self, order_id: str) -> Order:
        try:
            return self._orders[order_id]
        except KeyError as error:
            raise OrderRepositoryError(f"Order not found: {order_id}") from error
