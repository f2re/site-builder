## Status: DONE

## Completed:
- Added `BlogSection(str, enum.Enum)` with values `NEWS='news'` and `INSTRUCTIONS='instructions'` to `backend/app/db/models/blog.py`
- Added `section: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default=None)` to `BlogCategory` model
- Added `BlogSection` enum and `section: Optional[str] = None` field to `BlogCategoryRead`, `BlogCategoryCreate`, `BlogCategoryUpdate` schemas
- Added `category: Optional[BlogCategoryRead] = None` field to `BlogPostShortRead` (critical fix — category was missing from post cards)
- Added `section: Optional[str] = Query(None)` parameter to `GET /blog/categories` and `GET /blog/posts` router endpoints
- Added `section` parameter to admin `GET /blog/admin/categories` endpoint
- Updated `service.list_posts()` to accept and pass `section` to repository
- Updated `service.list_categories()` to accept and pass `section` to repository
- Updated `service.create_category()` to set `section` field from `BlogCategoryCreate`
- Updated `repository.list_posts()` to filter by `BlogCategory.section` via JOIN when `section` is provided
- Updated `repository.get_categories_with_count()` to accept `section` param and apply WHERE filter
- Created Alembic migration `20260315_1000-blog_add_section_to_blog_categories.py` with `ALTER TABLE blog_categories ADD COLUMN section VARCHAR(20) NULL`

## Artifacts:
- `backend/app/db/models/blog.py` — BlogSection enum + section field on BlogCategory
- `backend/app/api/v1/blog/schemas.py` — BlogSection enum, section in category schemas, category in BlogPostShortRead
- `backend/app/api/v1/blog/router.py` — section query param on list_posts and list_categories
- `backend/app/api/v1/blog/service.py` — section propagation in list_posts, list_categories, create_category
- `backend/app/api/v1/blog/repository.py` — section filter in list_posts and get_categories_with_count
- `backend/app/db/migrations/versions/20260315_1000-blog_add_section_to_blog_categories.py`

## Migrations:
- `20260315_1000`: blog_categories ADD COLUMN section VARCHAR(20) NULL; down: DROP COLUMN section
- Chain: `20260315_0910` → `20260315_1000` (head)
- `alembic heads` → exactly 1 head: `20260315_1000`

## Contracts Verified:
- Pydantic schemas: OK (from_attributes=True, all category schemas have section)
- DI via Depends: OK
- selectinload(BlogPost.category): already present in repository.list_posts — category populated on ORM level, BlogPostShortRead.model_validate picks it up via from_attributes
- No Any in type hints (blog module): OK
- ruff: 0 errors
- mypy: 0 issues (163 source files)
- alembic heads: 1 head

## Next:
- Frontend-agent: `GET /api/v1/blog/categories?section=news` and `GET /api/v1/blog/posts?section=instructions` are ready
- `BlogPostShortRead.category` field is now populated — frontend blog card components can display category name and section
- Migration must be applied in production: `alembic upgrade head` (requires running PostgreSQL)

## Blockers:
- none
