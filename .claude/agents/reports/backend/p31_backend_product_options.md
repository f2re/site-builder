## Status: DONE

## Completed:
- **Models** — `ProductOptionGroup` and `ProductOptionValue` exist in `backend/app/db/models/product.py`; `Product.option_groups` relationship added with `cascade="all, delete-orphan"` and `order_by="ProductOptionGroup.sort_order"`
- **Migration** — `20260308_1600-d1e2f3a4b5c6_products_add_option_groups.py` with `down_revision='6c70172e87c6'` creates both tables with indexes; subsequent migrations add `type` column and `selected_options` to cart/order items
- **Schemas** — `ProductOptionValueSchema`, `ProductOptionGroupSchema`, `ProductOptionValueCreate/Update`, `ProductOptionGroupCreate/Update`, `ProductPriceCalculationRequest/Response` all in `products/schemas.py`; `ProductRead.option_groups: List[ProductOptionGroupSchema] = []`
- **Repository** — `get_by_id` and `get_by_slug` eager-load `selectinload(Product.option_groups).selectinload(ProductOptionGroup.values)`; CRUD methods for option groups and values implemented; `get_option_values_by_ids` with selectinload of group
- **Service** — `ProductService.calculate_price()` validates required groups, computes `base_price + sum(modifiers)`, returns breakdown
- **Admin endpoints** — `POST/PUT/DELETE /admin/products/{product_id}/option-groups` and `POST/PUT/DELETE /admin/products/option-groups/{group_id}/values` registered in `admin/router.py`, protected by `require_admin`; structlog logging added: `logger.info("admin_action", admin_id=..., action=..., target_id=...)`
- **Public endpoint** — `POST /products/calculate-price` in `products/router.py` delegates to `ProductService.calculate_price()`
- **Bug fix** — Added missing `AsyncSessionLocal` import in `app/tasks/media.py` (pre-existing error unrelated to this task)

## Artifacts:
- `/Users/meteo/Documents/WWW/site-builder/backend/app/db/models/product.py`
- `/Users/meteo/Documents/WWW/site-builder/backend/app/api/v1/products/schemas.py`
- `/Users/meteo/Documents/WWW/site-builder/backend/app/api/v1/products/service.py`
- `/Users/meteo/Documents/WWW/site-builder/backend/app/api/v1/products/repository.py`
- `/Users/meteo/Documents/WWW/site-builder/backend/app/api/v1/products/router.py`
- `/Users/meteo/Documents/WWW/site-builder/backend/app/api/v1/admin/router.py`
- `/Users/meteo/Documents/WWW/site-builder/backend/app/db/migrations/versions/20260308_1600-d1e2f3a4b5c6_products_add_option_groups.py`
- `/Users/meteo/Documents/WWW/site-builder/backend/app/tasks/media.py` (bug fix)

## Migrations:
- Revision `d1e2f3a4b5c6` (`down_revision='6c70172e87c6'`): creates `product_option_groups` (with `ix_product_option_groups_product_id`) and `product_option_values` (with `ix_product_option_values_group_id`)
- Revision `e2f3a4b5c6d7` (`down_revision='d1e2f3a4b5c6'`): adds `selected_options` JSONB to `cart_items` and `order_items`
- Revision `de2e19023b3b` (`down_revision='e2f3a4b5c6d7'`): adds `doc_iframe_url` to `products`
- Revision `f3a4b5c6d7e8` (`down_revision='de2e19023b3b'`): adds `type` column to `product_option_groups`
- Current head: `f6f189d8f825`

## Contracts Verified:
- Pydantic schemas: OK (`from_attributes=True` on all read schemas)
- DI via Depends: OK
- selectinload for option_groups + values: OK
- await session.commit() in all mutating service methods: OK
- structlog logging in all admin option endpoints: OK
- ruff: OK (0 errors)
- mypy: OK (0 issues, 152 files checked)
- alembic heads: 1 head (f6f189d8f825) — OK
- alembic check: requires live DB (not available locally — expected)

## Blockers:
- none
