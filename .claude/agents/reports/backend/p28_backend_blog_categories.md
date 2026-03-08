## Status: DONE

## Completed:
- Fixed blog pagination cursor bug: replaced broken `WHERE id > cursor ORDER BY id` (UUID v4 comparison) with stable composite cursor by `(published_at DESC, id DESC)`
- Cursor is now base64-encoded JSON: `{published_at: ISO, id: UUID}` — functions `_encode_cursor` / `_decode_cursor` added to repository
- WHERE clause uses explicit OR/AND composite condition: `published_at < cursor_ts OR (published_at = cursor_ts AND id < cursor_id)` — avoids mypy issues with SQLAlchemy `tuple_()` typing
- `next_cursor` is null when no more posts exist (len(posts) <= per_page)
- `cursor: Optional[UUID]` → `cursor: Optional[str]` updated across repository, service, router
- `GET /api/v1/blog/categories` now has `response_model=List[BlogCategoryRead]` and returns `posts_count` (published posts count per category)
- Added `BlogCategoryRead.posts_count: int = 0` field to schemas
- Added `BlogCategoryCreate` and `BlogCategoryUpdate` schemas
- Added repository methods: `get_categories_with_count()`, `get_category_by_id()`, `get_category_by_slug()`, `create_category()`, `update_category()`, `delete_category()`
- Added service methods: `list_categories()` (updated), `create_category()`, `update_category()`, `delete_category()`
- Added admin CRUD endpoints in router: `GET/POST /api/v1/blog/admin/categories`, `PUT/DELETE /api/v1/blog/admin/categories/{category_id}`
- Updated `api_contracts.md` to v2.1 with blog categories and fixed pagination contract

## Artifacts:
- `backend/app/api/v1/blog/repository.py` — fixed pagination, added cursor helpers, category CRUD methods
- `backend/app/api/v1/blog/schemas.py` — added `posts_count` to `BlogCategoryRead`, new `BlogCategoryCreate`/`BlogCategoryUpdate`
- `backend/app/api/v1/blog/service.py` — fixed cursor type, updated `list_categories()`, added category CRUD methods
- `backend/app/api/v1/blog/router.py` — fixed cursor types, added response_model, added admin category CRUD endpoints
- `tests/unit/test_blog_pagination.py` — 6 unit tests for cursor encode/decode
- `.claude/agents/contracts/api_contracts.md` — updated to v2.1

## Migrations:
- None required — no schema changes (model `BlogCategory` already exists)

## Contracts Verified:
- Pydantic schemas: OK (`from_attributes=True`, no `Any` in new code)
- DI via Depends: OK
- ruff: OK (0 errors)
- mypy: OK (0 issues in blog module)
- pytest: 10 passed (6 new + 4 existing)

## Next:
- frontend-agent: `GET /api/v1/blog/categories` now returns `posts_count` field — update composable if needed
- frontend-agent: pagination cursor changed from `UUID` to opaque `string` — composable `after` param is already string-typed, no breaking change
- Admin panel: `GET/POST /api/v1/blog/admin/categories`, `PUT/DELETE /api/v1/blog/admin/categories/{id}` available for `/admin/blog/categories` page

## Blockers:
- none
