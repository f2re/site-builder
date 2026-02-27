---
id: BE-03
status: TODO
agent: backend-agent
stage: 3 (Корзина, заказы, платежи)
priority: HIGH
depends_on: [BE-01]
blocks: [FE-02]
---

# BE-03 — Корзина, заказы, YooMoney

## Цель

Реализовать полный checkout-флоу: корзина Redis → создание заказа → платёжная ссылка YooMoney → webhook → смена статуса.

## ⚠️ Перед началом

```bash
list_directory backend/app/api/v1/cart/
list_directory backend/app/api/v1/orders/
read_file backend/app/db/models/order.py   # модель уже есть
# Проверить наличие cart.py в models/
```

## Задачи

### 1. Модель корзины (`backend/app/db/models/cart.py`)

Если файл отсутствует — создать:

```python
class Cart(Base):
    __tablename__ = "cart"
    id: int, user_id: int | None (FK nullable), session_id: str | None
    created_at: datetime, updated_at: datetime
    # TTL-логика через Redis, PostgreSQL — только для авторизованных

class CartItem(Base):
    __tablename__ = "cart_item"
    id: int, cart_id: int, variant_id: int
    quantity: int  # CHECK quantity > 0
    reserved_until: datetime | None  # TTL резервирования
```

Гостевая корзина: **только Redis** `cart:guest:{session_id}` Hash, TTL 7 дней.
Авторизованная: Redis + синхронизация с PostgreSQL.

### 2. Cart Service & Redis

```python
# Redis Hash: cart:{user_id} → {variant_id: quantity}
# Lua-скрипт add_to_cart: ATOMICALLY increment + check stock reservation

class CartService:
    async def get_cart(self, user_id: int | None, session_id: str) -> CartResponse
    async def add_item(self, variant_id: int, qty: int, ...) -> CartResponse
    async def remove_item(self, variant_id: int, ...) -> CartResponse
    async def clear(self, ...) -> None
    async def merge_guest_cart(self, session_id: str, user_id: int) -> None
      # вызывать при логине
```

### 3. Orders

Чекаут-флоу строго по шагам:
1. Валидация остатков (Redis `stock:{variant_id}`)
2. Резервирование через Lua-скрипт (TTL 30 мин)
3. Расчёт доставки — делегировать `cdek-agent` (см. `BE-CDEK`)
4. Создание Order в БД (статус `PENDING`)
5. Создание платёжной ссылки YooMoney → вернуть `confirmation_url`
6. Освобождение резерва если платёж не прошёл за 30 мин (Celery Beat)

**Проверить `backend/app/db/models/order.py`** — должны быть все статусы:
```python
class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
```
Если не хватает — добавить и создать миграцию.

### 4. YooMoney webhook (`backend/app/api/v1/payments/`)

Если директория существует — проверить наличие всех 4 файлов.

```
POST /api/v1/payments/create
  → создаёт платёж, возвращает { confirmation_url, payment_id }

POST /api/v1/payments/webhook  (НЕ требует JWT, только HMAC)
  → идемпотентная обработка (Redis key payments:processed:{payment_id})
  → HMAC-SHA256 проверка ОБЯЗАТЕЛЬНА перед любой логикой
  → при success: Order.status = PAID, списание резерва, Celery notify
```

**HMAC проверка:**
```python
import hmac, hashlib
expected = hmac.new(
    settings.YOOMONEY_SECRET.encode(),
    request_body,
    hashlib.sha256
).hexdigest()
if not hmac.compare_digest(expected, received_signature):
    raise HTTPException(400)
```

### 5. Уведомления после PAID

Celery-таска `tasks/notifications.py`:
```python
@celery_app.task(name="tasks.notify_order_paid")
def notify_order_paid(order_id: int): ...
# Проверить наличие файла, создать если нет
```

## Контракты

- Резервирование: **Lua-скрипт**, не обычный DECR
- Webhook: HMAC проверяется ПЕРВЫМ, до любой бизнес-логики
- Idempotency: `payments:processed:{payment_id}` в Redis (SET NX)
- Нет логирования `payment_id` + `amount` в одной строке (152-ФЗ)
- Rate limiting: `slowapi` на `/payments/create` и `/checkout`

## Критерии готовности

- [ ] `alembic check` чисто (если cart.py создан)
- [ ] Добавление в корзину: атомарное через Lua
- [ ] Checkout создаёт Order(PENDING) + возвращает confirmation_url
- [ ] Webhook HMAC — невалидный подпись → 400, не выполнять логику
- [ ] Webhook идемпотентный — повторный вызов не дублирует
- [ ] Статус меняется PENDING → PAID после webhook
- [ ] Резерв снимается через Celery Beat если платёж не прошёл за 30 мин

## Отчёт

`.gemini/agents/reports/backend/BE-03.md`
