## Status: DONE

## Completed:
- Fix 1: Added `DELETE /api/v1/admin/migration/reset` endpoint in `backend/app/api/v1/admin/router.py`
- Fix 1: Implemented `MigrationService.reset_migration()` — deletes all migrated orders (with order items), products (cascade), blog posts (oc_product_id IS NOT NULL), categories (oc_category_id IS NOT NULL, parent_id nullified first), and all MigrationJob rows
- Fix 2: Added `OCProductImage` model to `backend/app/db/opencart_models.py` with fields: product_image_id, product_id, image, sort_order
- Fix 3: Added `oc_product_id: Optional[int]` field (nullable, indexed) to `BlogPost` model in `backend/app/db/models/blog.py`
- Fix 3: Created Alembic migration `20260308_1000-b2c3d4e5f6a7_blog_add_oc_product_id.py` (adds column + index, down_revision = a1b2c3d4e5f6)
- Fix 4a: Blog-category detection — built `blog_category_oc_ids` set from OCCategoryDescription names matching keywords: новости, статьи, инструкции, blog, news, articles, статья, новость
- Fix 4b: Product vs BlogPost routing in migrate_catalog() — products linked to blog categories become BlogPost rows
- Fix 4b: BlogPost creation with idempotency check on oc_product_id, author lookup (first Author → first admin User → create Author → skip with warning if none), tag parsing from meta_keyword + "импорт" tag
- Fix 4c: Additional images from OCProductImage fetched after cover image, saved as ProductImage(is_cover=False)
- Fix 4d: Product.description = bleach.clean(html, tags=[], strip=True) for plain-text; description_html retains raw HTML
- Fix 4e: Meilisearch sync triggered via `sync_products_to_meilisearch.delay()` after each batch commit (non-critical, wrapped in try/except)
- Added `import bleach` and `from sqlalchemy import delete` to migration_service.py
- Added `OCProductImage` import in migration_service.py
- Added `Author, BlogPost, BlogPostStatus, Tag` imports from blog models

## Artifacts:
- `backend/app/db/opencart_models.py` — added OCProductImage model
- `backend/app/db/models/blog.py` — added oc_product_id field
- `backend/app/db/migrations/versions/20260308_1000-b2c3d4e5f6a7_blog_add_oc_product_id.py` — new migration
- `backend/app/api/v1/admin/migration_service.py` — reset_migration(), rewritten migrate_catalog()
- `backend/app/api/v1/admin/router.py` — DELETE /migration/reset endpoint

## Migrations:
- `20260308_1000-b2c3d4e5f6a7_blog_add_oc_product_id`: adds `oc_product_id INTEGER NULL` column + index to `blog_posts` table
- Single head confirmed: `b2c3d4e5f6a7`

## Contracts Verified:
- Pydantic schemas: OK (no new schemas needed — endpoint returns dict)
- DI via Depends: OK (require_admin via AdminDep)
- No Any in new code: OK
- All admin endpoints use require_admin: OK
- CDEK integration: not touched

## Verification:
- ruff check app/: All checks passed (0 errors)
- mypy app/ --ignore-missing-imports: Success — no issues in 125 source files
- pytest tests/ -x -v: 13 passed in 3.91s
- alembic chain: exactly 1 head (b2c3d4e5f6a7), linear chain confirmed

## Next:
- frontend-agent: DELETE /api/v1/admin/migration/reset is available (requires admin Bearer token)
- Alembic migration b2c3d4e5f6a7 must be applied on next `alembic upgrade head`

## Blockers:
- none
