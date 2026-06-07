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

### GET /orders/{order_id}/status

Returns the current lifecycle status and the next client action for the order.

Response fields:

- `status`: current order state such as `created`, `paid`, `fulfilled`, or `cancelled`.
- `next_action`: recommended next step for the client, such as `collect_payment` or `fulfill_order`.

### GET /orders?customer_id={customer_id}

Lists all orders for a customer account.

Query fields:

- `customer_id`: customer whose order history should be returned.

Response fields:

- `customer_id`: customer identifier used for the lookup.
- `orders`: list of order summaries for that customer.
- `total_count`: number of orders returned.

### POST /orders/{order_id}/pay

Marks a checkout order as paid after payment authorization succeeds.

Request fields:

- `payment_reference`: payment processor reference for the successful charge.

Response fields:

- `status`: updated order state, set to `paid`.
- `checkout_next_step`: client action after payment, currently `view_order`.

### POST /orders/{order_id}/fulfill

Marks a paid order as fulfilled after warehouse processing completes.

Request fields:

- `fulfillment_reference`: warehouse or shipment reference for the completed fulfillment.

Response fields:

- `status`: updated order state, set to `fulfilled`.
- `checkout_next_step`: client action after fulfillment, currently `view_order`.

### POST /orders/{order_id}/refund

Refunds a paid or fulfilled order after payment has been captured.

Request fields:

- `refund_reference`: payment processor refund reference.
- `refund_reason`: customer or support reason for the refund.

Response fields:

- `status`: updated order state, set to `refunded`.
- `checkout_next_step`: client action after refund, currently `view_order`.

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
`POST /orders/{order_id}/pay` flows through the route, service validation, and repository update layers.
`POST /orders/{order_id}/fulfill` flows through the route, service validation, and repository update layers.
`POST /orders/{order_id}/cancel` flows through the route, service validation, and repository update layers.
`GET /orders?customer_id={customer_id}` flows through the route, service lookup, and repository query layers.
`GET /orders/{order_id}/status` flows through the route, service lookup, and status response mapping layers.
`POST /orders/{order_id}/refund` flows through the route, service validation, and repository update layers.
