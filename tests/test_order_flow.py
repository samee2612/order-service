from decimal import Decimal

from backend.routes.orders import add_gift_wrap_route, cancel_order_route, create_order_route, fulfill_order_route, get_order_invoice_route, get_order_route, get_order_status_route, get_order_tracking_route, list_orders_route, mark_order_paid_route, refund_order_route
from backend.schemas.orders import AddGiftWrapRequest, CancelOrderRequest, CreateOrderItem, CreateOrderRequest, FulfillOrderRequest, MarkOrderPaidRequest, RefundOrderRequest


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

def test_get_order_invoice_route_returns_invoice_details() -> None:
    order_res = create_order_route(
        CreateOrderRequest(
            customer_id="customer-inv",
            items=(CreateOrderItem(sku="sku-inv", quantity=3, unit_price=Decimal("10.00")),),
            payment_method_id="pm_card",
            shipping_address_id="addr_inv",
        )
    )
    mark_order_paid_route(
        order_res.order_id,
        MarkOrderPaidRequest(payment_reference="pay_invoice_123"),
    )
    response = get_order_invoice_route(order_res.order_id)
    assert response.order_id == order_res.order_id
    assert response.status == "paid"
    assert response.invoice_id.startswith("INV-")
    assert response.line_item_count == 3


def test_add_gift_wrap_route_returns_confirmed_gift_options() -> None:
    order_res = create_order_route(
        CreateOrderRequest(
            customer_id="customer-gift",
            items=(CreateOrderItem(sku="sku-gift", quantity=1, unit_price=Decimal("25.00")),),
            payment_method_id="pm_card",
            shipping_address_id="addr_gift",
        )
    )
    response = add_gift_wrap_route(
        order_res.order_id,
        AddGiftWrapRequest(
            wrap_style="premium",
            gift_message="Happy Birthday! Enjoy the gift.",
            recipient_name="Alice Smith",
        ),
    )
    assert response.order_id == order_res.order_id
    assert response.wrap_style == "premium"
    assert response.gift_wrap_fee == "6.99"
    assert response.recipient_name == "Alice Smith"
