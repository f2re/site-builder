## Status: DONE

## Completed:
- Fixed bug in `create_post`: was passing `data.title` as `display_name` to `get_or_create_author`; now loads `User` from DB and uses `user.full_name or user.email.split('@')[0]`
- Added `author_id: Optional[UUID]` to `BlogPostBase` — if set, uses that existing Author directly (404 if not found)
- Added `user_id: UUID` field to `AuthorRead` schema so frontend can identify the current user's author
- Added `AuthorUpdate` schema with optional `display_name`, `bio`, `avatar_url`
- Added `get_author_by_id` and `get_all_authors` methods to `BlogRepository` (get_all_authors JOINs users WHERE role IN ('admin','manager'))
- Added `list_authors` and `update_author_profile` methods to `BlogService`
- Added `require_admin_or_manager` dependency to `core/dependencies.py`
- Added three new endpoints in `blog/router.py`:
  - `GET /blog/admin/authors` — list all admin/manager authors
  - `GET /blog/admin/authors/me` — get/create current user's Author profile
  - `PUT /blog/admin/authors/me` — update current user's Author profile
- Updated `POST /blog/posts` to use `require_admin_or_manager` (managers can now publish posts)

## Artifacts:
- backend/app/core/dependencies.py — added `require_admin_or_manager`
- backend/app/api/v1/blog/schemas.py — added `user_id` to `AuthorRead`, added `AuthorUpdate`, added `author_id` to `BlogPostBase`
- backend/app/api/v1/blog/repository.py — added `get_author_by_id`, `get_all_authors`
- backend/app/api/v1/blog/service.py — fixed `create_post` bug, added `list_authors`, `update_author_profile`
- backend/app/api/v1/blog/router.py — added 3 author endpoints, updated `POST /posts` to allow managers

## Contracts Verified:
- Pydantic schemas: OK (from_attributes=True on all Read schemas)
- DI via Depends: OK (require_admin_or_manager, get_blog_service)
- session.commit() called in all mutating service methods: OK
- selectinload/refresh used after mutations: OK
- ruff: 0 errors
- mypy: no issues (172 source files)

## Next:
- Frontend can use `GET /blog/admin/authors` to populate author selector in post editor
- Frontend uses `user_id` in `AuthorRead` to pre-select current user's author
- No migrations needed (no model schema changes)

## Blockers:
- none
