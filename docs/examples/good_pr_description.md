# Эталонный PR / Отчёт агента

> Reference-by-example: используй как шаблон оформления PR и отчётов агентов.
> Агент копирует паттерн вместо интерпретации абстрактных правил.

---

## Пример PR Description

**Заголовок:**
```
✨ Реализован каталог товаров: endpoint /api/v1/products с пагинацией и фильтрацией
```

**Тело PR:**
```
## Что сделано
- GET /api/v1/products/ — пагинация, фильтр по category_id, поиск через Meilisearch
- GET /api/v1/products/{id} — детальная карточка товара
- POST /api/v1/products/ — создание (только admin)
- PATCH /api/v1/products/{id} — обновление (только admin)

## Архитектура
- Структура: router / service / repository / schemas (канонная)
- Модель Product в app/db/models/product.py
- Индексация в Meilisearch через Celery task (search_index.py)

## DoD checklist
- [x] ruff check app/ → 0 errors
- [x] mypy app/ → no issues
- [x] pytest tests/ → all green (18 tests, 0 failed)
- [x] alembic check → OK
- [x] alembic heads → 1 head
- [x] bash scripts/agents/verify_dod.sh → PASSED

## Затронутые компоненты
- backend/app/api/v1/products/
- backend/app/db/models/product.py
- backend/app/tasks/search_index.py
- migrations/versions/abc123_add_products.py

## Что передать следующему агенту
frontend-agent: API-контракт GET /api/v1/products/ готов, см. schemas.ProductListResponse
```

---

## Пример отчёта агента (.claude/agents/reports/backend/p3_backend_001.md)

```markdown
## Status: DONE

## Completed:
- GET /api/v1/products/ с пагинацией и фильтром по category_id
- GET /api/v1/products/{id}
- Meilisearch индексация через Celery
- Unit-тесты: 18 тестов, 0 failed

## Artifacts:
- backend/app/api/v1/products/router.py
- backend/app/api/v1/products/service.py
- backend/app/api/v1/products/repository.py
- backend/app/api/v1/products/schemas.py
- migrations/versions/abc123_add_products.py
- tests/unit/test_products_service.py
- tests/unit/test_products_repository.py

## Contracts Verified:
- Pydantic schemas: ✅
- DI via Depends: ✅
- ruff: ✅ | mypy: ✅ | pytest: ✅ (18/18)
- alembic check: ✅ | alembic heads: ✅ (1 head)
- bash scripts/agents/verify_dod.sh: ✅ PASSED

## Next:
- Передать frontend-agent: контракт ProductListResponse и ProductResponse готов
- cdek-agent может начинать интеграцию (зависимость от orders → Фаза 4)

## Blockers:
- нет
```
