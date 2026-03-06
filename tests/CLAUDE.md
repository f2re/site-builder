# tests/CLAUDE.md — testing-agent

> Агент читает этот файл при работе в директории `tests/`.
> Глобальные правила проекта, стек, DoD и граф фаз: [../CLAUDE.md](../CLAUDE.md)
> Задачи: [../.claude/agents/tasks/](../.claude/agents/tasks/)
> Отчёты: [../.claude/agents/reports/testing/](../.claude/agents/reports/testing/)

---

## 🔄 Рабочий цикл (ОБЯЗАТЕЛЕН — без исключений)

### ФАЗА 1 — PLAN [максимальный reasoning]
НЕ ПИШИ КОД. Выполни:
1. Прочитай `../CLAUDE.md` → проверь DoD задачи
2. Прочитай исходные файлы, которые нужно протестировать
3. Составь план тестов в 5–10 шагов
4. Опиши стратегию покрытия: какие кейсы критичны

### ФАЗА 2 — IMPLEMENT
- Пиши тесты строго по плану
- Если файл правился 3+ раза — СТОП, пересмотри подход

### ФАЗА 3 — VERIFY [максимальный reasoning]
```bash
pytest tests/unit/ -v --cov=app --cov-report=term-missing
pytest tests/integration/ -v
```

### ФАЗА 4 — FIX
- Исправляй строго по ошибкам из Фазы 3
- Повторяй до полного прохождения DoD

---

You write comprehensive tests for the FastAPI e-commerce platform, including WebSocket/IoT layer and load testing.

---

## 📁 Test File Structure

```
tests/
  unit/
    api/           test_products.py, test_orders.py, test_cart.py
    blog/          test_blog_posts.py
    integrations/  test_cdek.py, test_yoomoney.py, test_cbr_rates.py
    iot/           test_iot_ws.py, test_redis_streams.py
    auth/          test_auth.py, test_jwt.py
  integration/
    test_orders_flow.py       # cart → order → payment webhook → status
    test_iot_pipeline.py      # device connect → publish → TimescaleDB → query
    test_cbr_pipeline.py      # Celery beat → CBR → Redis cache → product price
  load/
    locustfile.py             # catalog + checkout scenarios
    locust_iot.py             # IoT-specific load scenario
  conftest.py                 # shared fixtures, test DB setup
```

**FORBIDDEN:** Creating test files outside `tests/`.

---

## 📊 Coverage Targets

| Layer | Target |
|---|---|
| `app/services/` | > 80% |
| `app/api/` | > 70% |
| `app/integrations/` | > 75% |
| `app/tasks/` | > 60% |
| IoT WebSocket handlers | > 70% |

---

## 📜 Core Test Contracts

- Unit tests: MUST mock ALL external services (CDEK, YooMoney, CBR, Redis) via `respx` or `unittest.mock`
- Integration tests: MUST use `fakeredis[lua]>=2.20.0` in `conftest.py`
- Integration tests: async `TestClient` + dedicated test PostgreSQL DB (`TEST_DATABASE_URL`)
- Every payment webhook handler MUST have idempotency test
- Every inventory operation MUST have concurrent-access / race condition test
- ALL tests MUST be deterministic — no `time.sleep()`, use `freezegun` for datetime mocking
- Database: SQLite in-memory or `test.db` for unit tests (JSON instead of JSONB)

---

## 🔌 WebSocket / IoT Test Contract

### Unit Tests (`tests/unit/iot/test_iot_ws.py`)
MUST cover 8 scenarios:
1. Connect with valid JWT via `?token=` → 200 + initial state
2. Connect without token → WebSocketDisconnect code 1008
3. Connect with expired JWT → code 1008
4. Connect with valid JWT but wrong `device_id` (not owned) → code 1008
5. Send IoT payload → validates Pydantic schema → published to Redis Stream
6. Send invalid payload → error frame, connection stays alive
7. Graceful disconnect: server-side close → no connection leak
8. Concurrent connections: 2 clients same `device_id` → both receive broadcast

```python
from httpx import AsyncClient
from httpx_ws import aconnect_ws

async def test_ws_auth_required(client: AsyncClient):
    async with aconnect_ws("/api/v1/iot/ws/device-123", client) as ws:
        msg = await ws.receive()
        assert msg.type == "websocket.close"
        assert msg.data["code"] == 1008
```

### Integration Tests (`tests/integration/test_iot_pipeline.py`)
Full pipeline:
1. Device authenticates via POST `/api/v1/iot/data` (JWT)
2. Payload published to Redis Stream `iot:{device_id}`
3. Worker consumes → writes to TimescaleDB
4. Query via GET `/api/v1/iot/history/{device_id}?from=...&to=...`
5. Assert data matches original payload

MUST test: Redis Stream isolation per device_id, hypertable chunk creation, real-time WebSocket update after worker processing.

---

## 🚀 Locust Load Testing

### Acceptance Criteria

| Scenario | Users | RPS Target | p95 Latency | Error Rate |
|---|---|---|---|---|
| Catalog browsing | 100 | ≥ 200 | < 300ms | < 1% |
| Search (Meilisearch) | 50 | ≥ 100 | < 500ms | < 1% |
| Checkout flow | 20 | ≥ 20 | < 2000ms | < 2% |
| IoT telemetry | 200 | ≥ 500 | < 100ms | < 0.5% |

### `tests/load/locustfile.py` structure
```python
from locust import HttpUser, TaskSet, task, between
from locust.contrib.fasthttp import FastHttpUser

class CatalogTaskSet(TaskSet):
    @task(5)
    def browse_products(self): ...
    @task(3)
    def search_products(self): ...
    @task(2)
    def view_product(self): ...

class CheckoutTaskSet(TaskSet):
    def on_start(self): ...  # POST /auth/login → store JWT
    @task(3)
    def add_to_cart(self): ...
    @task(1)
    def create_order(self): ...

class CatalogUser(FastHttpUser):
    tasks = [CatalogTaskSet]
    wait_time = between(1, 3)
    host = "http://localhost:8000"
```

### Run headless
```bash
locust -f tests/load/locustfile.py --headless -u 100 -r 10 --run-time 60s \
  --html tests/load/report.html
```

---

## 🛡 System Integrity Check (Gatekeeper Task)

When orchestrator requests "Final Verification", MUST:

```bash
# 1. Alembic integrity
cd backend && alembic heads          # verify single head
cd backend && alembic check          # verify model sync

# 2. Dependencies
pip install -r backend/requirements.txt --quiet

# 3. Linting
cd backend && ruff check app/ && mypy app/ --ignore-missing-imports
cd frontend && npm run lint

# 4. Tests
pytest tests/ -x -v
```

If any check fails → report MUST start with `## Status: BLOCKED`.

---

## 📝 Report Template

Write to: `../.claude/agents/reports/testing/<task_id>.md`

```markdown
## Status: DONE | IN_PROGRESS | BLOCKED
## Completed:
- написаны unit тесты для cart/, auth/, products/
## Artifacts:
- tests/unit/api/test_cart.py
- tests/unit/auth/test_auth.py
- tests/integration/test_orders_flow.py
- tests/load/report.html
## Coverage:
| Module | Coverage |
|---|---|
| app/services/cart.py | 84% |
| app/api/v1/cart/ | 71% |
## Locust Results:
| Scenario | RPS | p95 | Errors |
|---|---|---|---|
| Catalog | 220 | 280ms | 0.4% |
## WebSocket Tests:
- 8/8 auth scenarios: ✅
## Contracts Verified:
- fakeredis[lua]: ✅ | freezegun: ✅ | idempotency: ✅
## Next:
- security-agent: audit после прохождения тестов
## Blockers:
- none
```
