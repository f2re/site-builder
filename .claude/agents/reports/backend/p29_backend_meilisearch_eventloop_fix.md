## Status: DONE

## Completed:
- Исправлена Проблема 1: `MEILISEARCH_API_KEY` в `config.py` теперь читает переменную через `AliasChoices("MEILISEARCH_API_KEY", "MEILI_MASTER_KEY", "MEILI_API_KEY")` — backend подхватывает `MEILI_MASTER_KEY` из docker-compose автоматически
- Обновлён `.env.example` — раздел Meilisearch документирует оба имени переменной и объясняет алиасы
- Исправлена Проблема 2: создан `backend/app/db/celery_session.py` с `NullPool` — соединения не возвращаются в пул и не требуют работающего event loop при завершении `asyncio.run()`
- `tasks/search.py` — `AsyncSessionLocal` → `CelerySessionLocal`
- `tasks/delivery.py` — `AsyncSessionLocal` → `CelerySessionLocal`
- `tasks/migration_tasks.py` — `AsyncSessionLocal` → `CelerySessionLocal`; также исправлен `finally` блок: убран dispose основного `pg_engine` (FastAPI engine), заменён на `celery_engine.dispose()` — больше не убивает соединения FastAPI-процесса

## Artifacts:
- `backend/app/core/config.py` — `MEILISEARCH_API_KEY` с `AliasChoices`
- `backend/app/db/celery_session.py` — новый файл, `NullPool` engine для Celery
- `backend/app/tasks/search.py` — использует `CelerySessionLocal`
- `backend/app/tasks/delivery.py` — использует `CelerySessionLocal`
- `backend/app/tasks/migration_tasks.py` — использует `CelerySessionLocal` + исправлен dispose
- `.env.example` — документация переменных Meilisearch

## Contracts Verified:
- Pydantic schemas: OK
- ruff: 0 errors (2 auto-fixed)
- mypy: 0 issues (5 files проверено)

## Next:
- Перезапустить Celery worker и backend для применения изменений
- В `.env` убедиться что `MEILI_MASTER_KEY` заполнен (или `MEILISEARCH_API_KEY`)

## Blockers:
- none
