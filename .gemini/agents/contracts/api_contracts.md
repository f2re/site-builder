# API Contracts — E-Commerce Platform

## Contract Version: 2.0
## Status: ACTIVE
## Owner: backend-agent
## Consumers: frontend-agent, testing-agent, security-agent
## Updated: 2026-02-26

---

## Global Contracts (apply to ALL endpoints)

- ALL endpoints MUST have Pydantic Request + Response schemas
- ALL responses MUST include `request_id: UUID` header for tracing
- ALL list endpoints MUST support cursor-based pagination: `{ items[], next_cursor, total }`
- Authentication: Bearer JWT in `Authorization` header (except webhooks and public endpoints)
- Error format: `{ detail: str, code: str, request_id: UUID }`
- HTTP 422 for validation errors (Pydantic), 401 for unauthenticated, 403 for unauthorized

---

## 1. Auth API

### POST /api/v1/auth/register
Request: `{ email: str, password: str, name: str }`
Response: `{ user_id: UUID, email: str, name: str }`
Contract: password MUST be hashed with argon2 before storage
Contract: duplicate email → 409 Conflict
Contract: emit Celery task `notifications.send_welcome_email.delay(user_id)`

### POST /api/v1/auth/login
Request: `{ email: str, password: str }`
Response: `{ access_token: str, token_type: "bearer" }`
Contract: `access_token` lifetime = 15 minutes (JWT)
Contract: `refresh_token` set as httpOnly cookie, lifetime = 7 days
Contract: failed login → 401, after 5 failures → 429 (rate-limited by slowapi)

### POST /api/v1/auth/refresh
Request: refresh_token cookie (automatic)
Response: `{ access_token: str }`
Contract: refresh token MUST be rotated on each use (old token invalidated)
Contract: invalidated tokens stored in Redis blacklist `auth:blacklist:{jti}` TTL = token remaining lifetime

### POST /api/v1/auth/logout
Auth: Bearer
Response: `{ ok: true }`
Contract: add both tokens to Redis blacklist

---

## 2. Users API

### GET /api/v1/users/me
Auth: Bearer
Response: `{ id: UUID, email: str, name: str, phone?: str, role: "user"|"manager"|"admin", created_at: datetime }`
Contract: PD fields (phone, email) returned decrypted (Fernet)

### PATCH /api/v1/users/me
Auth: Bearer
Request: `{ name?: str, phone?: str }` (email change requires separate flow)
Response: updated User schema
Contract: phone MUST be validated (E.164 format)
Contract: changes logged to audit log

### DELETE /api/v1/users/me
Auth: Bearer
Response: `{ ok: true }`
Contract: GDPR right-to-erasure — anonymise PD fields, do NOT hard-delete
Contract: anonymise: email → `deleted_{id}@deleted.local`, name → `Deleted User`, phone → null
Contract: cancel active orders, release Redis cart reservations

### GET /api/v1/users/privacy
Auth: Bearer
Response: Privacy policy document (JSON with sections)
Contract: public-facing, no auth required for GET

---

## 3. Products API

### GET /api/v1/products
Request: `category_slug?, price_min?, price_max?, page_cursor?, per_page?, currency?`
Response: `{ items: Product[], next_cursor: str|null, total: int }`
Product schema: `{ id: UUID, slug: str, name: str, price_rub: Decimal, price_display: Decimal, currency: str, stock: int, images: Url[], category: Category }`
Contract: `stock` MUST reflect real-time Redis value
Contract: if `currency` param provided → apply CBR rate via `cbr_rates.get_rate(currency)`

### GET /api/v1/products/{slug}
Response: Product schema + `{ description: str, attributes: dict, related: Product[] }`
Contract: view count incremented in Redis `product:views:{id}`

### GET /api/v1/products/categories
Response: `{ items: Category[] }`
Category schema: `{ id: UUID, slug: str, name: str, parent_id: UUID|null, product_count: int }`
Contract: cached in Redis `categories:tree` TTL 1h

---

## 4. Cart API

### GET /api/v1/cart
Auth: Bearer
Response: `{ cart_id: UUID, items: CartItem[], subtotal_rub: Decimal, reserved_until: datetime|null }`
CartItem schema: `{ product_id: UUID, slug: str, name: str, quantity: int, price_rub: Decimal, stock_available: int }`

### POST /api/v1/cart/add
Auth: Bearer
Request: `{ product_id: UUID, quantity: int }`
Response: `{ cart_id: UUID, items: CartItem[], subtotal_rub: Decimal }`
Contract: reserve stock in Redis `cart:reserve:{product_id}` TTL 30min
Contract: 409 if `stock_available < requested quantity`
Contract: 404 if product not found or inactive

### DELETE /api/v1/cart/{product_id}
Auth: Bearer
Response: updated Cart schema
Contract: release Redis stock reservation on item remove

### DELETE /api/v1/cart
Auth: Bearer (clear entire cart)
Contract: release ALL Redis reservations for this cart

---

## 5. Orders API

### POST /api/v1/orders/
Auth: Bearer
Request: `{ delivery_type: "cdek_pvz"|"cdek_door", pvz_code?: str, address?: str, payment_method: "yoomoney" }`
Response: `{ order_id: UUID, payment_url: str, expires_at: datetime }`
Contract: `order_id` MUST be idempotency key for YooMoney
Contract: stock reservation MUST be confirmed atomically
Contract: order status flow: `pending` → `awaiting_payment` → `paid` → `shipped` → `delivered`

### GET /api/v1/orders/
Auth: Bearer
Response: `{ items: Order[], next_cursor, total }`
Order schema: `{ id: UUID, status: str, total_rub: Decimal, items: OrderItem[], delivery: DeliveryInfo, created_at: datetime }`

### GET /api/v1/orders/{order_id}
Auth: Bearer (own orders) | Bearer+manager role (any order)
Response: full Order schema + payment history

---

## 6. Payments API

### POST /api/v1/payments/webhook/yoomoney
Request: YooMoney webhook payload (`application/x-www-form-urlencoded`)
Contract: MUST verify HMAC-SHA256 signature BEFORE any processing
Contract: idempotent — repeated webhooks with same `notification_type+operation_id` = same result
Contract: on success: update order status → release Redis reservation → trigger `notifications.send_order_confirmed.delay(order_id)`
Contract: HTTP 200 MUST be returned even if already processed (idempotency)

---

## 7. Delivery API

### POST /api/v1/delivery/calculate
Auth: Bearer
Request: `{ city_code: str, tariff_code?: str, weight_kg: float, dimensions: { l, w, h } }`
Response: `{ cost_rub: Decimal, days_min: int, days_max: int, tariff_code: str, tariff_name: str }`
Contract: result cached Redis `cdek:calc:{city_code}:{tariff}:{weight}` TTL 1h

### GET /api/v1/delivery/pvz
Request: `city_code: str`
Response: `{ items: PVZ[] }`
PVZ schema: `{ code: str, address: str, name: str, lat: float, lon: float, work_hours: str }`
Contract: PVZ list cached Redis `cdek:pvz:{city_code}` TTL 6h

---

## 8. Blog API

### GET /api/v1/blog/posts
Request: `tag?, author_id?, page_cursor?, per_page?`
Response: `{ items: BlogPost[], next_cursor, total }`
BlogPost schema: `{ id: UUID, slug: str, title: str, excerpt: str, cover_url: Url, author: Author, tags: str[], published_at: datetime, reading_time_min: int }`
Contract: only `status=published` posts returned to unauthenticated users

### GET /api/v1/blog/posts/{slug}
Response: BlogPost schema + `{ content_html: str, related: BlogPost[] }`
Contract: `content_html` MUST be sanitised via `bleach` (no script/iframe/onclick)
Contract: view count incremented in Redis `blog:views:{id}`

### POST /api/v1/blog/posts
Auth: Bearer + role `manager` or `admin`
Request: `{ title: str, content_md: str, tags: str[], cover_url?: Url, status: "draft"|"published" }`
Response: created BlogPost schema
Contract: `content_md` converted to HTML via markdown lib, then sanitised via bleach
Contract: slug auto-generated from title (slugify), must be unique

### PATCH /api/v1/blog/posts/{slug}
Auth: Bearer + role `manager` or `admin` or author
Request: partial BlogPost fields
Contract: update version counter, keep edit history in DB

### DELETE /api/v1/blog/posts/{slug}
Auth: Bearer + role `admin`
Contract: soft-delete (set `status=deleted`), not hard-delete

---

## 9. Search API

### GET /api/v1/search
Request: `q: str, type?: "product"|"blog", page_cursor?, per_page?`
Response: `{ items: SearchResult[], next_cursor, total, took_ms: int }`
SearchResult schema: `{ id: UUID, type: "product"|"blog", slug: str, title: str, excerpt: str, highlight: str }`
Contract: powered by Meilisearch index
Contract: response time MUST be < 500ms (p95)
Contract: `took_ms` = Meilisearch processing time (for monitoring)

---

## 10. IoT API

### POST /api/v1/iot/data
Auth: Bearer (device JWT)
Request: `{ device_id: str, type: str, payload: dict, ts: datetime }`
Response: `{ ok: true, stream_id: str }`
Contract: `device_id` validated against `UserDevice` table (owner check)
Contract: payload validated via Pydantic schema for each device `type`
Contract: published to Redis Stream `iot:{device_id}` (XADD, maxlen=10000)

### GET /api/v1/iot/history/{device_id}
Auth: Bearer (owner only)
Request: `from: datetime, to: datetime, per_page?: int`
Response: `{ items: IoTRecord[], next_cursor, total }`
IoTRecord schema: `{ id: str, ts: datetime, type: str, payload: dict }`
Contract: data sourced from TimescaleDB hypertable `iot_telemetry`
Contract: max time range = 30 days per query

### GET /api/v1/iot/devices
Auth: Bearer
Response: `{ items: UserDevice[] }`
UserDevice schema: `{ id: UUID, device_id: str, name: str, type: str, last_seen: datetime, is_online: bool }`

### WebSocket /api/v1/iot/ws/{device_id}
Auth: `?token=<access_token>` query param (validated on connect)
Protocol: JSON frames
Connect response: `{ type: "connected", device_id: str, last_state: dict|null }`
Incoming frame: `{ type: "telemetry", payload: dict, ts: datetime }`
Outgoing frame: `{ type: "ack", ts: datetime }` or `{ type: "error", code: str, message: str }`
Broadcast frame: `{ type: "update", device_id: str, payload: dict, ts: datetime }` (sent to all connections for same device)
Contract: unauthenticated connect → close with code 1008 (Policy Violation)
Contract: wrong `device_id` (not owned) → close with code 1008
Contract: expired token → close with code 1008
Contract: graceful disconnect MUST clean up Redis connection tracking `iot:ws:connections:{device_id}`

---

## 11. Admin API

### GET /api/v1/admin/users
Auth: Bearer + role `admin`
Request: `search?, role?, page?, per_page?`
Response: `{ items: UserResponse[], total: int, page: int, per_page: int }`
UserResponse schema: `{ id: UUID, email: str, full_name: str, role: str, is_active: bool, created_at: datetime }`

### GET /api/v1/admin/pages
Auth: Bearer + role `admin`
Request: `none`
Response: `PageRead[]`
Contract: Returns all static pages. Use WITHOUT trailing slash.

### POST /api/v1/media/upload
Auth: Bearer
Request: `multipart/form-data` (file, context, alt)
Response: `{ url: str, width: int, height: int }`
Contract: Direct upload to storage. (Replaces upload-url/confirm flow)

### PATCH /api/v1/admin/users/{user_id}
Auth: Bearer + role `admin`
Request: `{ role?: str, is_blocked?: bool }`
Contract: admin cannot change own role or block themselves
Contract: changes logged to audit log with `changed_by: admin_user_id`

### GET /api/v1/admin/orders
Auth: Bearer + role `manager` or `admin`
Request: `status?, date_from?, date_to?, page_cursor?, per_page?`
Response: `{ items: Order[], next_cursor, total, stats: { total_count, total_revenue_rub } }`

### PATCH /api/v1/admin/orders/{order_id}
Auth: Bearer + role `manager` or `admin`
Request: `{ status?: str, tracking_number?: str }`
Contract: status transitions validated (cannot skip from `pending` to `delivered`)
Contract: on status `shipped` → trigger `notifications.send_shipping_update.delay(order_id)`

### GET /api/v1/admin/stats
Auth: Bearer + role `admin`
Response: `{ revenue_rub: Decimal, orders_count: int, users_count: int, period: str }`
Contract: cached Redis `admin:stats:{period}` TTL 5min

---

## 12. Contracts Change Policy

- Version bump REQUIRED for any breaking change (remove/rename field, change type)
- Non-breaking additions (new optional fields) → minor version bump, notify consumers in commit message
- Consumers (`frontend-agent`, `testing-agent`) MUST be notified when version changes
- Backward compatibility MUST be maintained for at least 1 minor version
