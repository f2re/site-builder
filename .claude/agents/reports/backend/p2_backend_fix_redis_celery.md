## Status: DONE

## Completed:
- Добавлена функция `get_inventory_for_celery()` в `backend/app/integrations/redis_inventory.py`
- Все три Celery-задачи в `backend/app/tasks/inventory.py` теперь создают локальный Redis-клиент внутри async-функции
- Глобальный `inventory` сохранён для FastAPI-эндпоинтов (через DI)

## Artifacts:
- /Users/meteo/Documents/WWW/site-builder/backend/app/integrations/redis_inventory.py
- /Users/meteo/Documents/WWW/site-builder/backend/app/tasks/inventory.py

## Root Cause:
Глобальный `inventory = RedisInventory(redis_client)` создавался при импорте модуля с async Redis-клиентом, привязанным к исходному event loop. При вызове `asyncio.run()` в Celery-воркере создавался новый event loop, а старое TCP-соединение было закрыто, что приводило к `RuntimeError: unable to perform operation on <TCPTransport closed=True>`.

## Solution:
Создана функция `get_inventory_for_celery()`, которая при каждом вызове создаёт новый Redis-клиент через `redis.from_url(settings.REDIS_URL)`. Все три Celery-задачи (`release_stale_reservations_task`, `sync_stock_to_redis`, `release_reserved_stock`) теперь вызывают эту функцию внутри async-блока перед использованием inventory.

## Changes:
### redis_inventory.py
- Добавлена функция `get_inventory_for_celery()` (строки 74-82)
- Функция создаёт свежий Redis-клиент для каждого Celery-контекста

### inventory.py
- Изменён импорт: `from app.integrations.redis_inventory import get_inventory_for_celery`
- Все три задачи теперь создают локальный `inventory = get_inventory_for_celery()` внутри async-функции

## Contracts Verified:
- Pydantic schemas: N/A (не затронуты)
- DI via Depends: ✅ (глобальный `inventory` и `get_inventory()` остались для FastAPI)
- No Any: ✅
- Celery async pattern: ✅ (используется `asyncio.run()`)
- ruff: ✅ (0 errors)
- mypy: ✅ (no issues)
- pytest: ✅ (49 passed)

## Verification Results:
```bash
cd backend && ruff check app/integrations/redis_inventory.py app/tasks/inventory.py
# All checks passed!

cd backend && mypy app/integrations/redis_inventory.py app/tasks/inventory.py --ignore-missing-imports
# Success: no issues found in 2 source files

cd backend && pytest tests/ -x -v
# 49 passed in 6.72s
```

## Next:
- Ручная проверка: запустить Celery-воркер и триггернуть задачу `release_stale_reservations_task` для подтверждения отсутствия RuntimeError
- Задача готова к продакшену

## Blockers:
- none
