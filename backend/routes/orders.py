from __future__ import annotations

from backend.repositories.order_repository import InMemoryOrderRepository
from backend.schemas.orders import CancelOrderRequest, CreateOrderRequest, ListOrdersResponse, OrderResponse
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


def list_orders_route(customer_id: str) -> ListOrdersResponse:
    """GET /orders?customer_id={customer_id} - list all orders for a customer."""
    orders = order_service.list_orders_for_customer(customer_id)
    order_responses = tuple(OrderResponse.from_order(order) for order in orders)
    return ListOrdersResponse(
        customer_id=customer_id,
        orders=order_responses,
        total_count=len(order_responses),
    )


def cancel_order_route(order_id: str, request: CancelOrderRequest) -> OrderResponse:
    """POST /orders/{order_id}/cancel - cancel a checkout order before fulfillment."""
    order = order_service.cancel_order(order_id, request.cancellation_reason)
    return OrderResponse.from_order(order)
