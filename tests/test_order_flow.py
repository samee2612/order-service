from decimal import Decimal

from backend.routes.orders import create_order_route, get_order_route
from backend.schemas.orders import CreateOrderItem, CreateOrderRequest


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
