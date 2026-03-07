## Status: DONE

## Completed:
- BUG-BE-01: Added `stock: int = 0` to `ProductRead` with `@model_validator(mode='after')` that computes `sum(v.stock_quantity for v in self.variants)`
- BUG-BE-02: Implemented `tiptap_json_to_html(content_json)` in `app/core/utils.py` — traverses TipTap AST and generates HTML (paragraph→`<p>`, heading→`<h2>`/`<h3>`, bulletList→`<ul><li>`, orderedList→`<ol><li>`, image→`<img src=...>`, inline marks bold/italic/code), sanitized via `bleach`. Wired into `create_product` and `update_product` in `service.py` — auto-generates `description_html` only when `content_json` is non-empty and `description_html` was NOT provided explicitly.
- BUG-BE-03: Added `category_slug: Optional[str] = Query(None)` to `router.py`; propagated through `service.get_products()` and `repository.list_products()`. In repository: when `category_slug` is set (and `category_id` is not), performs a JOIN with `Category` and filters by `Category.slug == category_slug`. `category_id` takes priority.
- BUG-BE-04: Created `CategoryListResponse(BaseModel)` schema with `items: List[CategoryTreeRead]`. Changed `GET /api/v1/products/categories` response_model to `CategoryListResponse`, endpoint now returns `CategoryListResponse(items=categories)`.

## Artifacts:
- `backend/app/api/v1/products/schemas.py` — added `stock` field + `@model_validator`, added `CategoryListResponse`
- `backend/app/api/v1/products/service.py` — added `category_slug` param to `get_products`, wired `tiptap_json_to_html` in create/update
- `backend/app/api/v1/products/repository.py` — added `category_slug` param with join/filter logic
- `backend/app/api/v1/products/router.py` — added `category_slug` query param, changed categories endpoint response
- `backend/app/core/utils.py` — added `tiptap_json_to_html`, `_render_node`, `_render_inline`, `bleach` import

## Contracts Verified:
- Pydantic schemas: OK (`model_validator` mode='after', `from_attributes=True`)
- DI via Depends: OK
- No hardcoded secrets: OK
- Auto-generation logic: only triggers when `content_json` present AND `description_html` not explicitly set
- ruff: OK (0 errors after --fix)
- mypy: OK (Success: no issues found in 124 source files)

## Test Results:
- `ruff check app/ --fix && ruff check app/` → All checks passed
- `mypy app/ --ignore-missing-imports` → Success: no issues found in 124 source files
- E2E test `test_admin_delete_product` fails (pre-existing — missing `data-testid='admin-delete-btn'` in frontend Vue component, unrelated to this task)

## Next:
- Frontend team can now rely on:
  - `GET /api/v1/products/{slug}` returning `stock` field (integer, sum of all variants)
  - `GET /api/v1/products?category_slug=obd-adaptery` for slug-based category filtering
  - `GET /api/v1/products/categories` returning `{items: [...]}`
  - `description_html` auto-generated from `content_json` on save

## Blockers:
- none
