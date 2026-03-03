# WifiOBD Site — Backend Agent Skill

## Role
Backend development agent for **WifiOBD Site** e-commerce and IoT platform.

## Stack
- **Python 3.12**, FastAPI (async), SQLAlchemy 2.x (async), Alembic
- **PostgreSQL 16 + TimescaleDB** — основная БД + IoT-телеметрия
- **Redis 7** — сессии, кэш, Celery broker, stock reservation
- **Celery + Beat** — фоновые задачи
- **Meilisearch** — полнотекстовый поиск

## Architecture
**Clean Architecture · Repository Pattern · Feature-First · Design-by-Contract**

### Feature Structure (backend/app/api/v1/{feature}/)
```
{feature}/
├── router.py      # FastAPI routes
├── service.py     # Business logic (DI-ready)
├── repository.py  # CRUD via SQLAlchemy async
└── schemas.py     # Pydantic Request/Response models
```

### Models Location
**ONLY** in `backend/app/db/models/` — NEVER create `app/models/`, `app/schemas/`, `app/services/`

## Coding Contracts

### Endpoints
- Pydantic Request + Response schemas for EVERY endpoint
- `ResponseSchema` must have `model_config = ConfigDict(from_attributes=True)`
- Explicit HTTP status codes
- Cursor-based pagination (NO offset pagination on large tables)

### Services & Repositories
- Services NEVER import from `db/` directly — only through repositories
- All repository methods are async
- External API calls: wrap with `tenacity` (3 attempts, exponential backoff)
- DI pattern: `def __init__(self, repo: XRepo = Depends(get_x_repo))`

### Authentication
- JWT: `access_token` (15 min) + `refresh_token` (7 days, rotation)
- Passwords: argon2 or bcrypt — NEVER plaintext
- Roles: `admin`, `manager`, `customer` — enforced via `Depends(require_role(...))`

### Cart (Redis + PostgreSQL)
- Redis Hash `stock:{product_id}` — real-time stock
- Reservation: atomic Lua script (prevents race conditions)
- TTL: 30 min — auto-release via Redis `EXPIRE`

## IoT Contract (CRITICAL)

### Telemetry Model
- MUST be **TimescaleDB hypertable** with `chunk_time_interval = '1 day'`
- Columns: `device_id UUID`, `ts TIMESTAMPTZ`, `data JSONB`
- Retention policy: 90 days (from `TELEMETRY_RETENTION_DAYS` env)

### Data Pipeline
```
OBD device → POST /api/v1/iot/data → Redis Stream → Celery consumer → TimescaleDB
WebSocket /ws/iot/{device_id} → live push to subscribers
```

### Dashboard Queries
**ALWAYS use `time_bucket`** (TimescaleDB), NEVER raw `SELECT *`:
```sql
SELECT time_bucket('5 minutes', ts) AS bucket,
       avg((data->>'rpm')::float) AS avg_rpm
FROM telemetry
WHERE device_id = :device_id AND ts > NOW() - INTERVAL '1 hour'
GROUP BY bucket ORDER BY bucket
```

## Alembic Contract
- ANY change to `db/models/*.py` REQUIRES migration
- NEVER edit already-applied migrations
- Migration naming: `YYYYMMDD_HHMMSS_<domain>_<action>.py`

## Pre-Commit Checklist
```bash
# Lint
ruff check backend/app --fix && ruff check backend/app

# Type check
mypy backend/app --ignore-missing-imports

# Migration integrity
alembic heads  # MUST be exactly ONE head
alembic check  # Models must match migrations

# Dependencies
pip install -r backend/requirements.txt --quiet
```

## Report Format
Save reports to `.qwen/agents/reports/backend/<task_id>.md`

```markdown
## Status: DONE

## Completed:
- list of completed items

## Artifacts:
- backend/app/db/models/cart.py
- backend/app/api/v1/cart/router.py

## Migrations:
- 20260227_150000_cart_add_cart_table.py

## Contracts Verified:
- Pydantic schemas: ✅
- DI via Depends: ✅
- alembic check: ✅

## Test Coverage:
- services/cart.py: 84%

## Next:
- frontend-agent: /api/v1/cart/* API ready

## Blockers:
- none
```
