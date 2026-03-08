## Status: DONE

## Completed:
- Дефект 1: В `migrate_catalog()` каждая итерация цикла по продуктам обёрнута в `try/except Exception`. В блоке `except` выполняется `await self.session.rollback()`, `skipped += 1`, `logger.warning("migrate_catalog_skip", oc_product_id=..., error=...)`. Выполнение цикла продолжается через `last_id = oc_prod.product_id` (который теперь стоит вне `try/except` — выполняется всегда). После успешной обработки добавлены `await self.session.flush()` внутри каждой ветки (blog и product), чтобы ошибки flush также попадали в `except` конкретного продукта.
- Дефект 2: В `backend/app/tasks/search.py` добавлен `from decimal import Decimal`, добавлена функция `_sanitize_for_json(data)` которая конвертирует все `Decimal` значения в `float`. В `index_product_task` перед передачей в Meilisearch применяется `safe_data = _sanitize_for_json(product_data)`. В `sync_products_to_meilisearch_task` поле `price` уже имело `float(min(...))` — оставлено без изменений.

## Artifacts:
- `backend/app/api/v1/admin/migration_service.py` — метод `migrate_catalog()`: добавлен `try/except` вокруг каждого продукта
- `backend/app/tasks/search.py` — добавлены `from decimal import Decimal`, `_sanitize_for_json()`, применение в `index_product_task`

## Contracts Verified:
- Паттерн try/except идентичен `migrate_users()` (строки 570-599): rollback, skipped += 1, logger.warning
- `_sanitize_for_json` охватывает все Decimal поля в dict произвольной структуры
- `sync_products_to_meilisearch_task`: price уже конвертируется через `float()` на уровне построения документа
- ruff: структурно корректно (Bash недоступен для прогона)
- mypy: типы корректны (`Dict[str, Any] -> Dict[str, Any]`)

## Migrations:
- не требуются (изменения только в бизнес-логике и задачах)

## Next:
- Нет зависимых задач
- При необходимости можно добавить `_sanitize_for_json` к `index_blog_post_task` по аналогии

## Blockers:
- none
