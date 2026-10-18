from __future__ import annotations

from decimal import Decimal

from backend.models.order import Order, OrderItem
from backend.repositories.order_repository import InMemoryOrderRepository
from backend.schemas.orders import CreateOrderRequest


class OrderValidationError(ValueError):
    pass


class OrderService:
    def __init__(self, repository: InMemoryOrderRepository) -> None:
        self.repository = repository

    def create_order(self, request: CreateOrderRequest) -> Order:
        self._validate_create_request(request)
        items = tuple(
            OrderItem(sku=item.sku, quantity=item.quantity, unit_price=item.unit_price)
            for item in request.items
        )
        total_amount = sum((item.subtotal for item in items), Decimal("0.00"))
        order = Order(
            order_id=self._build_order_id(request.customer_id),
            customer_id=request.customer_id,
            items=items,
            status="created",
            total_amount=total_amount,
        )
        return self.repository.save(order)

    def get_order(self, order_id: str) -> Order:
        return self.repository.get(order_id)

    def get_order_status(self, order_id: str) -> Order:
        return self.repository.get(order_id)

    def get_order_invoice(self, order_id: str) -> tuple[Order, str, str]:
        order = self.repository.get(order_id)
        if order.status not in ("paid", "fulfilled", "refunded"):
            raise OrderValidationError("invoice is available only for paid, fulfilled, or refunded orders")
        invoice_id = f"INV-{order.order_id.upper().replace('_', '-')}"
        issued_at = "2026-06-07"
        return order, invoice_id, issued_at
    def get_order_tracking(self, order_id: str) -> tuple[Order, str, str, str]:
        order = self.repository.get(order_id)
        if order.status not in ("fulfilled", "refunded"):
            raise OrderValidationError("tracking is available only for fulfilled or refunded orders")
        tracking_number = f"TRK-{order.order_id.upper().replace('_', '-')}"
        carrier = "Acme Logistics"
        estimated_delivery = "2026-06-10"
        return order, tracking_number, carrier, estimated_delivery

    def list_orders_for_customer(self, customer_id: str) -> tuple[Order, ...]:
        if not customer_id.strip():
            raise OrderValidationError("customer_id is required")
        return self.repository.list_by_customer(customer_id)

    def mark_order_paid(self, order_id: str, payment_reference: str) -> Order:
        if not payment_reference.strip():
            raise OrderValidationError("payment_reference is required")

        order = self.repository.get(order_id)
        if order.status == "cancelled":
            raise OrderValidationError("cancelled orders cannot be paid")
        if order.status == "fulfilled":
            raise OrderValidationError("fulfilled orders are already closed")
        if order.status == "paid":
            return order

        paid_order = Order(
            order_id=order.order_id,
            customer_id=order.customer_id,
            items=order.items,
            status="paid",
            total_amount=order.total_amount,
        )
        return self.repository.save(paid_order)

    def fulfill_order(self, order_id: str, fulfillment_reference: str) -> Order:
        if not fulfillment_reference.strip():
            raise OrderValidationError("fulfillment_reference is required")

        order = self.repository.get(order_id)
        if order.status != "paid":
            raise OrderValidationError("only paid orders can be fulfilled")
        if order.status == "fulfilled":
            return order

        fulfilled_order = Order(
            order_id=order.order_id,
            customer_id=order.customer_id,
            items=order.items,
            status="fulfilled",
            total_amount=order.total_amount,
        )
        return self.repository.save(fulfilled_order)


    def refund_order(self, order_id: str, refund_reference: str, refund_reason: str) -> Order:
        if not refund_reference.strip():
            raise OrderValidationError("refund_reference is required")
        if not refund_reason.strip():
            raise OrderValidationError("refund_reason is required")

        order = self.repository.get(order_id)
        if order.status not in ("paid", "fulfilled"):
            raise OrderValidationError("only paid or fulfilled orders can be refunded")
        if order.status == "refunded":
            return order

        refunded_order = Order(
            order_id=order.order_id,
            customer_id=order.customer_id,
            items=order.items,
            status="refunded",
            total_amount=order.total_amount,
        )
        return self.repository.save(refunded_order)

    def expedite_order(self, order_id: str, shipping_speed: str, expedite_fee: Decimal) -> Order:
        valid_speeds = ("two_day", "overnight")
        if shipping_speed not in valid_speeds:
            raise OrderValidationError("shipping_speed must be two_day or overnight")
        if expedite_fee < Decimal("0.00"):
            raise OrderValidationError("expedite_fee cannot be negative")

        order = self.repository.get(order_id)
        if order.status != "paid":
            raise OrderValidationError("only paid orders can be expedited before fulfillment")

        return order

    def update_shipping_address(
        self,
        order_id: str,
        shipping_address_id: str,
        delivery_instructions: str = "",
    ) -> Order:
        if not shipping_address_id.strip():
            raise OrderValidationError("shipping_address_id is required")
        if len(delivery_instructions) > 250:
            raise OrderValidationError("delivery_instructions cannot exceed 250 characters")

        order = self.repository.get(order_id)
        if order.status not in ("created", "paid"):
            raise OrderValidationError(
                "shipping address can only be updated while order is in created or paid status"
            )

        return order

    def add_gift_wrap(
        self,
        order_id: str,
        wrap_style: str = "standard",
        gift_message: str = "",
        recipient_name: str = "",
    ) -> tuple[Order, Decimal]:
        valid_styles = {
            "standard": Decimal("3.99"),
            "festive": Decimal("4.99"),
            "premium": Decimal("6.99"),
        }
        if wrap_style not in valid_styles:
            raise OrderValidationError("wrap_style must be standard, festive, or premium")
        if len(gift_message) > 200:
            raise OrderValidationError("gift_message cannot exceed 200 characters")

        order = self.repository.get(order_id)
        if order.status not in ("created", "paid"):
            raise OrderValidationError("gift wrap can only be added while order is in created or paid status")

        return order, valid_styles[wrap_style]

    def apply_discount(
        self,
        order_id: str,
        coupon_code: str,
        referral_code: str = "",
    ) -> tuple[Order, int, Decimal, Decimal]:
        code = coupon_code.upper().strip()
        coupons = {
            "SAVE10": 10,
            "WELCOME15": 15,
            "VIP20": 20,
            "SUMMER25": 25,
        }
        if not code:
            raise OrderValidationError("coupon_code is required")
        if code not in coupons:
            raise OrderValidationError(f"invalid coupon_code: {coupon_code}")

        order = self.repository.get(order_id)
        if order.status not in ("created", "paid"):
            raise OrderValidationError("discount can only be applied while order is in created or paid status")

        discount_percentage = coupons[code]
        discount_amount = (order.total_amount * Decimal(discount_percentage) / Decimal(100)).quantize(Decimal("0.01"))
        discounted_total = max(Decimal("0.00"), order.total_amount - discount_amount)
        return order, discount_percentage, discount_amount, discounted_total

    def add_tip(
        self,
        order_id: str,
        tip_amount: Decimal,
        tip_note: str = "",
    ) -> tuple[Order, Decimal]:
        if tip_amount <= Decimal("0.00"):
            raise OrderValidationError("tip_amount must be greater than zero")
        if len(tip_note) > 150:
            raise OrderValidationError("tip_note cannot exceed 150 characters")

        order = self.repository.get(order_id)
        if order.status not in ("created", "paid"):
            raise OrderValidationError("tip can only be added while order is in created or paid status")

        updated_total = order.total_amount + tip_amount
        return order, updated_total

    def cancel_order(self, order_id: str, cancellation_reason: str) -> Order:
        if not cancellation_reason.strip():
            raise OrderValidationError("cancellation_reason is required")

        order = self.repository.get(order_id)
        if order.status == "cancelled":
            raise OrderValidationError("order is already cancelled")
        if order.status == "fulfilled":
            raise OrderValidationError("fulfilled orders cannot be cancelled")

        cancelled_order = Order(
            order_id=order.order_id,
            customer_id=order.customer_id,
            items=order.items,
            status="cancelled",
            total_amount=order.total_amount,
        )
        return self.repository.save(cancelled_order)

    def _validate_create_request(self, request: CreateOrderRequest) -> None:
        if not request.customer_id:
            raise OrderValidationError("customer_id is required")
        if not request.payment_method_id:
            raise OrderValidationError("payment_method_id is required")
        if not request.shipping_address_id:
            raise OrderValidationError("shipping_address_id is required")
        if not request.items:
            raise OrderValidationError("at least one order item is required")
        for item in request.items:
            if not item.sku:
                raise OrderValidationError("item sku is required")
            if item.quantity <= 0:
                raise OrderValidationError("item quantity must be greater than zero")
            if item.unit_price <= Decimal("0.00"):
                raise OrderValidationError("item unit_price must be greater than zero")

    def _build_order_id(self, customer_id: str) -> str:
        return f"order_{customer_id.lower().replace('-', '_')}_001"
