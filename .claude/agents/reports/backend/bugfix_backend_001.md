## Status: DONE

## Completed:
- BUG-1: Добавлен `_SafeEnvSource` в config.py — перехватывает пустые строки для complex-типов до json.loads(), предотвращая JSONDecodeError при BACKEND_CORS_ORIGINS="" в .env.prod
- BUG-2: tasks/inventory.py:25 — `OrderStatus.PENDING` заменён на `OrderStatus.PENDING.value` (lowercase "pending" для PostgreSQL enum)
- BUG-3: blog/router.py — в `list_posts` и `list_comments` заменён `Depends(get_current_user)` на `Depends(get_optional_current_user)`, удалён неиспользуемый импорт `get_current_user`

## Artifacts:
- backend/app/core/config.py
- backend/app/tasks/inventory.py
- backend/app/api/v1/blog/router.py

## Contracts Verified:
- ruff: 0 errors
- mypy: Success: no issues found in 3 source files

## Next:
- Пересобрать и задеплоить контейнер backend: `docker compose build backend && docker compose up -d backend celery`
- После деплоя проверить: GET /api/v1/blog/posts без токена → 200, alembic upgrade head без ошибок

## Blockers:
- нет
