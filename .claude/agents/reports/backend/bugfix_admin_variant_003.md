## Status: DONE

## Problem
`PUT /api/v1/admin/products/{id}` returned 422 when frontend sent variants without `id`:
```
{"detail":[{"type":"missing","loc":["body","variants",0,"id"],"msg":"Field required"}]}
```
Root cause: `ProductUpdate.variants` used `List[ProductVariantRead]` which requires `id: UUID` as mandatory field. Frontend sends variants without `id` when creating new ones during product edit.

## Completed

- Added `ProductVariantUpdate(ProductVariantBase)` schema with `id: Optional[UUID] = None`
- Changed `ProductUpdate.variants` from `Optional[List[ProductVariantRead]]` to `Optional[List[ProductVariantUpdate]]`
- Added `create_variant()` method to `ProductRepository` for creating new variants
- Updated `ProductService.update_product()` to handle both cases:
  - variant with `id` — update existing via `repo.update_variant()`
  - variant without `id` — create new via `repo.create_variant()`
- Also fixed: existing update path now correctly excludes `id` field from update kwargs

## Artifacts

- `backend/app/api/v1/products/schemas.py` — added `ProductVariantUpdate`, updated `ProductUpdate.variants`
- `backend/app/api/v1/products/repository.py` — added `create_variant()` method
- `backend/app/api/v1/products/service.py` — split variant handling: update vs create branch

## No Migration Required
No SQLAlchemy model changes — only Pydantic schemas and service/repository logic.

## Contracts Verified

- Pydantic schemas: OK — `ProductVariantUpdate` accepts variant without `id`, validates correctly
- DI via Depends: OK — no changes to dependency wiring
- ruff: OK (0 errors after auto-fix of 1 unrelated issue)
- mypy: OK (0 issues in 124 source files)
- pytest: E2E tests only exist (require live server) — skipped per infrastructure constraints
- alembic: DB not running locally — not applicable (no model changes)

## Verification

```
python -c "from app.api.v1.products.schemas import ProductUpdate; p = ProductUpdate(variants=[{'name':'Default','sku':'23','price':'12.00','stock_quantity':1,'attributes':{}}]); print(p.variants)"
# => [ProductVariantUpdate(name='Default', sku='23', price=Decimal('12.00'), stock_quantity=1, attributes={}, id=None)]
```

## Next

- Frontend can send variants without `id` — 422 resolved
- Variants with `id` still update existing records as before
- New variants (no `id`) are created and linked to the product

## Blockers

- none
