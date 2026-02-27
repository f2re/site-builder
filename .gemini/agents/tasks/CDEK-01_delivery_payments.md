---
id: CDEK-01
status: TODO
agent: cdek-agent
stage: 3 (Доставка и оплата)
priority: HIGH
depends_on: [BE-03]
blocks: [FE-02]
---

# CDEK-01 — СДЭК v2 API и YooMoney интеграция

## Цель

Реализовать интеграции `cdek.py` и `yoomoney.py` в `backend/app/integrations/`.

## ⚠️ Перед началом

```bash
read_file backend/app/integrations/cdek.py       # может существовать
read_file backend/app/integrations/yoomoney.py   # может существовать
read_file backend/app/api/v1/delivery/           # проверить наличие
```

## СДЭК v2

### `backend/app/integrations/cdek.py`

```python
class CdekClient:
    # OAuth2 Bearer-токен → кэшировать в Redis: cdek:token, TTL = expires_in - 60
    async def get_token(self) -> str
    async def calculate_tariff(self, from_city: int, to_city: int,
                               packages: list[dict]) -> dict
    async def get_pickup_points(self, city_code: int) -> list[dict]
    async def create_order(self, order_data: dict) -> dict  # после PAID
    async def get_order_status(self, cdek_number: str) -> dict
```

**Retry:** `tenacity stop_after_attempt(3)`, `wait_exponential(min=1, max=10)`.
Никогда не логировать `CDEK_CLIENT_SECRET`.

### `backend/app/api/v1/delivery/router.py`

```
GET  /api/v1/delivery/calculate
     ?from_city_code=44&to_city_code=270&weight=500
     → { tariffs: [{code, name, price, days}] }

GET  /api/v1/delivery/pickup-points
     ?city_code=270
     → кэш Redis delivery:pvz:{city_code} TTL 6 часов
```

## YooMoney

### `backend/app/integrations/yoomoney.py`

```python
class YooMoneyClient:
    async def create_payment(
        self, amount: Decimal, order_id: int,
        return_url: str, description: str
    ) -> dict:  # { payment_id, confirmation_url }

    # HMAC проверка webhook — статический метод:
    @staticmethod
    def verify_webhook_signature(secret: str, body: bytes, signature: str) -> bool:
        expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
```

## Celery-таска для трекинга СДЭК

`backend/app/tasks/inventory.py` или отдельный файл:
```python
@celery_app.task(name="tasks.track_cdek_order")
def track_cdek_order(cdek_number: str, order_id: int):
    # Запрашивает статус, если изменился — обновляет Order.status
    # и запускает notify_order_status_changed
```

Celery Beat: запускать каждые 30 мин для заказов со статусом `SHIPPED`.

## Контракты

- OAuth токен СДЭК — только в Redis, никогда в БД или логах
- YooMoney HMAC — `compare_digest` (не `==`), timing-safe
- Все внешние HTTP через `httpx.AsyncClient` с таймаутом 30 сек
- Retry — `tenacity`, не голый `for i in range(3)`

## Критерии готовности

- [ ] `GET /delivery/calculate` — возвращает тарифы без токена в ответе
- [ ] `GET /delivery/pickup-points` — кэшируется в Redis
- [ ] YooMoney `create_payment` — возвращает `confirmation_url`
- [ ] `verify_webhook_signature` — тест с невалидной подписью → False
- [ ] CDEK-токен кэшируется, не запрашивается при каждом вызове

## Отчёт

`.gemini/agents/reports/cdek/CDEK-01.md`
