## Status: DONE

## Completed:
- **Backend #1 (Product Options)**:
  - Added `ProductOptionGroup` and `ProductOptionValue` models.
  - Implemented repository methods for CRUD and price calculation.
  - Added `calculate_price` logic to `ProductService`.
  - Registered Admin CRUD endpoints and public calculation endpoint.
  - Fixed `ProductVariant.price` type hint to `Decimal`.
  - Added `type` field to `ProductOptionGroup` with migration.
- **Backend #2 (Cart Options)**:
  - Added `selected_options` JSONB field to `CartItem` and `OrderItem` models.
  - Created migration for `selected_options`.
  - Refactored `CartService` to support composite keys (`variant_id:options`) in Redis.
  - Updated Cart and Order schemas to include selected options snapshots.
  - Updated `OrderService` to copy options from cart to order items.
- **Frontend (Product Options UI & Admin)**:
  - Updated `useProducts` and `useCart` composables.
  - Implemented `ProductOptionsManager.vue` component for admin.
  - Updated Product Page with options selector and reactive price calculation.
  - Updated Cart Page and Quick Buy Modal to support and display options.
  - Updated Checkout Page summary to show selected options.

## Artifacts:
- `backend/app/db/models/product.py` & `cart.py` & `order.py`
- `backend/app/api/v1/products/service.py` & `repository.py` & `router.py` & `schemas.py`
- `backend/app/api/v1/cart/service.py` & `router.py` & `schemas.py`
- `backend/app/api/v1/orders/service.py` & `schemas.py`
- `frontend/components/Admin/ProductOptionsManager.vue`
- `frontend/pages/products/[slug].vue`
- `frontend/pages/cart.vue`
- `frontend/pages/checkout/index.vue`
- `frontend/components/shop/QuickBuyModal.vue`
- `backend/app/db/migrations/versions/20260308_1601-e2f3a4b5c6d7_cart_add_selected_options.py`
- `backend/app/db/migrations/versions/20260308_1602-f3a4b5c6d7e8_add_type_to_option_groups.py`

## Contracts Verified:
- Pydantic models: ✅
- Alembic migrations: ✅
- Linting (ruff/eslint): ✅
- Type-checking (mypy/vue-tsc): ✅

## Next:
- Push all changes to remote repository.
- Verify full checkout flow with product options.
