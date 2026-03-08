# Task Report: p17_backend_celery_migration_fix

## Status: DONE

## Completed:
- Исправлена ошибка "Permission denied" для `/app/media/products` через создание директорий в Dockerfile
- Исправлена ошибка "Event loop is closed" через удаление вложенного `asyncio.run()` в обработке ошибок
- Добавлен volume `./media:/app/media` для celery сервиса в docker-compose.yml
- Добавлена обработка PermissionError с понятным сообщением в migration_service.py

## Artifacts:
- backend/Dockerfile (development и production stages)
- docker-compose.yml (celery service volumes)
- backend/app/tasks/migration_tasks.py
- backend/app/api/v1/admin/migration_service.py

## Changes Detail:

### 1. backend/Dockerfile
**Development stage:**
```dockerfile
RUN mkdir -p /app/media/products /app/media/blog
```

**Production stage:**
```dockerfile
RUN mkdir -p /app/media/products /app/media/blog && chown -R appuser:appuser /app/media
```

### 2. docker-compose.yml
Добавлен volume для celery:
```yaml
volumes:
  - ./backend:/app
  - ./media:/app/media
```

### 3. backend/app/tasks/migration_tasks.py
- Убрана функция `_mark_job_failed()` с вложенным `asyncio.run()`
- Обработка ошибок перенесена внутрь основного event loop
- Session закрывается в finally блоке перед dispose engines
- Engines dispose остается в finally для предотвращения "Event loop is closed"

### 4. backend/app/api/v1/admin/migration_service.py
Добавлена обработка PermissionError в методе `_download_image()`:
```python
try:
    full_path.parent.mkdir(parents=True, exist_ok=True)
except PermissionError as perm_err:
    logger.error(
        "media_permission_error",
        path=str(full_path.parent),
        error=str(perm_err),
        solution="Check Docker volume permissions: ensure /app/media is writable by the container user"
    )
    raise
```

## Contracts Verified:
- ruff check: ✅
- mypy: ✅ (140 source files)
- alembic heads: ✅ (single head: 51b7b7931577)
- YAML syntax: ✅
- No hardcoded paths: ✅
- Proper error handling: ✅

## Root Cause Analysis:

### Permission denied:
- Директория `/app/media/products` не существовала в Docker образе
- Celery worker не мог создать её из-за отсутствия родительской директории
- **Решение**: Создание директорий в Dockerfile с правильными правами

### Event loop is closed:
- В строке 50 старого кода вызывался `asyncio.run(_mark_job_failed(job_id))` после того как основной event loop уже закрылся
- Это создавало новый event loop, что приводило к конфликтам с asyncpg/aiomysql cleanup
- **Решение**: Обработка ошибок внутри основного event loop, без вложенных `asyncio.run()`

## Testing Recommendations:
1. Пересобрать celery контейнер: `docker compose build celery`
2. Запустить celery: `docker compose up -d celery`
3. Проверить создание директорий: `docker compose exec celery ls -la /app/media/`
4. Запустить миграцию через API: POST `/api/v1/admin/migration/start`
5. Проверить логи: `docker compose logs -f celery`
6. Убедиться что изображения скачиваются без ошибок

## Next:
- frontend-agent: миграция должна работать без ошибок, можно тестировать UI
- testing-agent: добавить интеграционный тест для проверки скачивания изображений

## Blockers:
- none
