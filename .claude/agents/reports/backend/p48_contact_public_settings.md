## Status: DONE

## Completed:
- Added public endpoint `GET /contact/settings` to `backend/app/api/v1/contact/router.py`
- Endpoint returns only `contact_page_text`; `contact_email` is suppressed (set to None) to avoid exposing internal addresses
- No changes to schemas, service, or repository — `SiteSettingsResponse` and `get_contact_settings()` were already correct

## Artifacts:
- backend/app/api/v1/contact/router.py

## Contracts Verified:
- Pydantic schemas: OK — `SiteSettingsResponse` used as response_model
- DI via Depends: OK — `get_contact_service` dependency injected
- No auth dependency on new endpoint: OK
- ruff: OK
- mypy: OK (172 files, no issues)

## Next:
- frontend-agent: `GET /api/v1/contact/settings` is now publicly accessible — no Authorization header required
- Response shape: `{ "contact_email": null, "contact_page_text": "<text or null>" }`

## Blockers:
- none
