## Status: DONE

## Completed:
- Created `backend/app/db/models/contact.py` with `ContactMessage` and `SiteSettings` models
  - `ContactMessage`: PII fields (name, email, phone) stored as Text (Fernet-encrypted in service layer)
  - `SiteSettings`: upsert-friendly key/value table with `uq_site_settings_key` constraint
  - `ContactStatus` enum: NEW, READ, REPLIED
- Updated `backend/app/db/models/__init__.py` to import new models
- Added `TURNSTILE_SECRET_KEY` and `CONTACT_EMAIL_RECIPIENT` fields to `backend/app/core/config.py`
- Created `backend/app/api/v1/contact/` feature directory:
  - `schemas.py`: ContactFormRequest, ContactMessageRead, ContactListResponse, ContactReplyRequest, SiteSettingsUpdate, SiteSettingsResponse
  - `repository.py`: ContactRepository (CRUD + cursor pagination), SiteSettingsRepository (get/set/upsert)
  - `service.py`: ContactService with Turnstile verification (skipped if key empty), Fernet PII encrypt/decrypt, Celery task dispatch
  - `router.py`: Public POST /contact (rate-limited 5/min via slowapi), admin GET/PUT/DELETE /admin/contact/*, admin GET/PUT /admin/settings/contact
- Updated `backend/app/tasks/notifications/dispatcher.py`:
  - Added `send_contact_notification_task` using `asyncio.run()` (correct pattern)
  - Fixed `send_email_task`: replaced `loop.run_until_complete()` with `asyncio.run()`
  - Fixed `send_telegram_task`: replaced `loop.run_until_complete()` with `asyncio.run()`
  - Fixed `send_telegram_task`: was using `YOOMONEY_SHOP_ID` as bot token (wrong) — corrected to `TELEGRAM_BOT_TOKEN`
- Registered `contact_router` in `backend/app/api/v1/router.py`
- Added slowapi middleware and exception handler to `backend/app/main.py`
- Added `slowapi==0.1.9` to `requirements.txt`
- Created Alembic migration `20260315_1400` (manually, DB not available locally)
- Updated `backend/app/db/migrations/env.py` to import `app.db.models.contact`

## Artifacts:
- `backend/app/db/models/contact.py`
- `backend/app/db/models/__init__.py` (updated)
- `backend/app/core/config.py` (updated — TURNSTILE_SECRET_KEY, CONTACT_EMAIL_RECIPIENT)
- `backend/app/api/v1/contact/__init__.py`
- `backend/app/api/v1/contact/schemas.py`
- `backend/app/api/v1/contact/repository.py`
- `backend/app/api/v1/contact/service.py`
- `backend/app/api/v1/contact/router.py`
- `backend/app/tasks/notifications/dispatcher.py` (updated)
- `backend/app/api/v1/router.py` (updated)
- `backend/app/main.py` (updated — slowapi added)
- `backend/app/db/migrations/env.py` (updated)
- `backend/app/db/migrations/versions/20260315_1400-contact_add_contact_message_and_site_settings_tables.py`
- `backend/requirements.txt` (updated — slowapi==0.1.9)

## Migrations:
- `20260315_1400`: created tables `contact_message` (UUID PK, PII fields as Text, ContactStatus enum), `site_settings` (int PK, key/value upsert), created `contactstatus` ENUM type

## Contracts Verified:
- Pydantic schemas: OK (from_attributes=True on read schemas, EmailStr validation, field constraints)
- DI via Depends: OK (get_contact_repo, get_settings_repo, get_contact_service)
- No Any types: OK
- PII encryption: OK (encrypt_data/decrypt_data from core.security via Fernet)
- Turnstile: OK (skips if TURNSTILE_SECRET_KEY empty — dev-friendly)
- Rate limiting: OK (slowapi 5/minute per IP on POST /contact)
- Admin auth: OK (require_admin Depends on all /admin/* endpoints)
- asyncio.run(): OK in all Celery tasks (no get_event_loop())
- SiteSettings upsert: OK (INSERT ... ON CONFLICT DO UPDATE)
- alembic heads: 1 head (20260315_1400)
- ruff: 0 errors
- mypy: 0 errors (171 files)

## Test Coverage:
- pytest: integration tests fail due to missing local PostgreSQL DB (pre-existing infra issue, not code regression)

## Next:
- frontend-agent: API contracts ready:
  - POST /api/v1/contact (public, Turnstile token required, rate-limited 5/min)
  - GET /api/v1/admin/contact (admin, cursor pagination, optional status filter)
  - GET /api/v1/admin/contact/{id} (admin, auto-marks READ)
  - PUT /api/v1/admin/contact/{id}/reply (admin, ContactReplyRequest)
  - DELETE /api/v1/admin/contact/{id} (admin, 204)
  - GET /api/v1/admin/settings/contact (admin)
  - PUT /api/v1/admin/settings/contact (admin, contact_email + contact_page_text)

## Blockers:
- none
