from __future__ import annotations

from backend.repositories.order_repository import InMemoryOrderRepository
from backend.schemas.orders import CreateOrderRequest, OrderResponse
from backend.services.order_service import OrderService

order_repository = InMemoryOrderRepository()
order_service = OrderService(order_repository)


def create_order_route(request: CreateOrderRequest) -> OrderResponse:
    """POST /orders - create a checkout order and return the client response."""
    order = order_service.create_order(request)
    return OrderResponse.from_order(order)


def get_order_route(order_id: str) -> OrderResponse:
    """GET /orders/{order_id} - return the current order summary."""
    order = order_service.get_order(order_id)
    return OrderResponse.from_order(order)
