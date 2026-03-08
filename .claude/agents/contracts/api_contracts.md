# API Contracts — WifiOBD Site

## Contract Version: 2.0
## Status: ACTIVE
## Owner: backend-agent
## Consumers: frontend-agent, testing-agent, security-agent
## Updated: 2026-03-06

> Настоящий файл — канонический источник API-контрактов для всех агентов.
> frontend-agent читает его **перед** любыми запросами к API.
> testing-agent читает его для построения fixtures.
> backend-agent обновляет его после каждого изменения endpoint.

---

## 🌐 Global Contracts (применяются ко ВСЕМ эндпойнтам)

- Каждый endpoint — Pydantic `RequestSchema` + `ResponseSchema`
- Все ответы содержат заголовок `request_id: UUID` для трейсинга
- Списки: cursor-based pagination `{ items[], next_cursor, total }`
- Аутентификация: Bearer JWT в `Authorization` заголовке (webhooks и public endpoints — исключения)
- Формат ошибки: `{ detail: str, code: str, request_id: UUID }`
- HTTP 422 — Pydantic validation, 401 — unauthenticated, 403 — unauthorized
- **apiBase** в frontend = `/api/v1` — пути в composables начинаются с `/` (например, `/products`)

---

## 1. Auth API

### POST /api/v1/auth/register
Request: `{ email: str, password: str, name: str }`
Response: `{ user_id: UUID, email: str, name: str }`
- password — argon2 до сохранения
- дубликат email → 409 Conflict
- Celery: `notifications.send_welcome_email.delay(user_id)`

### POST /api/v1/auth/login
Request: `{ email: str, password: str }`
Response: `{ access_token: str, refresh_token: str, token_type: "bearer", user: UserResponse }`
- `access_token` TTL = 15 min (JWT)
- `refresh_token` TTL = 7 days, httpOnly cookie + body
- 5 неудачных попыток → 429 (slowapi)
- **MUST** вернуть полный `UserResponse` в поле `user`

### POST /api/v1/auth/refresh
Request: refresh_token (cookie или body)
Response: `{ access_token: str }`
- ротация рефреш токена при каждом использовании
- устаревшие токены → Redis blacklist `auth:blacklist:{jti}`

### POST /api/v1/auth/logout
Auth: Bearer
Response: `{ ok: true }`
- оба токена в Redis blacklist

---

## 2. Users API

UserResponse schema:
```
{ id: UUID, email: str, name: str, phone?: str,
  role: "customer"|"manager"|"admin", created_at: datetime }
```

### GET /api/v1/users/me
Auth: Bearer
Response: UserResponse
- PD-поля (phone, email) возвращаются расшифрованными (Fernet)

### PATCH /api/v1/users/me
Auth: Bearer
Request: `{ name?: str, phone?: str }` (email — отдельный flow)
Response: UserResponse
- phone: E.164 формат
- изменения в audit log

### DELETE /api/v1/users/me
Auth: Bearer
Response: `{ ok: true }`
- GDPR: анонимизация, не удаление
- email → `deleted_{id}@deleted.local`, name → `Deleted User`, phone → null
- отмена активных заказов, свобождение Redis резерваций корзины

### GET /api/v1/users/me/addresses
Auth: Bearer
Response: `{ items: DeliveryAddress[] }`
- DeliveryAddress: `{ id: UUID, name: str, recipient_name: str, recipient_phone: str, address_type: "home"|"pickup", full_address: str, city: str, postal_code: str|null, provider: "cdek"|"pochta"|"ozon"|"wb", pickup_point_code: str|null, is_default: bool, created_at: datetime, updated_at: datetime }`
- Sorted by is_default DESC, created_at DESC

### POST /api/v1/users/me/addresses
Auth: Bearer
Request: `{ name: str, recipient_name: str, recipient_phone: str, address_type: str, full_address: str, city: str, postal_code?: str, provider: str, pickup_point_code?: str, is_default: bool }`
Response: DeliveryAddress
- recipient_phone: E.164 format validation
- PII fields encrypted at rest

### PATCH /api/v1/users/me/addresses/{id}
Auth: Bearer
Request: partial DeliveryAddress fields
Response: DeliveryAddress
- 404 if address not found or not owned by user

### DELETE /api/v1/users/me/addresses/{id}
Auth: Bearer
Response: 204 No Content
- 404 if address not found or not owned by user

### POST /api/v1/users/me/addresses/{id}/set-default
Auth: Bearer
Response: DeliveryAddress
- Unsets is_default on all other user addresses
- 404 if address not found or not owned by user

---

## 3. Products API

Product schema:
```
{ id: UUID, slug: str, name: str, price_rub: Decimal,
  price_display: Decimal, currency: str, stock: int,
  images: Url[], category: Category }
```
Category schema:
```
{ id: UUID, slug: str, name: str, parent_id: UUID|null, product_count: int }
```

### GET /api/v1/products
Request: `category_slug?, price_min?, price_max?, page_cursor?, per_page?, currency?`
Response: `{ items: Product[], next_cursor: str|null, total: int }`
- `stock` — real-time Redis
- `currency` → CBR rate via `cbr_rates.get_rate(currency)`

### GET /api/v1/products/{slug}
Response: Product + `{ description: str, attributes: dict, related: Product[] }`
- view count: Redis `product:views:{id}`

### GET /api/v1/products/categories
Response: `{ items: Category[] }`
- кэш: Redis `categories:tree` TTL 1h

---

## 4. Cart API

CartItem schema:
```
{ product_id: UUID, slug: str, name: str, quantity: int,
  price_rub: Decimal, stock_available: int }
```

### GET /api/v1/cart
Auth: Bearer
Response: `{ cart_id: UUID, items: CartItem[], subtotal_rub: Decimal, reserved_until: datetime|null }`

### POST /api/v1/cart/add
Auth: Bearer
Request: `{ product_id: UUID, quantity: int }`
Response: updated Cart
- резерв: Redis `cart:reserve:{product_id}` TTL 30min (атомарно Lua)
- 409 если `stock_available < requested`
- 404 если товар не найден/неактивен

### DELETE /api/v1/cart/{product_id}
Auth: Bearer
Response: updated Cart
- снимает Redis резервацию для товара

### DELETE /api/v1/cart
Auth: Bearer
- снимает ВСЕ резервации корзины

---

## 5. Orders API

Order schema:
```
{ id: UUID, status: str, total_rub: Decimal,
  items: OrderItem[], delivery: DeliveryInfo, created_at: datetime }
```
Status FSM: `pending → awaiting_payment → paid → shipped → delivered`

### POST /api/v1/orders/
Auth: Bearer
Request:
```
{ delivery_type: "cdek_pvz"|"cdek_door",
  pvz_code?: str, address?: str,
  payment_method: "yoomoney" }
```
Response: `{ order_id: UUID, payment_url: str, expires_at: datetime }`
- `order_id` = idempotency key для YooMoney
- атомарное подтверждение резерваций

### GET /api/v1/orders/
Auth: Bearer
Response: `{ items: Order[], next_cursor, total }`

### GET /api/v1/orders/{order_id}
Auth: Bearer (свои) | Bearer+manager (любые)
Response: Order + payment history

---

## 6. Payments API

### POST /api/v1/payments/webhook/yoomoney
Request: YooMoney payload (`application/x-www-form-urlencoded`)
- HMAC-SHA256 проверка **до** любой обработки
- идемпотентность: повторный webhook → тот же результат
- успех: статус заказа → Celery: `notifications.send_order_confirmed.delay(order_id)`
- HTTP 200 всегда (даже если уже обработан)

---

## 7. Delivery API

PVZ schema:
```
{ code: str, address: str, name: str, lat: float, lon: float, work_hours: str }
```

### POST /api/v1/delivery/calculate
Auth: Bearer
Request: `{ city_code: str, tariff_code?: str, weight_kg: float, dimensions: { l, w, h } }`
Response: `{ cost_rub: Decimal, days_min: int, days_max: int, tariff_code: str, tariff_name: str }`
- кэш: Redis `cdek:calc:{city_code}:{tariff}:{weight}` TTL 1h

### GET /api/v1/delivery/pvz
Request: `city_code: str`
Response: `{ items: PVZ[] }`
- кэш: Redis `cdek:pvz:{city_code}` TTL 6h

### GET /api/v1/delivery/orders/{order_id}/c2c-shipment
Auth: Bearer JWT (role=admin)
Response 200: C2CShipmentResponse
```
{ provider: str, order_id: str, recipient_name: str, recipient_phone: str,
  pvz_code: str, pvz_address: str, declared_value: Decimal, weight_kg: float,
  comment: str, deeplink: str, instructions: list[str] }
```
Response 400: `{ detail: 'Provider is not C2C (ozon/wb)', code: 'INVALID_PROVIDER' }`
Response 404: `{ detail: 'Order not found', code: 'ORDER_NOT_FOUND' }`
- Работает только для `delivery_provider = 'ozon'` или `'wb'`
- Генерирует deeplink в мобильное приложение и пошаговую инструкцию для оператора

---

## 8. Blog API

BlogPost schema:
```
{ id: UUID, slug: str, title: str, excerpt: str, cover_url: Url,
  author: Author, tags: str[], published_at: datetime, reading_time_min: int }
```

### GET /api/v1/blog/posts
Request: `tag?, author_id?, page_cursor?, per_page?`
Response: `{ items: BlogPost[], next_cursor, total }`
- неаутентифицированный: только `status=published`

### GET /api/v1/blog/posts/{slug}
Response: BlogPost + `{ content_html: str, related: BlogPost[] }`
- `content_html` sanitised via `bleach` (no script/iframe/onclick)
- view count: Redis `blog:views:{id}`

### POST /api/v1/blog/posts
Auth: Bearer + role `manager`|`admin`
Request: `{ title: str, content_md: str, tags: str[], cover_url?: Url, status: "draft"|"published" }`
- slug: auto-generated, unique
- content_md → HTML → bleach

### PATCH /api/v1/blog/posts/{slug}
Auth: Bearer + role `manager`|`admin`|author
Request: partial BlogPost
- version counter, edit history

### DELETE /api/v1/blog/posts/{slug}
Auth: Bearer + role `admin`
- soft-delete (`status=deleted`)

---

## 9. Search API

SearchResult schema:
```
{ id: UUID, type: "product"|"blog", slug: str,
  title: str, excerpt: str, highlight: str }
```

### GET /api/v1/search
Request: `q: str, type?: "product"|"blog", page_cursor?, per_page?`
Response: `{ items: SearchResult[], next_cursor, total, took_ms: int }`
- Meilisearch
- p95 response < 500ms
- `took_ms` = Meilisearch processing time

---

## 10. IoT API

IoTRecord schema:
```
{ id: str, ts: datetime, type: str, payload: dict }
```
UserDevice schema:
```
{ id: UUID, device_id: str, name: str, type: str,
  last_seen: datetime, is_online: bool }
```

### POST /api/v1/iot/data
Auth: Bearer (device JWT)
Request: `{ device_id: str, type: str, payload: dict, ts: datetime }`
Response: `{ ok: true, stream_id: str }`
- `device_id` валидация через `UserDevice` (проверка владельца)
- XADD Redis Stream `iot:{device_id}` maxlen=10000

### GET /api/v1/iot/history/{device_id}
Auth: Bearer (владелец)
Request: `from: datetime, to: datetime, per_page?: int`
Response: `{ items: IoTRecord[], next_cursor, total }`
- TimescaleDB hypertable, max range = 30 days

### GET /api/v1/iot/devices
Auth: Bearer
Response: `{ items: UserDevice[] }`

### WebSocket /api/v1/iot/ws/{device_id}
Auth: `?token=<access_token>`

| Frame | Направление | Поля |
|---|---|---|
| connected | server → client | `{ type, device_id, last_state }` |
| telemetry | client → server | `{ type, payload, ts }` |
| ack | server → client | `{ type, ts }` |
| error | server → client | `{ type, code, message }` |
| update | server → all clients | `{ type, device_id, payload, ts }` |

- без аутентификации / чужой device → close 1008 (Policy Violation)
- отключение: чистить Redis `iot:ws:connections:{device_id}`

---

## 11. Admin API

> Все `/admin/*` маршруты — `require_role("admin")`.
> Для `/admin/orders` и `/admin/stats` — также `require_role("manager")`.

### GET /api/v1/admin/users
Auth: Bearer+admin
Request: `search?, role?, page?, per_page?`
Response: `{ items: UserResponse[], total: int }`

### PATCH /api/v1/admin/users/{user_id}
Auth: Bearer+admin
Request: `{ role?: str, is_blocked?: bool }`
- админ не может изменить свою роль / заблокировать себя
- audit log: `changed_by: admin_user_id`

### GET /api/v1/admin/orders
Auth: Bearer+manager|admin
Request: `status?, date_from?, date_to?, page_cursor?, per_page?`
Response: `{ items: Order[], next_cursor, total, stats: { total_count, total_revenue_rub } }`

### PATCH /api/v1/admin/orders/{order_id}
Auth: Bearer+manager|admin
Request: `{ status?: str, tracking_number?: str }`
- status transitions validated (FSM)
- on `shipped`: Celery `notifications.send_shipping_update.delay(order_id)`

### GET /api/v1/admin/stats
Auth: Bearer+admin
Response: `{ revenue_rub: Decimal, orders_count: int, users_count: int, period: str }`
- кэш: Redis `admin:stats:{period}` TTL 5min

### POST /api/v1/media/upload
Auth: Bearer
Request: `multipart/form-data` (file, context, alt)
Response: `{ url: str, width: int, height: int }`

---

## 12. Contracts Change Policy

- **Breaking change** (remove/rename field, change type) → bump major version, notify ALL consumers
- **Non-breaking** (новые optional поля) → bump minor version, commit message
- **Consumers** (`frontend-agent`, `testing-agent`) ОБЯЗАНЫ обновить свои schemas при изменении версии
- Обратная совместимость минимум 1 minor версию
