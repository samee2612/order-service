from __future__ import annotations

from backend.repositories.order_repository import InMemoryOrderRepository
from backend.schemas.orders import CancelOrderRequest, CreateOrderRequest, FulfillOrderRequest, ListOrdersResponse, MarkOrderPaidRequest, OrderResponse, OrderStatusResponse, OrderTrackingResponse, RefundOrderRequest
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


def get_order_status_route(order_id: str) -> OrderStatusResponse:
    """GET /orders/{order_id}/status - return the current lifecycle status and next action."""
    order = order_service.get_order_status(order_id)
    return OrderStatusResponse.from_order(order)


def list_orders_route(customer_id: str) -> ListOrdersResponse:
    """GET /orders?customer_id={customer_id} - list all orders for a customer."""
    orders = order_service.list_orders_for_customer(customer_id)
    order_responses = tuple(OrderResponse.from_order(order) for order in orders)
    return ListOrdersResponse(
        customer_id=customer_id,
        orders=order_responses,
        total_count=len(order_responses),
    )


def mark_order_paid_route(order_id: str, request: MarkOrderPaidRequest) -> OrderResponse:
    """POST /orders/{order_id}/pay - mark a checkout order as paid."""
    order = order_service.mark_order_paid(order_id, request.payment_reference)
    return OrderResponse.from_order(order)


def fulfill_order_route(order_id: str, request: FulfillOrderRequest) -> OrderResponse:
    """POST /orders/{order_id}/fulfill - mark a paid order as fulfilled."""
    order = order_service.fulfill_order(order_id, request.fulfillment_reference)
    return OrderResponse.from_order(order)


def get_order_tracking_route(order_id: str) -> OrderTrackingResponse:
    """GET /orders/{order_id}/tracking - return shipment tracking for fulfilled orders."""
    order, tracking_number, carrier, estimated_delivery = order_service.get_order_tracking(order_id)
    return OrderTrackingResponse.from_order(order, tracking_number, carrier, estimated_delivery)


def refund_order_route(order_id: str, request: RefundOrderRequest) -> OrderResponse:
    """POST /orders/{order_id}/refund - refund a paid or fulfilled order."""
    order = order_service.refund_order(order_id, request.refund_reference, request.refund_reason)
    return OrderResponse.from_order(order)


def cancel_order_route(order_id: str, request: CancelOrderRequest) -> OrderResponse:
    """POST /orders/{order_id}/cancel - cancel a checkout order before fulfillment."""
    order = order_service.cancel_order(order_id, request.cancellation_reason)
    return OrderResponse.from_order(order)
