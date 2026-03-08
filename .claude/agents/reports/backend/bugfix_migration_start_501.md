## Status: DONE

## Completed:
- FIX 1: Added `response_model=List[MigrationJobResponse]` to `@router.post("/migration/start")` in router.py — resolves PydanticSerializationError 500 when returning raw SQLAlchemy objects
- FIX 2: In `migration_service.py::start_migration()`, separated tracking of `new_jobs` vs existing `active_job`, then triggers `run_migration_task.delay(str(job.id))` for each new job inside try/except with logger.warning on dispatch failure; import is local (avoids circular import with migration_tasks.py)
- FIX 3: In `migration_repository.py::update_job_status()`, replaced `.returning(MigrationJob)` ORM approach with: execute UPDATE, commit, then `get_job_by_id(job_id)` SELECT — avoids asyncpg RETURNING ORM compatibility issue
- BONUS: Fixed `migration_tasks.py` — replaced forbidden `get_event_loop().run_until_complete()` with `asyncio.run()` per CLAUDE.md mandatory rule

## Artifacts:
- backend/app/api/v1/admin/router.py
- backend/app/api/v1/admin/migration_service.py
- backend/app/api/v1/admin/migration_repository.py
- backend/app/tasks/migration_tasks.py

## Contracts Verified:
- Pydantic schemas: OK — `List[MigrationJobResponse]` response_model added
- DI via Depends: OK — unchanged
- Circular import: avoided by using local imports inside start_migration()
- Celery task signature: `run_migration_task.delay(str(job.id))` matches task def `def run_migration_task(self, job_id: str)`
- asyncio.run(): OK — migration_tasks.py now uses asyncio.run() instead of get_event_loop()
- ruff: OK (0 errors)
- mypy: not run (no mypy in path)
- pytest: E2E tests — 6 pass, 1 pre-existing failure in test_02_blog.py::test_admin_create_blog_post[chromium] (frontend Playwright/TipTap navigation timeout, unrelated to migration changes; no unit/integration tests exist in tests/ directory)

## Next:
- POST /api/v1/admin/migration/start now returns 200 with List[MigrationJobResponse] JSON
- Migration jobs are now dispatched to Celery workers on creation

## Blockers:
- none
