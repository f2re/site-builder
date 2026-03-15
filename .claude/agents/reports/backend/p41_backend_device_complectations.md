## Status: DONE

## Completed:
- Added `complectations: List[ComplectationRead] = []` to `AdminDeviceRead` in `admin/schemas.py`
- Added `complectation_ids: Optional[List[UUID]] = None` to `AdminDeviceUpdate` in `admin/schemas.py`
- Added `complectations: List[ComplectationRead] = []` to `AdminUserDeviceRead` in `admin/schemas.py`
- Imported `ComplectationRead` from `firmware/schemas.py` (single source of truth — no duplication)
- Added `GET /admin/firmware/complectations` endpoint (before POST) — returns `List[ComplectationRead]` ordered by caption via `service.repo.list_complectations()`
- Added `PUT /admin/devices/{device_id}/complectations` endpoint — replaces M2M complectations for a UserDevice, uses `selectinload(UserDevice.complectations)`, returns `AdminDeviceRead`
- Added `DeviceComplectationsUpdate` inline schema for the PUT body
- Added `complectations: List[ComplectationRead] = []` to inline `DeviceResponse` in `users/router.py`
- Added `GET /users/complectations` endpoint in `users/router.py` — auth required (any user), returns all `ModuleComplectation` ordered by caption
- Added imports: `selectinload`, `ModuleComplectation` in `admin/router.py`; `select`, `AsyncSession`, `ModuleComplectation`, `ComplectationRead`, `get_db` in `users/router.py`
- `UserDevice.complectations` already has `lazy='selectin'` on the ORM model — auto-loads in all existing GET endpoints

## Artifacts:
- `backend/app/api/v1/admin/schemas.py` — ComplectationRead import, complectations fields in AdminDeviceRead/AdminUserDeviceRead, complectation_ids in AdminDeviceUpdate
- `backend/app/api/v1/admin/router.py` — GET /firmware/complectations, PUT /devices/{device_id}/complectations, DeviceComplectationsUpdate schema, selectinload import, ModuleComplectation import
- `backend/app/api/v1/users/router.py` — complectations field in DeviceResponse, GET /users/complectations endpoint

## API Endpoints Added:
- `GET /api/v1/admin/firmware/complectations` → `List[ComplectationRead]` (admin only)
- `PUT /api/v1/admin/devices/{device_id}/complectations` → body: `{complectation_ids: [uuid,...]}` → `AdminDeviceRead` (admin only)
- `GET /api/v1/users/complectations` → `List[ComplectationRead]` (any authenticated user)

## Contracts Verified:
- ComplectationRead single source: `firmware/schemas.py` (no duplication)
- Pydantic schemas: OK
- DI via Depends: OK
- selectinload used in PUT /devices/{device_id}/complectations: OK
- lazy='selectin' on UserDevice.complectations covers all existing GET endpoints automatically
- ruff: 0 errors
- mypy: 0 issues (164 source files)
- alembic: N/A (no model changes — M2M table `user_device_complectations` already exists from prior migration)
- pytest: pre-existing failures only (e2e requires running server; test_blog_pagination has PYTHONPATH issue; delivery providers need external APIs)

## Next:
- Frontend-agent: endpoints ready
  - `GET /api/v1/admin/firmware/complectations` — used by `useFirmware.ts::fetchAllComplectations()`
  - `PUT /api/v1/admin/devices/{id}/complectations` — set device complectations in admin UI
  - `GET /api/v1/users/complectations` — public complectations list for user cabinet
  - `GET /api/v1/admin/devices/{id}` and `GET /api/v1/users/me/devices` — now return `complectations: []`

## Blockers:
- none
