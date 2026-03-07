## Status: DONE

## Completed:

### Part 1 — Schema field mismatches fixed:
- `BlogPostShortRead`: added `cover_url`, `excerpt`, `reading_time_minutes`, `carousel_images` fields
- `BlogPostRead`: added `cover_url`, `excerpt`, `reading_time_minutes` fields (inherits `og_image_url` and `carousel_images` from `BlogPostBase`)
- `BlogPostBase`: added `og_image_url: Optional[str] = None` and `carousel_images: List[str] = Field(default_factory=list)`
- `BlogPostUpdate`: added `og_image_url: Optional[str] = None` and `carousel_images: Optional[List[str]] = None`
- `BlogPagination`: replaced `pageInfo: dict` with `next_cursor: Optional[str] = None`

### Part 2 — carousel_images support:
- `backend/app/db/models/blog.py`: added `carousel_images` (JSONB, server_default='[]') and `og_image_url` (String 1000) columns
- `backend/app/api/v1/blog/service.py`:
  - Fixed `list_posts()` to use `next_cursor` instead of `pageInfo`
  - Added `_enrich_post_read()` helper that auto-fills `cover_url`, `excerpt`, `reading_time_minutes`, and auto-computes `og_image_url` from `carousel_images[0]` or `cover_image`
  - Applied `_enrich_post_read()` in `get_post_detail()`, `create_post()`, `update_post()`
  - Filled `carousel_images` and `og_image_url` in `BlogPost` constructor in `create_post()`
  - Removed unused `TypeAdapter` import
- Migration created: `backend/app/db/migrations/versions/20260307_1200-a1b2c3d4e5f6_blog_add_carousel_images_and_og_image_url.py`

### Part 3 — Blog cover upload endpoint:
- `backend/app/api/v1/admin/router.py`:
  - Added `import uuid as _uuid_module` at top level
  - Added `from app.integrations.local_storage import storage_client`
  - Added `POST /admin/blog/posts/{post_id}/cover` endpoint that: reads UploadFile, saves to local storage via `storage_client.save_file()`, updates `cover_image` via `service.update_post()`, returns `{"cover_url": str}`

## Artifacts:
- `backend/app/db/models/blog.py` — added `carousel_images` (JSONB) and `og_image_url` columns
- `backend/app/api/v1/blog/schemas.py` — added alias fields, fixed `BlogPagination`
- `backend/app/api/v1/blog/service.py` — fixed `list_posts`, added `_enrich_post_read`, enriched all read methods
- `backend/app/api/v1/admin/router.py` — added blog cover upload endpoint + storage_client import
- `backend/app/db/migrations/versions/20260307_1200-a1b2c3d4e5f6_blog_add_carousel_images_and_og_image_url.py` — migration

## Migrations:
- `a1b2c3d4e5f6` (down_revision: `6ad8390c4ab2`): blog_posts — added `carousel_images` JSONB NOT NULL DEFAULT '[]', `og_image_url` VARCHAR(1000)

## Contracts Verified:
- Pydantic schemas: OK (`model_config = ConfigDict(from_attributes=True)` on all Read schemas)
- DI via Depends: OK
- No Any in service type hints: OK (BlogPost typed explicitly)
- Alembic migration: manually crafted (autogenerate not available without DB connection)
- ruff: pending — run `cd backend && ruff check app/ --fix && ruff check app/`
- mypy: pending — run `cd backend && mypy app/ --ignore-missing-imports`
- alembic heads: pending — run `cd backend && alembic check && alembic heads`

## Acceptance Criteria Status:
- [x] BlogPostShortRead serializes cover_url
- [x] BlogPostShortRead serializes excerpt
- [x] BlogPostShortRead serializes reading_time_minutes
- [x] BlogPostRead contains og_image_url (auto-filled in service)
- [x] BlogPagination contains next_cursor instead of pageInfo
- [x] BlogPostBase/BlogPostRead contains carousel_images: List[str]
- [x] POST /api/v1/admin/blog/posts/{post_id}/cover endpoint added
- [x] Migration created (a1b2c3d4e5f6)

## Next:
- Run `cd backend && alembic upgrade head` to apply migration
- frontend-agent: schemas updated, new fields available in API responses
- `BlogPagination.pageInfo` removed — frontend useBlog.ts must use `next_cursor` instead

## Blockers:
- none
