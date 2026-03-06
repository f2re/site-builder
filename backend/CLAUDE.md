# backend/CLAUDE.md — backend-agent

> Агент читает этот файл при работе в директории `backend/`.
> Глобальные правила проекта, стек, DoD и граф фаз: [../CLAUDE.md](../CLAUDE.md)
> Задачи: [../.claude/agents/tasks/](../.claude/agents/tasks/)
> Отчёты: [../.claude/agents/reports/backend/](../.claude/agents/reports/backend/)
> Контракты API: [../.claude/agents/contracts/api_contracts.md](../.claude/agents/contracts/api_contracts.md)

---

## 🔄 Рабочий цикл (ОБЯЗАТЕЛЕН — без исключений)

### ФАЗА 1 — PLAN [максимальный reasoning]
НЕ ПИШИ КОД. Выполни:
1. Прочитай `../CLAUDE.md` → проверь DoD задачи
2. Поиск по ключевым словам задачи в кодовой базе
3. Прочитай все затронутые файлы
4. Составь план в 5–10 нумерованных шагов
5. Опиши стратегию верификации: какие команды докажут готовность

### ФАЗА 2 — IMPLEMENT
- Пиши код строго по плану из Фазы 1
- Создавай тесты параллельно с кодом, не в конце
- Если файл правился 3+ раза — СТОП, пересмотри подход

### ФАЗА 3 — VERIFY [максимальный reasoning]
Выполни последовательно, дожди полного вывода:
```bash
cd backend && ruff check app/ --fix && ruff check app/
cd backend && mypy app/ --ignore-missing-imports
cd backend && alembic check && alembic heads
pytest tests/ -x -v
```

### ФАЗА 4 — FIX
- Исправляй строго по ошибкам из Фазы 3 (не угадывай)
- После каждого исправления → снова Фаза 3

---

You write production-grade **Python 3.12 + FastAPI** code for the WifiOBD Site e-commerce and IoT platform.
Architecture: **Clean Architecture · Repository Pattern · Feature-First · Design-by-Contract**.

> ⚠️ BEFORE ANY WORK: check `backend/app/api/v1/` and `backend/app/db/models/`
> to discover what already exists. NEVER overwrite existing code without explicit task instruction.

---

## ✅ Already Implemented (do not touch without a task)

### Core (`backend/app/core/`)
- `config.py` — Pydantic `BaseSettings`, all env vars ✅
- `security.py` — JWT (access + refresh), bcrypt/argon2 ✅
- `dependencies.py` — DI: db session, `current_user`, `require_role` ✅
- `exceptions.py` — global HTTP exception handlers ✅
- `logging.py` — structlog JSON logger ✅

### Database (`backend/app/db/`)
- `base.py` — `DeclarativeBase` ✅
- `session.py` — `AsyncSessionLocal`, `get_async_session` ✅
- `redis.py` — Redis connection pool ✅

### Models (`backend/app/db/models/`)
- `user.py`, `user_device.py`, `product.py`, `order.py` ✅
- `blog.py`, `notification.py`, `redirect.py` ✅
- `cart.py` ❌ MISSING — must create
- `telemetry.py` ❌ MISSING — TimescaleDB hypertable

### API (`backend/app/api/v1/`) — directories exist:
`auth/` `users/` `products/` `orders/` `cart/` `blog/` `delivery/` `iot/` `admin/` `media/`
Route aggregator: `router.py` ✅

---

## 🚧 Pending Work

| Domain | What is needed | Priority |
|---|---|---|
| `db/models/` | `cart.py`, `telemetry.py` — missing, must create | P1 |
| `auth/` | router, service, schemas — verify existence | P1 |
| `products/` | verify all 4 files, Meilisearch indexing | P1 |
| `cart/` | Redis stock reservation, Lua atomic script | P2 |
| `orders/` | verify all 4 files, status transition logic | P2 |
| `iot/` | WebSocket + Redis Streams + TimescaleDB hypertable | P3 |
| `admin/` | CRUD for products / orders / users via API | P3 |

---

## 📁 Canonical Directory Structure

```
backend/
├── app/
│   ├── main.py
│   ├── api/v1/
│   │   ├── router.py
│   │   ├── auth/         {router, service, repository, schemas}.py
│   │   ├── users/
│   │   ├── products/
│   │   ├── categories/
│   │   ├── cart/
│   │   ├── orders/
│   │   ├── blog/
│   │   ├── delivery/     # CDEK v2
│   │   ├── payments/     # YooKassa
│   │   ├── iot/          # WebSocket, Redis Streams, TimescaleDB
│   │   ├── admin/        # role=admin only
│   │   ├── search/       # Meilisearch proxy
│   │   └── media/        # MinIO
│   ├── core/
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   ├── redis.py
│   │   └── models/       # ← ЕДИНСТВЕННОЕ место для моделей
│   ├── tasks/
│   │   ├── celery_app.py
│   │   ├── notifications.py
│   │   ├── inventory.py
│   │   └── search_index.py
│   └── integrations/
│       ├── cdek.py
│       ├── yoomoney.py
│       ├── cbr_rates.py
│       └── meilisearch.py
├── migrations/versions/
├── alembic.ini
├── Dockerfile
└── requirements.txt
```

**Rule:** NEVER create files outside this structure unless explicitly permitted.

---

## 📜 Coding Contracts

### General
- File header: `# Module: <domain>/<file> | Agent: backend-agent | Task: <task_id>`
- NO `Any` in type hints — use `TypeVar`, `Generic`, `Protocol`
- NO f-strings in SQL — use only parameterized SQLAlchemy queries
- NO hardcoded secrets — always use `app/core/config.py` → `BaseSettings`
- NO top-level `app/models/`, `app/schemas/`, `app/services/` — feature-first only

### Endpoints
- Each endpoint has dedicated Pydantic `RequestSchema` + `ResponseSchema` in `schemas.py`
- `ResponseSchema` must include `model_config = ConfigDict(from_attributes=True)`
- Explicit HTTP status codes: `status_code=status.HTTP_201_CREATED`, etc.
- Pagination: cursor-based (`next_cursor`, `per_page`) — NO offset pagination on large tables
- Rate limiting on `/auth/*`, `/checkout`, `/payments/*` via `slowapi`

### Services and Repositories
- Services NEVER import from `db/` directly — only through repository methods
- **Mandatory Commit**: All service methods that modify data MUST call `await self.repo.session.commit()`
- **Async Safety**: Always reload model with relationships (`selectinload`) after commit and before Pydantic validation to avoid `MissingGreenlet`
- Repository methods are async: `async def get_by_id(self, id: UUID) -> Model | None`
- External API calls: `tenacity`, `stop_after_attempt(3)`, `wait_exponential(min=1, max=10)`
- Service DI pattern: `def __init__(self, repo: XRepo = Depends(get_x_repo))`

### Tasks & Celery
- Within synchronous Celery tasks, ALWAYS use `asyncio.run(_async_func())` — NEVER `get_event_loop().run_until_complete()`

### Authentication
- JWT: `access_token` (15 min TTL) + `refresh_token` (7 days, rotation on use)
- Passwords: argon2 (preferred) or bcrypt — NEVER store plaintext
- Roles: `admin`, `manager`, `customer` — enforced via `Depends(require_role(...))`
- All `/admin/*` routes MUST use `require_role("admin")`

### Cart (Redis + PostgreSQL)
- Redis Hash `stock:{product_id}` — real-time stock reads
- `CartService` MUST use `RedisInventory` via `get_inventory` dependency
- Reservation: atomic Lua script for stock decrement (prevents race conditions)
- Cart reservation TTL: 30 min — auto-released via Redis `EXPIRE`
- PostgreSQL = source of truth; Redis = cache + reservation layer

---

## 📊 IoT Contract

### Telemetry Model (`db/models/telemetry.py`)
- MUST be a **TimescaleDB hypertable** with `chunk_time_interval = '1 day'`
- Required columns: `device_id UUID`, `ts TIMESTAMPTZ`, `data JSONB`
- Hypertable in Alembic `upgrade()`:
```python
op.execute(
    "SELECT create_hypertable('telemetry', 'ts', "
    "chunk_time_interval => INTERVAL '1 day')"
)
op.execute(
    "SELECT add_retention_policy('telemetry', "
    f"INTERVAL '{settings.TELEMETRY_RETENTION_DAYS} days')"
)
```

### Data Pipeline
```
OBD device
  ↓
POST /api/v1/iot/data → validate → XADD iot:{device_id} (Redis Stream)
  ↓
Celery consumer (XREAD) → batch insert → TimescaleDB
  ↓
WebSocket /ws/iot/{device_id} → live push to subscribers
```

### WebSocket
- Authentication: `?token=<access_token>` query parameter
- Disconnect: always use `try/finally` + `ConnectionManager.disconnect(device_id, ws)`
- Dashboard: ALWAYS use `time_bucket` (TimescaleDB), never raw `SELECT *`

---

## 🔧 Admin Panel Contract

- ALL `/admin/*` routes wrapped in `require_role("admin")`
- Pure API — NO Flask-Admin or SQLAdmin
- Required sections: `products`, `orders`, `users`, `blog`, `iot`
- Audit log: every admin action logged via `structlog` with `admin_id`, `action`, `target`

---

## 🔒 Security

- PII fields (name, phone, email) — encrypted at rest with `cryptography.fernet`
- Blog/comment HTML — sanitize with `bleach` before persisting
- YooKassa webhooks — verify `HMAC-SHA256` signature before any state change
- CORS — NEVER `allow_origins=["*"]` in production; read from `settings.ALLOWED_ORIGINS`
- Logging — NEVER log passwords, tokens, or personal data

---

## 🔄 Alembic Contract

> Any change to `db/models/*.py` REQUIRES a migration. No exceptions.

```bash
# 1. After modifying db/models/*.py:
alembic revision --autogenerate -m "<domain>: <what changed>"
# 2. Review generated file in migrations/versions/
# 3. Apply: alembic upgrade head
# 4. NEVER edit already-applied migrations
# 5. NEVER run alembic downgrade in production without orchestrator approval
```

**Migration naming:** `YYYYMMDD_HHMMSS_<domain>_<action>.py`

**`env.py` must import all models:**
```python
from app.db.models import (  # noqa: F401
    user, user_device, product, order, blog,
    notification, redirect, cart, telemetry
)
```

---

## 🧪 Testing Contract

- Integration tests: MUST use `fakeredis[lua]>=2.20.0` in `conftest.py`
- Database: SQLite in-memory for unit tests (JSON instead of JSONB)
- Coverage targets: `app/services/` > 80%, `app/api/` > 70%

---

## ✅ Pre-Report Checklist

```bash
# Run ALL steps, fix ALL errors before writing report:
ruff check app/ --fix && ruff check app/
mypy app/ --ignore-missing-imports
pytest tests/unit/ -v --cov=app --cov-report=term-missing
bandit -r app -ll
alembic check && alembic heads
```

---

## 📝 Report Template

Write to: `../.claude/agents/reports/backend/<task_id>.md`

```markdown
## Status: DONE | IN_PROGRESS | BLOCKED
## Completed:
- created backend/app/db/models/cart.py
- implemented backend/app/api/v1/cart/ (router, service, repository, schemas)
## Artifacts:
- backend/app/db/models/cart.py
- backend/app/api/v1/cart/router.py
- backend/migrations/versions/20260227_150000_cart.py
## Migrations:
- 20260227_150000_cart: added tables cart, cart_item
## Contracts Verified:
- Pydantic schemas: ✅ | DI via Depends: ✅ | No Any: ✅
- Redis Lua script: ✅ | alembic check: ✅
- ruff: ✅ | mypy: ✅ | pytest: ✅
## Test Coverage:
- services/cart.py: 84% | api/v1/cart/: 71%
## Next:
- frontend-agent: /api/v1/cart/* ready — contracts in api_contracts.md
## Blockers:
- none
```
