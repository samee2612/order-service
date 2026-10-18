from decimal import Decimal

from backend.routes.orders import add_delivery_instructions_route, add_priority_fulfillment_route, add_gift_wrap_route, add_tip_route, apply_discount_route, cancel_order_route, create_order_route, fulfill_order_route, get_order_invoice_route, get_order_route, get_order_status_route, get_order_tracking_route, list_orders_route, mark_order_paid_route, refund_order_route
from backend.schemas.orders import AddDeliveryInstructionsRequest, AddPriorityFulfillmentRequest, AddGiftWrapRequest, AddTipRequest, ApplyDiscountRequest, CancelOrderRequest, CreateOrderItem, CreateOrderRequest, FulfillOrderRequest, MarkOrderPaidRequest, RefundOrderRequest


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


def test_apply_discount_route_calculates_savings() -> None:
    order_res = create_order_route(
        CreateOrderRequest(
            customer_id="customer-discount",
            items=(CreateOrderItem(sku="sku-gadget", quantity=2, unit_price=Decimal("50.00")),),
            payment_method_id="pm_card",
            shipping_address_id="addr_disc",
        )
    )
    # Total is 100.00. Apply SAVE10 (10% off) -> 10.00 off, discounted total 90.00
    response = apply_discount_route(
        order_res.order_id,
        ApplyDiscountRequest(coupon_code="SAVE10"),
    )
    assert response.order_id == order_res.order_id
    assert response.coupon_code == "SAVE10"
    assert response.discount_percentage == 10
    assert response.discount_amount == "10.00"
    assert response.original_total == "100.00"
    assert response.discounted_total == "90.00"
    assert response.applied is True


def test_add_tip_route_updates_total() -> None:
    order_res = create_order_route(
        CreateOrderRequest(
            customer_id="customer-tip",
            items=(CreateOrderItem(sku="sku-lunch", quantity=1, unit_price=Decimal("40.00")),),
            payment_method_id="pm_card",
            shipping_address_id="addr_tip",
        )
    )
    response = add_tip_route(
        order_res.order_id,
        AddTipRequest(tip_amount=Decimal("5.00"), tip_note="Great service!"),
    )
    assert response.order_id == order_res.order_id
    assert response.tip_amount == "5.00"
    assert response.tip_note == "Great service!"
    assert response.updated_total_amount == "45.00"


def test_cancel_order_route_cancels_pending_order() -> None:
    order_res = create_order_route(
        CreateOrderRequest(
            customer_id="customer-cancel",
            items=(CreateOrderItem(sku="sku-watch", quantity=1, unit_price=Decimal("150.00")),),
            payment_method_id="pm_card",
            shipping_address_id="addr_cancel",
        )
    )
    response = cancel_order_route(
        order_res.order_id,
        CancelOrderRequest(cancellation_reason="Customer requested cancellation before shipment"),
    )
    assert response.order_id == order_res.order_id
    assert response.customer_id == "customer-cancel"
    assert response.status == "cancelled"
    assert response.cancellation_reason == "Customer requested cancellation before shipment"


def test_add_delivery_instructions_route_updates_instructions() -> None:
    order_res = create_order_route(
        CreateOrderRequest(
            customer_id="customer-gate",
            items=(CreateOrderItem(sku="sku-shoes", quantity=1, unit_price=Decimal("89.99")),),
            payment_method_id="pm_card",
            shipping_address_id="addr_apt",
        )
    )
    response = add_delivery_instructions_route(
        order_res.order_id,
        AddDeliveryInstructionsRequest(
            delivery_notes="Please leave at side door behind gate",
            dropoff_preference="porch",
            gate_code="#4321",
        ),
    )
    assert response.order_id == order_res.order_id
    assert response.customer_id == "customer-gate"
    assert response.delivery_notes == "Please leave at side door behind gate"
    assert response.dropoff_preference == "porch"
    assert response.gate_code == "#4321"


def test_add_priority_fulfillment_route_updates_priority() -> None:
    order_res = create_order_route(
        CreateOrderRequest(
            customer_id="customer-rush",
            items=(CreateOrderItem(sku="sku-laptop", quantity=1, unit_price=Decimal("1299.00")),),
            payment_method_id="pm_corp_card",
            shipping_address_id="addr_office",
        )
    )
    response = add_priority_fulfillment_route(
        order_res.order_id,
        AddPriorityFulfillmentRequest(
            priority_level="urgent",
            rush_reason="Executive traveling tomorrow morning",
        ),
    )
    assert response.order_id == order_res.order_id
    assert response.customer_id == "customer-rush"
    assert response.status == "created"
    assert response.priority_level == "urgent"
    assert response.rush_reason == "Executive traveling tomorrow morning"

