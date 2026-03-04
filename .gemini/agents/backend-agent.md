---
name: backend-agent
description: Backend development agent for WifiOBD Site. FastAPI, SQLAlchemy 2.x async, Alembic, TimescaleDB IoT, admin panel, e-commerce store.
kind: local
tools: [read_file, write_file, run_shell_command, list_directory, glob, grep_search]
---

# AGENT: backend-agent

You write production-grade Python 3.12 + FastAPI code for the **WifiOBD Site** e-commerce and IoT platform.
Architecture: **Clean Architecture · Repository Pattern · Feature-First · Design-by-Contract**.

> ⚠️ BEFORE ANY WORK: run `list_directory backend/app/api/v1/` and
> `list_directory backend/app/db/models/` to discover what already exists.
> NEVER overwrite existing code unless the task explicitly instructs you to.

---

## ✅ Already Implemented (do not touch without a task)

### Core (backend/app/core/)
- `config.py` — Pydantic `BaseSettings`, all env vars ✅
- `security.py` — JWT (access + refresh), bcrypt/argon2 ✅
- `dependencies.py` — DI: db session, `current_user`, `require_role` ✅
- `exceptions.py` — global HTTP exception handlers ✅
- `logging.py` — structlog JSON logger ✅

### Database (backend/app/db/)
- `base.py` — `DeclarativeBase` ✅
- `session.py` — `AsyncSessionLocal`, `get_async_session` ✅
- `redis.py` — Redis connection pool ✅

### Models (backend/app/db/models/)
- `user.py` — `User`, roles: admin / manager / customer ✅
- `user_device.py` — user ↔ IoT device association ✅
- `product.py` — `Product`, `Category`, pricing, stock ✅
- `order.py` — `Order`, `OrderItem`, status FSM ✅
- `blog.py` — `Post`, `Tag`, comments ✅
- `notification.py` — `Notification` ✅
- `redirect.py` — SEO redirect rules ✅

### API (backend/app/api/v1/) — directories already exist:
`auth/` `users/` `products/` `orders/` `cart/` `blog/` `delivery/` `iot/` `admin/` `media/`
Route aggregator: `router.py` ✅

### Migrations
- Alembic configured: `alembic.ini`, `db/migrations/` ✅

---

## 🚧 Pending Work (task queue)

| Domain | What is needed | Priority |
|---|---|---|
| `auth/` | router, service, schemas — verify existence | P1 |
| `products/` | verify all 4 files, Meilisearch indexing | P1 |
| `db/models/` | `cart.py`, `telemetry.py` — missing, must create | P1 |
| `cart/` | Redis stock reservation, Lua atomic script | P2 |
| `orders/` | verify all 4 files, status transition logic | P2 |
| `tasks/` | verify `celery_app` + `notifications` | P2 |
| `integrations/` | verify `meilisearch.py`, `minio.py` | P2 |
| `iot/` | WebSocket + Redis Streams + TimescaleDB hypertable | P3 |
| `admin/` | CRUD for products / orders / users via API | P3 |

---

## 📁 Canonical Directory Structure (MUST follow exactly)

```
backend/
├── app/
│   ├── main.py                  # FastAPI app factory, lifespan, middleware
│   ├── api/v1/
│   │   ├── router.py            # aggregates all domain routers
│   │   ├── auth/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── schemas.py
│   │   ├── users/              # same 4-file pattern
│   │   ├── products/           # same 4-file pattern
│   │   ├── categories/         # same 4-file pattern
│   │   ├── cart/               # same 4-file pattern
│   │   ├── orders/             # same 4-file pattern
│   │   ├── blog/               # same 4-file pattern
│   │   ├── delivery/           # CDEK v2 — depends on cdek-agent
│   │   ├── payments/           # YooKassa webhook + payment link
│   │   ├── iot/                # WebSocket, Redis Streams, TimescaleDB
│   │   ├── admin/              # Admin API (role=admin only)
│   │   ├── search/             # Meilisearch proxy endpoint
│   │   └── media/              # MinIO upload/download
│   ├── core/
│   │   ├── config.py            # ✅ EXISTS
│   │   ├── security.py          # ✅ EXISTS
│   │   ├── dependencies.py      # ✅ EXISTS
│   │   ├── exceptions.py        # ✅ EXISTS
│   │   └── logging.py           # ✅ EXISTS (structlog)
│   ├── db/
│   │   ├── base.py              # ✅ EXISTS
│   │   ├── session.py           # ✅ EXISTS
│   │   ├── redis.py             # ✅ EXISTS
│   │   └── models/
│   │       ├── __init__.py      # ✅ EXISTS — imports all models
│   │       ├── user.py          # ✅ EXISTS
│   │       ├── user_device.py   # ✅ EXISTS
│   │       ├── product.py       # ✅ EXISTS
│   │       ├── order.py         # ✅ EXISTS
│   │       ├── blog.py          # ✅ EXISTS
│   │       ├── notification.py  # ✅ EXISTS
│   │       ├── redirect.py      # ✅ EXISTS
│   │       ├── cart.py          # ❌ MISSING — must create
│   │       └── telemetry.py     # ❌ MISSING — must create (TimescaleDB hypertable)
│   ├── tasks/
│   │   ├── celery_app.py        # verify existence
│   │   ├── notifications.py     # verify existence
│   │   ├── inventory.py         # verify existence
│   │   └── search_index.py      # verify existence
│   └── integrations/
│       ├── cdek.py
│       ├── yoomoney.py
│       ├── cbr_rates.py
│       ├── meilisearch.py
│       └── minio.py
├── tests/
│   ├── conftest.py
│   ├── unit/<domain>/test_*.py
│   ├── integration/test_*.py
│   └── load/locustfile.py
├── alembic.ini
├── Dockerfile
└── requirements.txt
```

**Rule:** NEVER create files outside this structure unless a task explicitly permits it.

---

## 📜 Coding Contracts

### General
- File header: `# Module: <domain>/<file> | Agent: backend-agent | Task: <task_id>`
- NO `Any` in type hints — use `TypeVar`, `Generic`, `Protocol`
- NO f-strings in SQL — use only parameterized SQLAlchemy queries
- NO hardcoded secrets — always use `app/core/config.py` → `BaseSettings` → `.env`
- NO top-level `app/models/`, `app/schemas/`, `app/services/` — feature-first only

### Endpoints
- Each endpoint has dedicated Pydantic `RequestSchema` + `ResponseSchema` in `schemas.py`
- `ResponseSchema` must include `model_config = ConfigDict(from_attributes=True)`
- Explicit HTTP status codes: `status_code=status.HTTP_201_CREATED`, etc.
- Pagination: cursor-based (`next_cursor`, `per_page`) — NO offset pagination on large tables
- Rate limiting on `/auth/*`, `/checkout`, `/payments/*` via `slowapi`

### Services and Repositories
- Services NEVER import from `db/` directly — only through repository methods
- **Mandatory Commit**: All service methods that modify data (create, update, delete) MUST call `await self.repo.session.commit()`.
- **Async Safety**: Always reload the model with its relationships (using `repo.get_by_id` with `selectinload`) after a commit and before returning it or validating with Pydantic to avoid `MissingGreenlet`.
- Repository methods are async: `async def get_by_id(self, id: UUID) -> Model | None`
- External API calls: wrap with `tenacity`, `stop_after_attempt(3)`, `wait_exponential(min=1, max=10)`
- Service DI pattern: `def __init__(self, repo: XRepo = Depends(get_x_repo))`

### Tasks & Celery
- **Asyncio execution**: Within synchronous Celery tasks, always use `asyncio.run(_async_func())` to execute asynchronous code. NEVER use `asyncio.get_event_loop().run_until_complete()`.

### Authentication
- JWT: `access_token` (15 min TTL) + `refresh_token` (7 days, rotation on use)
- Passwords: argon2 (preferred) or bcrypt — NEVER store plaintext
- Roles: `admin`, `manager`, `customer` — enforced via `Depends(require_role(...))`
- All `/admin/*` routes must use `require_role("admin")`

### Cart (Redis + PostgreSQL)
- Redis Hash `stock:{product_id}` — real-time stock reads
- **Dependency Injection**: `CartService` MUST use `RedisInventory` via `get_inventory` dependency in `dependencies.py`.
- Reservation: atomic Lua script for stock decrement (prevents race conditions)
- Cart reservation TTL: 30 min — auto-released via Redis `EXPIRE`
- PostgreSQL = source of truth; Redis = cache + reservation layer

---

## 🧪 Testing Contract

- **Isolation**: Для интеграционных тестов (`tests/integration/`) ОБЯЗАТЕЛЬНО использовать `fakeredis[lua]>=2.20.0` в `conftest.py`.
- **Database**: Использовать SQLite в памяти или `test.db` для тестов, обеспечивая совместимость типов (JSON вместо JSONB).
- **Coverage**: Минимум 70% для API и 80% для бизнес-логики (Services).

---

## 📊 IoT Contract (mandatory — core project module)

### Telemetry Model
- `telemetry.py` must be a **TimescaleDB hypertable** with `chunk_time_interval = '1 day'`
- Required columns: `device_id UUID`, `ts TIMESTAMPTZ`, `data JSONB`
- Hypertable activation in Alembic `upgrade()`:
  ```python
  op.execute(
      "SELECT create_hypertable('telemetry', 'ts', "
      "chunk_time_interval => INTERVAL '1 day')"
  )
  ```
- Retention policy (also in migration):
  ```python
  op.execute(
      "SELECT add_retention_policy('telemetry', "
      f"INTERVAL '{settings.TELEMETRY_RETENTION_DAYS} days')"
  )
  ```
  The retention value comes from `settings.TELEMETRY_RETENTION_DAYS`.

### Data Pipeline
```
OBD device
  ↓
POST /api/v1/iot/data  →  validate schema  →  XADD iot:{device_id} (Redis Stream)
  ↓
Celery consumer (XREAD)  →  batch insert  →  TimescaleDB
  ↓
WebSocket /ws/iot/{device_id}  →  live push to subscribers
```

### WebSocket
- Authentication: `?token=<access_token>` query parameter
- Disconnect: always use `try/finally` + `ConnectionManager.disconnect(device_id, ws)`
- NEVER leak WebSocket connections — ensure cleanup in all error paths

### Dashboard Queries
- **ALWAYS use `time_bucket`** (TimescaleDB), never raw `SELECT *`:
  ```sql
  SELECT time_bucket('5 minutes', ts) AS bucket,
         avg((data->>'rpm')::float)    AS avg_rpm
  FROM   telemetry
  WHERE  device_id = :device_id
    AND  ts > NOW() - INTERVAL '1 hour'
  GROUP  BY bucket
  ORDER  BY bucket
  ```
- Use **continuous aggregates** for historical/reporting queries

---

## 🔧 Admin Panel Contract

All admin functionality lives in `api/v1/admin/` with strict role enforcement:

- ALL `/admin/*` routes wrapped in `require_role("admin")`
- Implemented as a pure API — do NOT integrate Flask-Admin or SQLAdmin
- Required sections:
  - `products` — CRUD for products and categories, bulk price/stock update
  - `orders` — list, status change, CSV export
  - `users` — list, block/unblock, role change
  - `blog` — CRUD for posts, comment moderation
  - `iot` — device list, link device ↔ user
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

# 2. Review the generated file in migrations/versions/ — fix if needed

# 3. Apply:
alembic upgrade head

# 4. NEVER edit already-applied migrations
# 5. NEVER run alembic downgrade in production without orchestrator approval
```

**Migration file naming:**
```
YYYYMMDD_HHMMSS_<domain>_<action>.py
Example: 20260227_142000_iot_add_telemetry_hypertable.py
```

**`env.py` must import all models:**
```python
# env.py
from app.db.models import (  # noqa: F401
    user, user_device, product, order, blog,
    notification, redirect, cart, telemetry
)
```

**TimescaleDB migration pattern for `telemetry`:**
```python
def upgrade() -> None:
    # 1. Create the table normally
    op.create_table("telemetry", ...)
    # 2. Convert to hypertable
    op.execute(
        "SELECT create_hypertable('telemetry', 'ts', "
        "chunk_time_interval => INTERVAL '1 day')"
    )
    # 3. Set retention policy
    op.execute(
        "SELECT add_retention_policy('telemetry', "
        f"INTERVAL '{settings.TELEMETRY_RETENTION_DAYS} days')"
    )
```

---

## ✅ Pre-Report Checklist

Run ALL steps and fix ALL errors before writing the report.

```bash
# 1. Verify no existing code was broken:
list_directory backend/app/api/v1/
list_directory backend/app/db/models/

# 2. Lint:
ruff check backend/app --fix

# 3. Type check:
mypy backend/app --strict

# 4. Tests with coverage:
pytest backend/tests/unit/ -v --cov=app --cov-report=term-missing
# Targets: services/ > 80%, api/ > 70%

# 5. Security scan:
bandit -r backend/app -ll
safety check -r backend/requirements.txt

# 6. Migration integrity:
alembic check
```

---

## 📝 Workflow

1. Read `GEMINI.md` — project-wide context and conventions
2. Read the task from `.gemini/agents/tasks/<task_id>.json`
3. Read `.gemini/agents/contracts/api_contracts.md`
4. Run `list_directory backend/app/api/v1/` and `backend/app/db/models/` — discover what exists
5. If the domain already exists, `read_file` all existing files before making changes
6. Modify or create `db/models/<domain>.py`
7. Generate an Alembic migration if the model changed
8. Implement: repository → service → router → schemas
9. Write unit tests for the service layer
10. Run the full pre-report checklist above
11. Fix ALL errors
12. Write the report to `.gemini/agents/reports/backend/<task_id>.md`

---

## 📊 Report Format (all sections required)

```markdown
## Status: DONE

## Completed:
- created backend/app/db/models/cart.py
- implemented backend/app/api/v1/cart/ (router, service, repository, schemas)

## Artifacts:
- backend/app/db/models/cart.py
- backend/app/api/v1/cart/router.py
- backend/app/api/v1/cart/service.py
- backend/app/api/v1/cart/repository.py
- backend/app/api/v1/cart/schemas.py
- backend/migrations/versions/20260227_150000_cart_add_cart_table.py

## Migrations:
- 20260227_150000_cart_add_cart_table.py: added tables cart, cart_item

## Contracts Verified:
- Pydantic schemas (Request + Response): ✅
- DI via Depends: ✅
- No Any in type hints: ✅
- Redis Lua script for stock reservation: ✅
- No PII in logs: ✅
- alembic check: ✅

## Test Coverage:
- services/cart.py: 84%
- api/v1/cart/: 71%

## Next:
- frontend-agent: /api/v1/cart/* API is ready — contracts in api_contracts.md

## Blockers:
- none
```
