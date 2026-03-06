# Примеры кода

В этой директории находятся эталонные реализации для различных слоёв и тестов. Копируйте и адаптируйте их при создании новых фич.

- `endpoint/router.py` — эталонный FastAPI router
- `endpoint/service.py` — сервис с DI и tenacity
- `endpoint/repository.py` — async SQLAlchemy repository
- `endpoint/schemas.py` — Pydantic Request + Response
- `test_unit.py` — unit-тест с fakeredis, respx
- `test_integration.py` — интеграционный тест
- `migration_example.py` — миграция Alembic с IF NOT EXISTS