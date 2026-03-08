## Status: DONE

## Completed:
- migrate_users: каждый INSERT обёрнут в `try/except` с `await session.rollback()` — падение одного пользователя не ломает весь batch
- migrate_users: если `get_blind_index(email)` возвращает пустую строку или None — генерируется уникальный fallback hash через `hashlib.sha256(str(uuid4()).encode()).hexdigest()`
- migrate_users: пропущенные записи инкрементируют `skipped`, логируются через `logger.warning` с `oc_customer_id` и `error`
- migration_tasks: добавлена async-функция `_mark_job_failed()` — обновляет статус job через свежую DB-сессию перед retry, чтобы job не зависал в RUNNING навсегда
- migration_tasks: `max_retries` увеличен с 1 до 3
- reset_migration: добавлено удаление пользователей с `role='customer'` и `is_superuser=False` (шаг 7, после Orders, перед MigrationJob)
- reset_migration: администраторы (role='admin', is_superuser=True) НЕ удаляются
- reset_migration: логируется количество удалённых пользователей через `logger.info`
- Исправлена mypy ошибка в существующем файле миграции `20260308_0945-..._merge_delivery_addresses_and_order_.py` (down_revision тип Union[str, Sequence[str], None])
- Добавлены импорты: `hashlib`, `uuid4` в migration_service.py

## Artifacts:
- backend/app/api/v1/admin/migration_service.py
- backend/app/tasks/migration_tasks.py
- backend/app/db/migrations/versions/20260308_0945-51b7b7931577_merge_delivery_addresses_and_order_.py

## Migrations:
- Изменения только в сервисном слое — новые миграции не требуются

## Contracts Verified:
- Pydantic schemas: OK (не изменялись)
- DI via Depends: OK
- ruff: OK (0 errors)
- mypy: OK (0 errors, 140 files checked)
- pytest: OK (41 passed)
- alembic check: не применимо (БД недоступна локально — ошибка подключения, не ошибка схемы)

## Next:
- Функционал готов к деплою и ручному тестированию миграции с реальной OpenCart БД

## Blockers:
- none
