# Order Service

Order creation, checkout, fulfillment, and order-status APIs for AcmeFlow Technologies.

## API Flow Under Test

This branch adds a realistic order creation flow for validating MergeFlow documentation generation.

### POST /orders

Creates a checkout order for a customer.

Request fields:

- `customer_id`: customer placing the order.
- `items`: tuple of order line items with `sku`, `quantity`, and `unit_price`.
- `payment_method_id`: payment method selected during checkout.
- `shipping_address_id`: delivery address selected during checkout.

Response fields:

- `order_id`: generated order identifier.
- `customer_id`: customer that owns the order.
- `status`: initial order state, currently `created`.
- `item_count`: total quantity across all order line items.
- `total_amount`: calculated order total as a currency string.
- `checkout_next_step`: next client action after order creation.

### GET /orders/{order_id}

Returns the saved order summary from the repository.

### POST /orders/{order_id}/cancel

Cancels an order that has not yet been fulfilled.

Request fields:

- `cancellation_reason`: customer or support reason for cancelling the order.

Response fields:

- `status`: updated order state, set to `cancelled`.
- `checkout_next_step`: client action after cancellation, currently `view_order`.

## Code Path

`backend/routes/orders.py` receives request objects and returns response objects.
`backend/services/order_service.py` validates checkout inputs, calculates totals, and creates the domain order.
`backend/repositories/order_repository.py` persists and retrieves orders.
`backend/models/order.py` defines the domain model.
`backend/schemas/orders.py` defines request and response shapes.
`POST /orders/{order_id}/cancel` flows through the route, service validation, and repository update layers.
