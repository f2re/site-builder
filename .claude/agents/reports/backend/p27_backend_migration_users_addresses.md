## Status: DONE

## Completed:
- Добавлена курсорная пагинация в `migrate_addresses()`: читает по `self.batch_size` записей через `OCAddress.address_id > last_addr_id`
- Cursor хранится в `job.extra_data['addresses_last_id']` (не конфликтует с `job.last_oc_id` который используется в `migrate_users`)
- Обёртка `try/except` на каждый адрес уже была, сохранена и работает корректно — при ошибке вызывает `await self.session.rollback()`, инкрементирует `skipped`, логирует `logger.warning("migrate_addresses_skip", ...)`
- Изменена сигнатура: `migrate_addresses(self, job: MigrationJob) -> bool`
- Возвращает `True` если `len(addresses) == self.batch_size` (нужен retrigger), `False` если batch неполный
- Обновлён `run_batch`: после завершения `migrate_users` запускает `migrate_addresses(job)` в цикле через флаг `extra_data['addresses_done']`
- Когда последний батч адресов обработан — статус job выставляется в `DONE`
- Счётчики `job.processed` и `job.skipped` обновляются после каждого батча
- Исправлена pre-existing проблема ruff F811: `bs4.Tag` переименован в `BSTag` (ruff --fix применил автоматически)

## Artifacts:
- backend/app/api/v1/admin/migration_service.py

## Contracts Verified:
- Pydantic schemas: N/A (сервисный слой, без изменения API контрактов)
- ruff: OK (0 ошибок)
- mypy: 2 pre-existing ошибки в строках 155-156 (bs4 union-attr), не введены мной
- alembic heads: 1 head (96f1ab236541) — OK; alembic check: нет подключения к БД локально (ожидаемо)
- pytest: не запускались (нет локального PostgreSQL/Redis), юнит-тесты не затронуты

## Architecture:
- `migrate_addresses(self, job: MigrationJob) -> bool` — cursor через `extra_data['addresses_last_id']`
- `run_batch` orchestration: `migrate_users` → (users done) → `migrate_addresses` батчи → (addresses done) → `DONE`
- Каждый адрес: idempotency check → lookup OCCustomer → lookup User → try/except INSERT
- Телефон берётся из `oc_customer.telephone` (правильно — в OpenCart телефон в customer, не в address)

## Next:
- none

## Blockers:
- none
