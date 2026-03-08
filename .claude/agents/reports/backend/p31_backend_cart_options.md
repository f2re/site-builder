## Status: DONE

## Completed:
- Added `selected_options` JSONB field to `CartItem` and `OrderItem` models.
- Created migration for `selected_options`.
- Refactored `CartService` to support composite keys (`variant_id:options`) in Redis.
- Updated Cart and Order schemas to include selected options snapshots.
- Updated `OrderService` to copy options from cart to order items.

## Next:
- Frontend selection of options.
