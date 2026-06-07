from decimal import Decimal

from backend.routes.orders import cancel_order_route, create_order_route, fulfill_order_route, get_order_route, get_order_status_route, get_order_tracking_route, list_orders_route, mark_order_paid_route, refund_order_route
from backend.schemas.orders import CancelOrderRequest, CreateOrderItem, CreateOrderRequest, FulfillOrderRequest, MarkOrderPaidRequest, RefundOrderRequest


def test_create_order_route_returns_checkout_response() -> None:
    request = CreateOrderRequest(
        customer_id="customer-123",
        items=(
            CreateOrderItem(sku="sku-basic-plan", quantity=2, unit_price=Decimal("19.99")),
            CreateOrderItem(sku="sku-support-addon", quantity=1, unit_price=Decimal("9.99")),
        ),
        payment_method_id="pm_card_visa",
        shipping_address_id="addr_home",
    )

    response = create_order_route(request)

    assert response.order_id == "order_customer_123_001"
    assert response.customer_id == "customer-123"
    assert response.status == "created"
    assert response.item_count == 3
    assert response.total_amount == "49.97"
    assert response.checkout_next_step == "collect_payment"


def test_get_order_route_returns_saved_order() -> None:
    response = get_order_route("order_customer_123_001")

    assert response.order_id == "order_customer_123_001"
    assert response.status == "created"


def test_get_order_status_route_returns_next_action() -> None:
    response = get_order_status_route("order_customer_123_001")

    assert response.order_id == "order_customer_123_001"
    assert response.status == "created"
    assert response.next_action == "collect_payment"


def test_list_orders_route_returns_customer_orders() -> None:
    response = list_orders_route("customer-123")

    assert response.customer_id == "customer-123"
    assert response.total_count == 1
    assert response.orders[0].order_id == "order_customer_123_001"
    assert response.orders[0].status == "created"


def test_mark_order_paid_route_updates_order_status() -> None:
    response = mark_order_paid_route(
        "order_customer_123_001",
        MarkOrderPaidRequest(payment_reference="pay_test_123"),
    )

    assert response.order_id == "order_customer_123_001"
    assert response.status == "paid"
    assert response.checkout_next_step == "view_order"


def test_fulfill_order_route_updates_order_status() -> None:
    response = fulfill_order_route(
        "order_customer_123_001",
        FulfillOrderRequest(fulfillment_reference="fulfill_test_123"),
    )

    assert response.order_id == "order_customer_123_001"
    assert response.status == "fulfilled"
    assert response.checkout_next_step == "view_order"


def test_refund_order_route_updates_order_status() -> None:
    response = refund_order_route(
        "order_customer_123_001",
        RefundOrderRequest(
            refund_reference="refund_test_123",
            refund_reason="customer requested refund after delivery",
        ),
    )

    assert response.order_id == "order_customer_123_001"
    assert response.status == "refunded"
    assert response.checkout_next_step == "view_order"


def test_get_order_tracking_route_returns_tracking_details() -> None:
    mark_order_paid_route(
        "order_customer_123_001",
        MarkOrderPaidRequest(payment_reference="pay_tracking_123"),
    )
    fulfill_order_route(
        "order_customer_123_001",
        FulfillOrderRequest(fulfillment_reference="fulfill_tracking_123"),
    )

    response = get_order_tracking_route("order_customer_123_001")

    assert response.order_id == "order_customer_123_001"
    assert response.status == "fulfilled"
    assert response.carrier == "Acme Logistics"
    assert response.tracking_number.startswith("TRK-")
