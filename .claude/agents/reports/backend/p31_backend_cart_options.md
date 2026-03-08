## Status: DONE

## Completed:
- Verified `CartItem.selected_options` JSONB field already present in `backend/app/db/models/cart.py` (JSON with JSONB variant, server_default='[]', default=list)
- Verified migration `20260308_1601-e2f3a4b5c6d7_cart_add_selected_options.py` already exists in the chain (revises d1e2f3a4b5c6, included in head f6f189d8f825)
- Verified `CartItemCreate.selected_option_value_ids: List[UUID]` already present in schemas
- Verified `CartService.add_item` already builds option snapshots from `ProductOptionValue` with HTTP 422 validation on invalid IDs
- Added `SelectedOptionSnapshot` Pydantic model to `backend/app/api/v1/cart/schemas.py` with typed fields: `group_id: UUID`, `group_name: str`, `value_id: UUID`, `value_name: str`, `price_modifier: float`
- Updated `CartItemResponse.selected_options` from `List[dict]` to `List[SelectedOptionSnapshot]` for strong typing
- Updated `CartItemCreate.selected_option_value_ids` to use `Field(default_factory=list)` (avoids mutable default antipattern)

## Artifacts:
- `backend/app/api/v1/cart/schemas.py` — updated: added `SelectedOptionSnapshot`, updated `CartItemResponse`, fixed mutable default

## Previously completed (no changes needed):
- `backend/app/db/models/cart.py` — `selected_options` field already present
- `backend/app/db/migrations/versions/20260308_1601-e2f3a4b5c6d7_cart_add_selected_options.py` — migration already present
- `backend/app/api/v1/cart/service.py` — option snapshot logic already implemented

## Migrations:
- `e2f3a4b5c6d7` (20260308_1601): `selected_options JSONB DEFAULT '[]'` on `cart_items` and `order_items` — in chain, no new migration needed

## Contracts Verified:
- Pydantic schemas: OK — `SelectedOptionSnapshot` matches snapshot format `{group_id, group_name, value_id, value_name, price_modifier}`
- CartItemCreate: `selected_option_value_ids: List[UUID] = Field(default_factory=list)` — OK
- CartItemResponse: `selected_options: List[SelectedOptionSnapshot]` — strongly typed
- Service validation: HTTP 422 raised when value_ids count mismatch — OK
- DI via Depends: OK
- ruff: OK (0 errors)
- mypy: OK (0 issues, 152 source files)
- pytest: OK (49 passed, including test_cart_options_flow)
- alembic heads: f6f189d8f825 (single head, DB not available in dev environment)

## Next:
- frontend-agent: `POST /api/v1/cart/add` accepts `selected_option_value_ids: List[UUID]` in request body; `GET /api/v1/cart` returns `selected_options: List[SelectedOptionSnapshot]` per item

## Blockers:
- none
