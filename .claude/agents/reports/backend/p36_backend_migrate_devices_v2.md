## Status: DONE
## Completed:
- Rewrote migrate_devices() from single-pass oc_devices reader to 3-phase oc_token_to_device pipeline
- Sub-phase A: one-shot import of oc_complectations (7 rows) into module_complectations, idempotent by label
- Sub-phase B: batched import from oc_token_to_device (~800 rows) with cursor pagination, SAVEPOINT per device, user resolution via oc_tokens -> oc_customer -> email_hash -> User, merge by device_uid (serial)
- Sub-phase C: batched M2M linking via oc_complectation_to_device -> user_device_complectations, SAVEPOINT per row, idempotent by PK
- Changed count_stmt for DEVICES entity from OCDevice to OCTokenToDevice in run_batch()
- Added _TTD_MODEL_MAP constant: obd -> WIFI_OBD2, afr -> WIFI_OBD2_ADVANCED
- Added imports: OCComplectation, OCComplectationToDevice, OCTokenToDevice, OCToken, ModuleComplectation, user_device_complectations
- Removed unused imports: ModuleDevice (no longer referenced), uuid4 (cleaned by ruff)
## Artifacts:
- backend/app/api/v1/admin/migration_service.py
## What was NOT changed:
- migrate_users, migrate_addresses, migrate_orders, migrate_catalog, migrate_information, _migrate_categories
- run_batch() logic (except the count_stmt for DEVICES)
- No new Alembic migrations (no schema changes)
- No model changes
## Contracts Verified:
- 3-phase structure with extra_data flags: complectations_done, token_devices_done, device_complectations_done
- SAVEPOINT per device/row: OK
- Cursor-based pagination: ttd_last_id (int), ctd_last_serial (str)
- Idempotency: complectations by label, devices by device_uid, M2M by composite PK
- ruff: OK (0 errors)
- mypy: OK (0 issues in 162 files)
- alembic heads: OK (1 head: 20260315_0910)
- pytest: SKIPPED (no DB connection available in local env, tests require PostgreSQL)
## Next:
- Test migration via POST /api/v1/admin/migration/start {"entity": "devices"} with running DB
## Blockers:
- none
