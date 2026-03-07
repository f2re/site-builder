## Status: DONE

## Completed:
- Step 1: Added `FIRMWARE_COMPILER_PATH` and `FIRMWARE_BUILD_DIR` to `Settings` in `config.py`
- Step 2: Rewrote `get_versions()` in `service.py` — correct CLI format `cd {dir} && ./{binary} {device_exec} revisions`, uses `shlex.quote()`, parses `Revisions: 1 2 3 ...` output, fallback `['1','2','3']` when compiler absent
- Step 3: Rewrote `compile_firmware()` in `service.py` — correct CLI format with `make {serial} {version} {label}`, output to `FIRMWARE_BUILD_DIR/Firmware_{TYPE}_{version}_{label}_{serial}.bin`, `os.makedirs(exist_ok=True)`, dummy file in dev mode, all args via `shlex.quote()`
- Step 4: Added `get_token_by_token_str()` to `repository.py` — eager-loads `.devices` with `.complectations` via `selectinload`
- Step 5: Added to `service.py`: `get_devices_by_token_str()`, `get_version_info()`, `verify_token_owns_device()`, `toggle_complectation()`, `merge_users_by_id()`; updated `get_all_devices()` to accept `search` param
- Step 6: Added to `repository.py`: `get_complectation_by_id()`, `toggle_device_complectation()` (check-then-delete-or-insert), `delete_device()`, `list_all_devices()` with optional `search` filter
- Step 7: Added to `router.py`: `GET /firmware/by-token/{token}/devices`, `GET /firmware/by-token/{token}/versions/{device_type}`, `GET /firmware/version-info`, `POST /firmware/by-token/{token}/download`, `POST /firmware/devices/{serial}/complectations/{complectation_id}/toggle`
- Step 8: Added to `admin/router.py`: `GET /admin/firmware/devices` (with `search` query param), `POST /admin/firmware/devices`, `DELETE /admin/firmware/devices/{serial}`, `POST /admin/firmware/devices/{serial}/complectations/{comp_id}/toggle` (no owner check), `GET /admin/firmware/duplicates` (email_hash grouping), `POST /admin/firmware/merge` (by user UUID)
- Step 9: Added new schemas to `schemas.py`: `VersionInfoResponse`, `AdminAddDeviceRequest`, `MergeByIdRequest`
- Step 10: No new Alembic migration needed — no model schema changes, firmware tables already exist in `20260301_1400-dashfirm_initial_tables.py`

## Artifacts:
- `backend/app/core/config.py` — added `FIRMWARE_COMPILER_PATH`, `FIRMWARE_BUILD_DIR`
- `backend/app/api/v1/firmware/service.py` — rewritten with 5 new methods and corrected CLI calls
- `backend/app/api/v1/firmware/repository.py` — added 4 new methods, updated `list_all_devices` with search
- `backend/app/api/v1/firmware/schemas.py` — added `VersionInfoResponse`, `AdminAddDeviceRequest`, `MergeByIdRequest`
- `backend/app/api/v1/firmware/router.py` — added 5 public token-based endpoints
- `backend/app/api/v1/admin/router.py` — added 6 new admin firmware endpoints

## Contracts Verified:
- Pydantic schemas: OK (all have `ConfigDict(from_attributes=True)` where needed)
- DI via Depends: OK
- All mutating service methods call `await session.commit()`: OK
- `shlex.quote()` used on all CLI arguments: OK
- No hardcoded secrets: OK
- ruff: 0 errors
- mypy: 0 issues (124 source files checked)
- pytest: 12/12 passed
- alembic: DB not running locally (connection error expected), code-level check via `python -c 'from app.db.models.firmware import ...'` passes OK

## Next:
- Frontend-agent can consume:
  - `GET /api/v1/firmware/by-token/{token}/devices` — list devices by token
  - `GET /api/v1/firmware/by-token/{token}/versions/{device_type}` — list firmware versions
  - `GET /api/v1/firmware/version-info?version=X&device_type=OBD` — version changelog
  - `POST /api/v1/firmware/by-token/{token}/download` — download firmware by token (no auth)
  - `POST /api/v1/firmware/devices/{serial}/complectations/{id}/toggle` — toggle complectation (auth required)
  - Admin: `/api/v1/admin/firmware/*` — all CRUD endpoints

## Blockers:
- none
