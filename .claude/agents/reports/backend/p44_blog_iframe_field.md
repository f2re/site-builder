## Status: DONE

## Completed:
- Added `doc_iframe_url: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)` to `BlogPost` model
- Added `doc_iframe_url: Optional[str] = None` to `BlogPostBase` schema (covers `BlogPostCreate` and `BlogPostRead` by inheritance)
- Added `doc_iframe_url: Optional[str] = None` to `BlogPostUpdate` schema
- Created Alembic migration `20260315_1500-blog_add_doc_iframe_url_to_blog_posts.py`

## Artifacts:
- `backend/app/db/models/blog.py` — field added to `BlogPost` (after `og_image_url`)
- `backend/app/api/v1/blog/schemas.py` — field added to `BlogPostBase` and `BlogPostUpdate`
- `backend/app/db/migrations/versions/20260315_1500-blog_add_doc_iframe_url_to_blog_posts.py`

## Migrations:
- `20260315_1500`: `op.add_column("blog_posts", Column("doc_iframe_url", String(2000), nullable=True))`
- Revises: `20260315_1400` (previous head)

## Contracts Verified:
- Pydantic schemas: OK
- ruff: OK (0 errors)
- mypy: OK (no issues, 172 source files)
- alembic: migration created manually (DB not available locally — standard dev environment)

## Next:
- none — self-contained field addition

## Blockers:
- none
