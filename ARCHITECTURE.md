# ARCHITECTURE.md — Architectural Invariants

> This is the canonical architecture. Violation of any invariant = PR block.

## Layers (Forward-only dependencies)

```
Types → Config → Repository → Service → Router → UI
```

- **Types** (`schemas.py`) — Pydantic models, no dependencies.
- **Config** (`core/config.py`) — pydantic-settings, only depends on Types.
- **Repository** (`repository.py`) — SQLAlchemy async CRUD, depends on Types + Config.
- **Service** (`service.py`) — Business logic, uses Repository via DI.
- **Router** (`router.py`) — FastAPI endpoints, uses Service via Depends.
- **UI** (frontend) — Consumes Router via REST/WS.

## Cross-cutting Concerns
Auth, telemetry, feature flags → only via `app/core/dependencies.py` (Providers).

## Module Invariants

| Layer | Location | Prohibited |
|---|---|---|
| SQLAlchemy Models | `backend/app/db/models/` | Duplicating in other folders. |
| Pydantic Schemas | `backend/app/api/v1/<feature>/schemas.py` | Global `app/schemas/` folder. |
| Business Logic | `backend/app/api/v1/<feature>/service.py` | Global `app/services/` folder. |
| Cross-domain Logic | `backend/app/core/` or `app/tasks/` | In feature-specific folders. |
| Design Tokens | `frontend/assets/css/tokens.css` | Inlining in `.vue` components. |
| Theme State | `frontend/stores/themeStore.ts` | Storing in local components. |

## Mandatory Feature Structure

```
backend/app/api/v1/<feature>/
├── router.py      # FastAPI routes (@router.get/post/...)
├── service.py     # Business logic, accepts dependencies via DI
├── repository.py  # CRUD via SQLAlchemy async, parameterized queries
└── schemas.py     # Separate Request + Response Pydantic models
```

## Canonical Project Structure

```
site-builder/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Feature-first structure
│   │   ├── core/            # Settings, security, dependencies
│   │   ├── db/              # Base, session, models (ONLY place for models)
│   │   ├── tasks/           # Celery tasks
│   │   └── integrations/    # External APIs (CDEK, YooMoney, etc.)
│   ├── migrations/          # Alembic versions
│   └── requirements.txt
├── frontend/
│   ├── assets/css/tokens.css # ONLY source for design tokens
│   ├── components/U/        # UI kit
│   ├── pages/               # Nuxt pages
│   ├── stores/              # Pinia stores
│   └── nuxt.config.ts
├── deploy/                  # Nginx, Docker Compose (prod)
├── tests/                   # Integration, unit, load tests
└── .gemini/                 # Agent configurations and tasks
```

## Development Contracts

### 🌐 API Path & BaseURL Policy
1. **apiBase** in `runtimeConfig` **MUST** include the version (e.g., `/api/v1`).
2. **PROHIBITED**: Manually adding `/api/v1` or `/v1` to relative paths when using `useFetch` or `$fetch` with `baseURL: apiBase`.
3. All paths in composables MUST start with `/` relative to `apiBase` (e.g., `/products`, not `/api/v1/products`).

### 🔐 Auth & Profile Flow Contract
1. **Full User Object**: Any auth endpoint (`login`, `callback`, `telegram`) **MUST** return the full `UserResponse` model in the `user` field along with tokens.
2. **Token Naming**: Use strictly `accessToken` in frontend composables (not `token`, not `jwt`).
3. **Re-hashing**: When updating `email` in `UserRepository`, the backend MUST recalculate `email_hash` (blind index).

### 📱 UI Parity Rule
- Any navigation link added to the mobile menu (Drawer) **MUST** have a counterpart in the desktop version (Header/Sidebar) unless specified otherwise.

### 🏷️ Frontend Naming Conventions (Types & Interfaces)
1. **Device Conflicts**: To avoid Nuxt 3 auto-import conflicts, do not use the generic name `Device`.
   - For IoT/Telemetry, use `IoTDevice` (in `useIoT.ts`).
   - For Shop/Firmware, use `FirmwareDevice` (in `firmwareStore.ts`).
2. **Shared Types**: Common data types (User, Order) must be unique in `stores/` or `composables/`.

### 📊 IoT / Telemetry Contract
- Table `telemetry` **MUST** be a TimescaleDB hypertable (chunk_time_interval = '1 day').
- WebSocket endpoint: `ws://host/ws/iot/{device_id}`.
- Data written via Redis Streams → Celery consumer → TimescaleDB.
- Dashboard aggregates data via TimescaleDB `time_bucket` (no raw SELECT).
- Retention policy: 90 days (configured via `TELEMETRY_RETENTION_DAYS` in .env).

## Linter & Validation Rules
- Files > 500 lines → Warning/Refactor required.
- `import` from `app/models/` (instead of `app/db/models/`) → Error.
- `raw SQL` in `repository.py` → Error.
- Colors in `.vue` outside of `var(--*)` → Error.
