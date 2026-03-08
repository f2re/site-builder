## Status: DONE

## Completed:
- Added `AdminUserUpdate` schema (full_name, email, phone, role, is_active — all Optional)
- Added `DeliveryAddressResponse` schema (from_attributes=True, all address fields)
- Added `DeliveryAddressUpdate` schema (all Optional fields for PATCH semantics)
- Added `get_address_repo` dependency factory for `DeliveryAddressRepository`
- Imported `DeliveryAddressRepository` from `app.api.v1.users.repository`
- Added `GET /admin/users/{user_id}` — returns decrypted user or 404
- Added `PATCH /admin/users/{user_id}` — updates PII fields via `repo.update()` (encryption handled in repository), includes superadmin/last-admin demotion protection
- Added `GET /admin/users/{user_id}/addresses` — returns list of decrypted addresses
- Added `PUT /admin/users/{user_id}/addresses/{addr_id}` — updates address with PII encryption via `DeliveryAddressRepository.update()`
- Added `DELETE /admin/users/{user_id}/addresses/{addr_id}` — deletes address or returns 404

## Artifacts:
- backend/app/api/v1/admin/router.py (modified — new endpoints added at lines 483–608)

## Key Implementation Notes:
- Route ordering preserved: `GET /users/export` remains before `GET /users/{user_id}` — no conflict
- PII encryption delegated to `UserRepository.update()` and `DeliveryAddressRepository.update()` — consistent with existing pattern
- `PATCH /admin/users/{user_id}` checks: if target is last superadmin, role change is blocked; if target is last non-superadmin admin, role change is blocked
- `addr.user_id != user_id` check ensures cross-user address access is prevented (returns 404)
- `update_kwargs` built only from non-None payload fields (true partial update)

## Contracts Verified:
- Pydantic schemas: OK (ConfigDict from_attributes=True on DeliveryAddressResponse)
- DI via Depends: OK
- No Any in type hints: router functions return Any (existing pattern in this file)
- ruff: OK (0 errors)
- mypy: OK on router.py and users/ (pre-existing error in migration_service.py line 188 — not caused by this task)
- alembic check: N/A — no model changes, DB not available locally (Docker-only)

## Migrations:
- None required — no changes to SQLAlchemy models

## Next:
- frontend-agent: admin user edit endpoints ready at `/api/v1/admin/users/{user_id}` (GET, PATCH) and `/api/v1/admin/users/{user_id}/addresses` (GET, PUT, DELETE)

## Blockers:
- none
