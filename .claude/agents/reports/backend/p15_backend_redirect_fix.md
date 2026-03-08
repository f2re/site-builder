## Status: DONE

## Completed:
- Added `GET /api/v1/redirects/lookup?old_path=...` endpoint to `redirect_router.py`
  - Accepts full old_path including query string as a Query parameter
  - Resolves the root bug: `/{path:path}` only captures path segment before `?`, losing the query string for OpenCart-style URLs like `/index.php?route=product/category&path=61_67`
- Kept backward-compatible `GET /redirects/{path:path}` endpoint for paths without query string
- Verified `redirect_repository.py` normalization — `get_by_old_path` already adds a leading `/` when missing, which correctly handles both `/index.php?route=...` and `index.php?route=...` inputs
- Added `OCInformation` and `OCInformationDescription` models to `backend/app/db/opencart_models.py` (read-only OC table mappings)
- Created `scripts/seed_redirects.py`:
  - Reads OpenCart categories (`oc_category`, `oc_category_description`) and generates:
    - `/index.php?route=product/category&path={cat_id}` -> `/catalog/{slug}`
    - `/index.php?route=product/category&path={parent_id}_{cat_id}` -> `/catalog/{slug}` (for nested categories)
  - Reads OpenCart products (`oc_product`, `oc_product_description`) and generates:
    - `/index.php?route=product/product&product_id={id}` -> `/shop/{slug}`
  - Reads OpenCart information pages (`oc_information`, `oc_information_description`) and generates:
    - `/index.php?route=information/information&information_id={id}` -> `/blog/{slug}`
  - Slug resolution priority: new-site category/product table (by oc_category_id / oc_product_id) -> slugified OC description name -> fallback ID-based slug
  - Uses PostgreSQL `INSERT ... ON CONFLICT DO UPDATE` (idempotent)
  - `--dry-run` flag prints what would be written without committing
  - `--oc-db-url` override for MySQL connection; falls back to `OC_DB_*` env vars via `settings`

## Artifacts:
- `backend/app/api/v1/pages/redirect_router.py` — added `/lookup` endpoint
- `backend/app/db/opencart_models.py` — added `OCInformation`, `OCInformationDescription`
- `scripts/seed_redirects.py` — new seed script

## Migrations:
- None required — no changes to new-site SQLAlchemy models (`Redirect` model is unchanged, `OCInformation` maps to existing OC tables and uses a separate `OCBase`)

## Contracts Verified:
- Pydantic schemas: OK (RedirectRead already existed, no changes needed)
- DI via Depends: OK
- ruff check app/ --fix: 0 errors
- ruff check ../scripts/seed_redirects.py: 0 errors
- mypy app/ --ignore-missing-imports: Success, no issues
- alembic check: skipped (PostgreSQL not available in local env; no schema changes made)

## Root Cause Summary:
FastAPI's `{path:path}` path parameter captures only the URL path component — everything before `?`. The query string is parsed separately by ASGI and is NOT part of the path. For an OpenCart URL `/index.php?route=product/category&path=61_67`, the handler received only `index.php`, causing every lookup to fail. The fix adds a dedicated `/lookup` endpoint where `old_path` is a regular Query parameter, so the client URL-encodes the full path+query string and passes it intact.

## Usage Example:
```
GET /api/v1/redirects/lookup?old_path=%2Findex.php%3Froute%3Dproduct%2Fcategory%26path%3D61_67
```

## Blockers:
- none
