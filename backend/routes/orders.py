from __future__ import annotations

from backend.repositories.order_repository import InMemoryOrderRepository
from backend.schemas.orders import AddDeliveryInstructionsRequest, DeliveryInstructionsResponse, CancelOrderRequest, CancelOrderResponse, CreateOrderRequest, FulfillOrderRequest, ListOrdersResponse, MarkOrderPaidRequest, InvoiceResponse, OrderResponse, OrderStatusResponse, OrderTrackingResponse, RefundOrderRequest, ExpediteOrderRequest, ExpediteOrderResponse, UpdateShippingAddressRequest, UpdateShippingAddressResponse, AddGiftWrapRequest, GiftWrapResponse, ApplyDiscountRequest, DiscountResponse, AddTipRequest, TipResponse
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


def get_order_invoice_route(order_id: str) -> InvoiceResponse:
    """GET /orders/{order_id}/invoice - return invoice details for billable orders."""
    order, invoice_id, issued_at = order_service.get_order_invoice(order_id)
    return InvoiceResponse.from_order(order, invoice_id, issued_at)
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


def expedite_order_route(order_id: str, request: ExpediteOrderRequest) -> ExpediteOrderResponse:
    """POST /orders/{order_id}/expedite - upgrade shipping speed for a paid order before fulfillment."""
    order = order_service.expedite_order(order_id, request.shipping_speed, request.expedite_fee)
    return ExpediteOrderResponse.from_order(order, request.shipping_speed, request.expedite_fee)


def update_shipping_address_route(
    order_id: str,
    request: UpdateShippingAddressRequest,
) -> UpdateShippingAddressResponse:
    """POST /orders/{order_id}/shipping-address - update delivery address for an unfulfilled order."""
    order = order_service.update_shipping_address(
        order_id,
        request.shipping_address_id,
        request.delivery_instructions,
    )
    return UpdateShippingAddressResponse.from_order(
        order,
        request.shipping_address_id,
        request.delivery_instructions,
    )


def add_gift_wrap_route(
    order_id: str,
    request: AddGiftWrapRequest,
) -> GiftWrapResponse:
    """POST /orders/{order_id}/gift-wrap - add custom gift wrapping and message before fulfillment."""
    order, fee = order_service.add_gift_wrap(
        order_id,
        request.wrap_style,
        request.gift_message,
        request.recipient_name,
    )
    return GiftWrapResponse.from_order(
        order,
        request.wrap_style,
        request.gift_message,
        request.recipient_name,
        fee,
    )


def apply_discount_route(
    order_id: str,
    request: ApplyDiscountRequest,
) -> DiscountResponse:
    """POST /orders/{order_id}/discount - apply promotional coupon code to calculate order savings."""
    order, discount_pct, discount_amount, discounted_total = order_service.apply_discount(
        order_id,
        request.coupon_code,
        request.referral_code,
    )
    return DiscountResponse.from_order(
        order,
        request.coupon_code,
        discount_pct,
        discount_amount,
        discounted_total,
    )


def add_tip_route(
    order_id: str,
    request: AddTipRequest,
) -> TipResponse:
    """POST /orders/{order_id}/tip - add optional courier tip and note before order fulfillment."""
    order, updated_total = order_service.add_tip(
        order_id,
        request.tip_amount,
        request.tip_note,
    )
    return TipResponse.from_order(
        order,
        request.tip_amount,
        request.tip_note,
        updated_total,
    )


def cancel_order_route(
    order_id: str,
    request: CancelOrderRequest,
) -> CancelOrderResponse:
    """POST /orders/{order_id}/cancel - cancel an existing order before fulfillment with a reason."""
    order = order_service.cancel_order(
        order_id,
        request.cancellation_reason,
    )
    return CancelOrderResponse.from_order(
        order,
        request.cancellation_reason,
    )


def add_delivery_instructions_route(
    order_id: str,
    request: AddDeliveryInstructionsRequest,
) -> DeliveryInstructionsResponse:
    """POST /orders/{order_id}/delivery-instructions - specify drop-off preferences, gate codes, and delivery notes."""
    order = order_service.add_delivery_instructions(
        order_id,
        request.delivery_notes,
        request.dropoff_preference,
        request.gate_code,
    )
    return DeliveryInstructionsResponse.from_order(
        order,
        request.delivery_notes,
        request.dropoff_preference,
        request.gate_code,
    )
