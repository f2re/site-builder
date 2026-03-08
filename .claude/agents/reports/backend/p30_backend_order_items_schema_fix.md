## Status: DONE

## Completed:
- Fixed `OrderItemRead` in `backend/app/api/v1/orders/schemas.py`: added three brief Pydantic schemas (`ProductImageBrief`, `ProductBrief`, `ProductVariantBrief`) and declared `product_variant: Optional[ProductVariantBrief] = None` as an explicit field.
- Replaced fragile `hasattr(self, "product_variant")` guards in `@computed_field` methods with direct `if self.product_variant` checks — now that the field is properly declared, Pydantic v2 populates it from the ORM relationship via `from_attributes=True`.
- Removed inline `from app.api.v1.orders.schemas import OrderRead` inside `list_orders` handler body; moved to top-level import.
- Added `response_model=OrderRead` to `GET /admin/orders/{order_id}` endpoint in `backend/app/api/v1/admin/router.py`.

## Root Cause Analysis:
Pydantic v2 with `model_config = ConfigDict(from_attributes=True)` only populates fields that are explicitly declared in the schema. `product_variant` was accessed via `@computed_field` using `hasattr(self, 'product_variant')`, but since it was not declared as a schema field, it was never populated from the ORM object — `hasattr` always returned `False`, and all three computed fields fell through to their fallback values (`"Unknown Product"`, `None`, `None`).

## Diagnosis: Empty `items` for Migrated Orders
Orders imported from OpenCart (the migration service) have `total_amount` set directly but no rows in the `order_items` table. This is correct behavior — the migration service populates the order header fields but does not create `OrderItem` records for historical line-items. The `items: []` response for such orders is therefore expected and not a backend bug. The `selectinload(Order.items)` chain in `OrderRepository.get_by_id()` is correct; it simply returns an empty list when no `order_items` rows exist for a given `order_id`.

## Repository State:
`OrderRepository.get_by_id()`, `get_user_orders()`, and `list_all()` all already include the full selectinload chain:
```
selectinload(Order.items)
  .selectinload(OrderItem.product_variant)
  .selectinload(ProductVariant.product)
  .selectinload(Product.images)
```
No changes were required in the repository.

## Artifacts:
- `backend/app/api/v1/orders/schemas.py` — added `ProductImageBrief`, `ProductBrief`, `ProductVariantBrief`; `OrderItemRead.product_variant` declared explicitly
- `backend/app/api/v1/admin/router.py` — added `response_model=OrderRead` to `GET /admin/orders/{order_id}`; moved `OrderRead` import to module level

## Contracts Verified:
- Pydantic schemas: OK — `from_attributes=True` on all brief schemas
- DI via Depends: OK
- ruff: OK (0 errors)
- mypy: OK (0 issues in 146 source files)
- pytest unit tests: 10 passed

## Next:
- Frontend can rely on `GET /api/v1/admin/orders/{id}` now returning `items[].product_name`, `items[].sku`, `items[].image_url` populated from the product relationship for orders with actual line items.

## Blockers:
- none
