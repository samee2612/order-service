# Changelog

## [PR #26] - 2026-11-19
### Add POST /orders/{order_id}/packaging endpoint for sustainable options by @samee2612
- **Category**: API, Service Logic, Validation
- **Summary**: Added functionality to configure packaging options for orders, including validation for packaging types and order status.
- **Changed Files**: `backend/routes/orders.py`, `backend/schemas/orders.py`, `backend/services/order_service.py`, `tests/test_order_flow.py`

All notable changes merged via MergeFlow AI are documented in this file.

## [PR #22] - 2026-10-18
### Add POST /orders/{order_id}/cancel endpoint for order cancellation by @samee2612
- **Category**: API, Service Logic
- **Summary**: Added a new API endpoint and associated service logic for cancelling orders.
- **Changed Files**: `backend/routes/orders.py`, `backend/schemas/orders.py`, `tests/test_order_flow.py`
