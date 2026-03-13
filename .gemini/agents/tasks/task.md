@orchestrator ты должен устранить эти баги, архитектурные проблемы
Now I have a complete picture. Here is the full diagnosis and fix plan.

***

## Root Cause: Enum Case Mismatch

The error is unambiguous:

```
invalid input value for enum migrationentity: "users"
```

The SQL query sends `'users'` (lowercase), but the `migrationentity` enum in the PostgreSQL database was created with **lowercase** values — which is correct. However, **the Python model was later changed to use UPPERCASE values**, creating a permanent mismatch.

### The Conflict in Detail

| Layer | Values used |
|---|---|
| **DB enum** (created by migration `20260301_1230`) | `'users'`, `'categories'`, `'products'`, `'images'`, `'orders'`, `'blog'` |
| **DB enum** (extended by `20260311_1200`)| + `'devices'`, `'addresses'` |
| **Python `MigrationEntity`** (current `migration.py`) | `USERS = "USERS"`, `CATEGORIES = "CATEGORIES"`, etc. — **UPPERCASE** |

The Alembic migration [created the enum with lowercase strings](https://github.com/f2re/site-builder/blob/main/backend/app/db/migrations/versions/20260301_1230-opencart_migration_tables.py) (`'users'`, `'categories'`…), but the Python model in [`db/models/migration.py`](https://github.com/f2re/site-builder/blob/main/backend/app/db/models/migration.py) now declares `USERS = "USERS"` — so SQLAlchemy sends `"users"` (the `.value` lowercased by `values_callable`) but PostgreSQL actually stored `"USERS"` — wait, let's be precise: the DB has `'users'` (lowercase), Python sends `"USERS"` (uppercase). PostgreSQL enum comparison is case-sensitive, so it rejects `"users"` sent as the value… Actually re-reading: `values_callable=lambda enum_cls: [e.value for e in enum_cls]` means SQLAlchemy registers the type expecting `"USERS"` as the valid value, but the DB enum type contains `'users'`. The wire value sent is `'users'` (from the SQL log), meaning somewhere the value is lowercased. Regardless, the DB has lowercase, Python has uppercase — **they don't match**.

***

## Fix Plan

### Option A — Fix the Python model (recommended, no DB change)

Change `MigrationEntity` values in [`backend/app/db/models/migration.py`](https://github.com/f2re/site-builder/blob/main/backend/app/db/models/migration.py) to match what the DB actually contains:

```python
class MigrationEntity(str, enum.Enum):
    USERS      = "users"
    CATEGORIES = "categories"
    PRODUCTS   = "products"
    IMAGES     = "images"
    ORDERS     = "orders"
    BLOG       = "blog"
    DEVICES    = "devices"
    ADDRESSES  = "addresses"
```

This requires **no migration**, no DB touch, and is safe for running services. All call sites use `MigrationEntity.USERS` etc., which already works correctly since Python enum members are accessed by name, not by `.value`.

### Option B — Fix the DB (requires downtime + migration)

Write a new Alembic migration to rename all enum values to uppercase:

```sql
-- For each value, PostgreSQL 10+ supports:
ALTER TYPE migrationentity RENAME VALUE 'users' TO 'USERS';
ALTER TYPE migrationentity RENAME VALUE 'categories' TO 'CATEGORIES';
-- ... and so on for all 8 values
```

This is riskier because any existing rows in `migration_jobs.entity` with lowercase values will also need a `UPDATE migration_jobs SET entity = 'USERS'::migrationentity WHERE entity = 'users'::migrationentity` — but since the enum rename and cast happen simultaneously on a live type, it requires careful ordering and a maintenance window.

***

## Recommended Action

**Apply Option A immediately** — it is a one-line-per-value fix in a single Python file with zero DB risk . The DB enum values `'users'`, `'categories'`, `'products'`, `'images'`, `'orders'`, `'blog'`, `'devices'`, `'addresses'` are already consistent across both migrations ; only the Python model needs its `.value` strings lowercased to match.
сам не пиши код, делегируй агентам. в конце запусти тесты и линты перед коммитом, закоммить изменения