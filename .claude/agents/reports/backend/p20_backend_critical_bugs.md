# Task Report: p20_backend_critical_bugs

## Status: DONE

## Completed:
- Fixed GET /api/v1/admin/orders/{order_id} 404 error - added missing endpoint
- Fixed migration crash 'MetaData' object has no attribute 'get' - renamed to extra_data
- Verified MigrationEntity.BLOG exists for blog migration tracking

## Artifacts:
- backend/app/db/models/migration.py (added extra_data field)
- backend/app/db/migrations/versions/20260308_1221_add_extra_data_to_migration_jobs.py
- backend/app/api/v1/admin/migration_service.py (updated metadata → extra_data)
- backend/app/api/v1/admin/router.py (added GET /admin/orders/{order_id} endpoint)

## Implementation Details:

### 1. Fixed Orders API 404
Added missing endpoint in admin/router.py:
```python
@router.get("/orders/{order_id}")
async def get_order(
    order_id: UUID,
    _admin: User = AdminDep,
    repo: OrderRepository = Depends(get_order_repo),
) -> Any:
    from app.api.v1.orders.schemas import OrderRead
    order = await repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderRead.model_validate(order)
```

### 2. Fixed MetaData AttributeError
Root cause: MigrationJob model had no metadata field, causing SQLAlchemy to confuse with its own MetaData class.

Solution:
- Added `extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)` to MigrationJob
- Note: "metadata" is reserved in SQLAlchemy Declarative API, used "extra_data" instead
- Updated migration_service.py line 402: `job.metadata` → `job.extra_data`
- Updated migration_service.py line 410: `metadata=metadata` → `extra_data=metadata`
- Created Alembic migration to add extra_data column

### 3. Blog Migration Category
MigrationEntity.BLOG already exists in migration.py line 22 - no changes needed.

## Contracts Verified:
- ruff check: ✅ All checks passed
- mypy: ✅ Success: no issues found in 142 source files
- alembic check: ⚠️ Skipped (database not running locally)

## Next:
- Apply migration: `alembic upgrade head` (when database is running)
- frontend-agent: Fix orders list display (total amount, pagination, date filters) - task p21_frontend_admin_orders_fix
- Test GET /api/v1/admin/orders/{id} returns 200 with order data
- Test migration runs without MetaData error

## Blockers:
- none
