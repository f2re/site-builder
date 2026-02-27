---
id: QA-01
status: TODO
agent: testing-agent
stage: 10 (Тестирование)
priority: MEDIUM
depends_on: [BE-01, BE-02, BE-03, BE-04, BE-05]
blocks: []
---

# QA-01 — Тесты (pytest + Locust + Lighthouse CI)

## Цель

Достичь покрытия: сервисный слой > 80%, API > 70%. Нагрузочный тест checkout и IoT.

## ⚠️ Перед началом

```bash
list_directory backend/tests/
read_file backend/tests/conftest.py
```

## Unit-тесты (pytest)

### `tests/unit/products/test_product_service.py`
- `test_get_product_by_slug_found`
- `test_get_product_by_slug_not_found` → 404
- `test_reserve_stock_success` — Lua-скрипт, mock Redis
- `test_reserve_stock_insufficient` → HTTPException 409
- `test_cursor_pagination` — правильный next_cursor

### `tests/unit/orders/test_order_service.py`
- `test_create_order_success`
- `test_create_order_no_stock` → HTTPException 409
- `test_yoomoney_webhook_valid_hmac`
- `test_yoomoney_webhook_invalid_hmac` → 400
- `test_yoomoney_webhook_idempotent` — повторный вызов не дублирует

### `tests/unit/blog/test_blog_service.py`
- `test_get_post_by_slug`
- `test_bleach_sanitization` — `<script>` удаляется
- `test_reading_time_calculation`
- `test_comment_email_encrypted` — email не хранится plaintext

### `tests/unit/iot/test_iot_service.py`
- `test_post_data_adds_to_redis_stream`
- `test_device_ownership_check` — чужое устройство → 403
- `test_time_bucket_query` — SQL содержит `time_bucket`

## Интеграционные тесты

### `tests/integration/test_checkout_flow.py`
Полный флоу через `AsyncClient`:
1. Register → Login → JWT
2. GET /products/{slug} → вариант
3. POST /cart/items
4. POST /orders → Order(PENDING) + confirmation_url
5. POST /payments/webhook (HMAC подписан)
6. GET /orders/{id} → статус PAID

### `tests/integration/test_iot_websocket.py`
```python
async def test_iot_live_data():
    async with AsyncClient(...) as client:
        token = await login(client)
        async with websockets.connect(f"/ws/iot/{device_id}?token={token}") as ws:
            await client.post("/api/v1/iot/data", json={...})
            msg = await asyncio.wait_for(ws.recv(), timeout=3.0)
            assert json.loads(msg)["rpm"] == expected
```

## Нагрузочные тесты (Locust)

`tests/load/locustfile.py`:
```python
class ShopUser(HttpUser):
    @task(3)
    def browse_catalog(self): ...    # GET /api/v1/products

    @task(2)
    def view_product(self): ...      # GET /api/v1/products/{slug}

    @task(1)
    def checkout(self): ...          # POST /orders + webhook

class IotDevice(HttpUser):
    @task
    def send_telemetry(self): ...    # POST /api/v1/iot/data × 1/sек
```

Целевые показатели при 100 RPS: p95 < 200ms, p99 < 500ms, error rate < 0.1%.

## Lighthouse CI

`lighthouserc.json`:
```json
{
  "ci": {
    "collect": { "url": ["/", "/products", "/blog"] },
    "assert": {
      "assertions": {
        "categories:seo": ["warn", { "minScore": 1 }],
        "categories:performance": ["warn", { "minScore": 0.9 }]
      }
    }
  }
}
```

В `.gitlab-ci.yml` — `allow_failure: true`, результат сохраняется артефактом.

## Критерии готовности

- [ ] `pytest backend/tests/ -v --cov=app --cov-report=term-missing`
  - services/ > 80%
  - api/ > 70%
- [ ] Все edge-cases webhook проходят
- [ ] IoT WebSocket тест < 3 сек end-to-end
- [ ] Locust: 100 RPS без деградации
- [ ] Lighthouse артефакт появляется в GitLab CI

## Отчёт

`.gemini/agents/reports/testing/QA-01.md`
