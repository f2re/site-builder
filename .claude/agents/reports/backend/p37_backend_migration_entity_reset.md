## Status: DONE

## Completed:
- Added `reset_entity(self, entity: MigrationEntity) -> Dict[str, str]` method to `MigrationService`
- Added `DELETE /admin/migration/reset/{entity}` endpoint to admin router
- New endpoint placed BEFORE `DELETE /migration/reset` to avoid FastAPI route conflict
- Added `MigrationEntity` import to `router.py`

## Artifacts:
- `backend/app/api/v1/admin/migration_service.py` — new `reset_entity` method (~line 427)
- `backend/app/api/v1/admin/router.py` — new endpoint at line 1310, import at line 65

## Entity Reset Logic:
- `users`: deletes DeliveryAddress, user_device_complectations, UserDevice, then User (role=customer, is_superuser=False)
- `categories`: nullifies parent_id on children referencing migrated cats, then deletes Category where oc_category_id IS NOT NULL
- `products`: deletes Product where oc_product_id IS NOT NULL (cascade removes variants/images via FK)
- `images`: deletes ProductImage for products where oc_product_id IS NOT NULL (no physical file removal)
- `orders`: deletes OrderItem for migrated orders first, then Order where oc_order_id IS NOT NULL
- `blog`: deletes BlogPost where oc_product_id IS NOT NULL
- `addresses`: deletes DeliveryAddress where oc_address_id IS NOT NULL
- `devices`: deletes user_device_complectations rows first, then UserDevice where oc_device_id IS NOT NULL
- All branches: delete MigrationJob rows WHERE entity = entity.value, then commit

## Contracts Verified:
- Pydantic schemas: OK (FastAPI validates MigrationEntity path param automatically — 422 on invalid value)
- DI via Depends: OK
- No Any in new code: OK (uses Dict[str, str] return type)
- ruff: OK (0 errors)
- mypy: OK (no issues found in 162 source files)
- alembic check: N/A — no DB model changes, database not running locally (connection refused to wifiobd)
- alembic heads: N/A — same reason

## Migrations:
- None required — only code changes, no schema modifications

## Next:
- Frontend-agent can now call `DELETE /api/v1/admin/migration/reset/{entity}` with any of: users, categories, products, images, orders, blog, addresses, devices
- Returns `{"status": "reset", "entity": "<entity_value>"}` on success

## Blockers:
- none
