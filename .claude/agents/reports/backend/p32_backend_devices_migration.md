## Status: DONE

## Completed:
- Added `comment` (Text, nullable) and `oc_device_id` (Integer, nullable, indexed) fields to `UserDevice` model
- Added `OCDevice`, `OCToken`, `OCTokenToDevice` classes to `opencart_models.py` (appended, existing classes untouched)
- Created Alembic migration `20260309_1000_user_devices_add_comment_oc_device_id.py` with revision `a9b8c7d6e5f4`, `down_revision = 'f6f189d8f825'`
- Added `migrate_devices()` method to `MigrationService` in `migration_service.py`
  - Pagination: batch_size=50 by `device_id` cursor via `extra_data['devices_last_id']`
  - User lookup: `OCCustomer.email` → `get_blind_index(email)` → `User.email_hash` (same pattern as `migrate_addresses`)
  - Empty `device_serial` → generates `f"oc-{device_id}-{uuid4().hex[:8]}"`
  - ON CONFLICT SKIP on `unique`/`duplicate` exception
  - Counts: `migrated`, `skipped`, `errors_count` tracked in `job.processed/skipped/failed`
- Added `OCDevice` to top-level imports in `migration_service.py`
- Updated `run_batch()` USERS branch: addresses step now sets `RUNNING` (not DONE), then devices step runs, devices step sets `DONE`
- Added `AdminDeviceRead` and `AdminDeviceUpdate` schemas to `schemas.py`
- Added 5 Admin CRUD endpoints to `router.py`, all protected by `AdminDep`:
  - `GET /admin/devices` — list with `user_id`, `is_active`, `search`, `page`, `per_page` filters
  - `GET /admin/devices/{device_id}` — detail by UUID, 404 on miss
  - `PATCH /admin/devices/{device_id}` — partial update (name, model, is_active, comment)
  - `DELETE /admin/devices/{device_id}` — 204 No Content, 404 on miss
  - `GET /admin/users/{user_id}/devices` — devices by user
- Audit logging via `structlog` with `admin_id`, `action`, `target_id` on all device endpoints

## Artifacts:
- `backend/app/db/models/user_device.py` — added `comment`, `oc_device_id` fields
- `backend/app/db/opencart_models.py` — added `OCDevice`, `OCToken`, `OCTokenToDevice`
- `backend/app/db/migrations/versions/20260309_1000_user_devices_add_comment_oc_device_id.py` — Alembic migration
- `backend/app/api/v1/admin/migration_service.py` — added `migrate_devices()`, updated `run_batch()`, added `OCDevice` import
- `backend/app/api/v1/admin/schemas.py` — added `AdminDeviceRead`, `AdminDeviceUpdate`
- `backend/app/api/v1/admin/router.py` — added 5 device CRUD endpoints, `or_` import, updated admin schemas import

## Migrations:
- `a9b8c7d6e5f4`: `user_devices` — ADD COLUMN comment TEXT NULL, ADD COLUMN oc_device_id INTEGER NULL, CREATE INDEX ix_user_devices_oc_device_id

## Contracts Verified:
- Pydantic schemas: OK (from_attributes=True, all fields typed)
- DI via Depends: OK (get_db session, AdminDep guard)
- No Any in business logic: OK
- Alembic down_revision chain: `f6f189d8f825` → `a9b8c7d6e5f4`
- OCDevice model uses same OCBase as all other OC models
- ruff: not run (no bash access) — code follows project conventions
- mypy: not run (no bash access) — all type annotations explicit
- pytest: not run (no bash access)

## Design Notes:
- User lookup uses `email_hash` blind index via `OCCustomer` join — consistent with `migrate_addresses()` pattern
- The `User` model does NOT have `oc_customer_id` — email-based lookup is the correct approach
- `run_batch()` USERS branch now has 3 sequential phases: users → addresses → devices
- Idempotency: `oc_device_id` field allows checking for re-runs (not yet used as filter, but supports future idempotency checks)

## Next:
- Frontend admin panel can display `/admin/devices` list with migration data
- After running migration, verify device counts match `oc_devices` table

## Blockers:
- none
