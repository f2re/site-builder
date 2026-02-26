# API Contracts — E-Commerce Platform

## Contract Version: 1.0
## Status: ACTIVE
## Owner: backend-agent
## Consumers: frontend-agent, testing-agent

---

## Products API

### GET /api/v1/products
Request: query params — category_slug?, price_min?, price_max?, page_cursor?, per_page?
Response: { items: Product[], next_cursor: str|null, total: int }
Product schema: { id, slug, name, price: Decimal, currency, stock: int, images: Url[] }
Contract: stock MUST reflect real-time Redis value
Contract: price MUST apply currency rate if non-RUB

### POST /api/v1/cart/add
Request: { product_id: UUID, quantity: int }
Response: { cart_id, items: CartItem[], subtotal: Decimal }
Contract: MUST reserve stock in Redis on add (TTL 30min)
Contract: MUST return 409 if stock < requested quantity

### POST /api/v1/orders/
Request: { delivery_type: "cdek_pvz"|"cdek_door", pvz_code?: str, address?: str, payment_method: "yoomoney" }
Response: { order_id: UUID, payment_url: str, expires_at: datetime }
Contract: order_id MUST be idempotency key for YooMoney
Contract: stock reservation MUST be confirmed (not just cached)

### POST /api/v1/payments/webhook/yoomoney
Request: YooMoney webhook payload (application/x-www-form-urlencoded)
Contract: MUST verify HMAC-SHA256 signature BEFORE processing
Contract: MUST be idempotent (repeated webhooks = same result)
Contract: On success → update order status → release Redis reservation → trigger Celery notify task
