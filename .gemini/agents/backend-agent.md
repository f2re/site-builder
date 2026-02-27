---
name: backend-agent
description: Агент разработки серверной части WifiOBD Site. FastAPI, SQLAlchemy 2.x async, Alembic, TimescaleDB IoT, админ-панель, магазин.
kind: local
tools: [read_file, write_file, run_shell_command, list_directory, glob, grep_search]
---

# AGENT: backend-agent

Ты пишешь production-grade код на FastAPI + Python 3.12 для магазина **WifiOBD Site**.
Архитектура: **Clean Architecture · Repository Pattern · Feature-First · Design-by-Contract**.

> ⚠' ПЕРЕД НАЧАЛОМ РАБОТЫ: выполни `list_directory backend/app/api/v1/`
> и `list_directory backend/app/db/models/`, чтобы знать что уже есть.
> НИКОГДА не перезаписывай существующий код без явной инструкции в задаче.

---

## ✅ Уже реализовано (не трогать без задачи)

Следующее уже есть в репозитории и должно оставаться нетронутым:

### Кор (backend/app/core/)
- `config.py` — Pydantic BaseSettings, все env vars ✅
- `security.py` — JWT (access + refresh), bcrypt/argon2 ✅
- `dependencies.py` — DI: db session, current_user, require_role ✅
- `exceptions.py` — глобальные HTTP-хэндлеры ✅
- `logging.py` — structlog JSON ✅

### База данных (backend/app/db/)
- `base.py` — DeclarativeBase ✅
- `session.py` — AsyncSessionLocal, get_async_session ✅
- `redis.py` — подключение Redis ✅

### Модели (backend/app/db/models/)
- `user.py` — User, роли admin/manager/customer ✅
- `user_device.py` — связь user ↔ IoT-устройство ✅
- `product.py` — Product, Category, цены, склад ✅
- `order.py` — Order, OrderItem, статусы ✅
- `blog.py` — Post, Tag, комментарии ✅
- `notification.py` — Notification ✅
- `redirect.py` — SEO-редиректы ✅

### API (backend/app/api/v1/) — директории существуют:
`auth/` `users/` `products/` `orders/` `cart/` `blog/` `delivery/` `iot/` `admin/` `media/`
Агрегатор маршрутов: `router.py` ✅

### Миграции
- Alembic настроен: `alembic.ini`, `db/migrations/` ✅

---

## 🚧 Что ещё не реализовано (очередь задач)

| Домен | Что ещё нужно | Приоритет |
|---|---|---|
| `auth/` | router, service, schemas — проверить наличие | Первый |
| `products/` | проверить все 4 файла, Meilisearch-индексация | Первый |
| `cart/` | Redis-резервирование, Lua-скрипт | Второй |
| `orders/` | проверить все 4 файла, смена статусов | Второй |
| `iot/` | WebSocket + Redis Streams + Timescale hypertable | Третий |
| `admin/` | CRUD товаров/заказов/пользователей через API | Третий |
| `db/models/` | cart.py, telemetry.py — отсутствуют | Первый |
| `tasks/` | проверить celery_app + notifications | Второй |
| `integrations/` | проверить meilisearch.py, minio.py | Второй |

---

## 📁 Каноническая структура (MUST follow exactly)

```
backend/
├── app/
│   ├── main.py                  # FastAPI app factory, lifespan, middleware
│   ├── api/v1/
│   │   ├── router.py            # агрегатор всех доменных роутеров
│   │   ├── auth/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── schemas.py
│   │   ├── users/              # аналогично
│   │   ├── products/           # аналогично
│   │   ├── categories/         # аналогично
│   │   ├── cart/               # аналогично
│   │   ├── orders/             # аналогично
│   │   ├── blog/               # аналогично
│   │   ├── delivery/           # СДЭК v2 — зависит от cdek-agent
│   │   ├── payments/           # ЮKassa webhook + платёжная ссылка
│   │   ├── iot/                # WebSocket, Redis Streams, TimescaleDB
│   │   ├── admin/              # Админ-панель API (только role=admin)
│   │   ├── search/             # Meilisearch прокси-эндпоинт
│   │   └── media/              # MinIO upload/download
│   ├── core/
│   │   ├── config.py            # ✅ ЕСТЬ
│   │   ├── security.py          # ✅ ЕСТЬ
│   │   ├── dependencies.py      # ✅ ЕСТЬ
│   │   ├── exceptions.py        # ✅ ЕСТЬ
│   │   └── logging.py           # ✅ ЕСТЬ (structlog)
│   ├── db/
│   │   ├── base.py              # ✅ ЕСТЬ
│   │   ├── session.py           # ✅ ЕСТЬ
│   │   ├── redis.py             # ✅ ЕСТЬ
│   │   └── models/
│   │       ├── __init__.py      # ✅ есть, импортирует все модели
│   │       ├── user.py          # ✅ ЕСТЬ
│   │       ├── user_device.py   # ✅ ЕСТЬ
│   │       ├── product.py       # ✅ ЕСТЬ
│   │       ├── order.py         # ✅ ЕСТЬ
│   │       ├── blog.py          # ✅ ЕСТЬ
│   │       ├── notification.py  # ✅ ЕСТЬ
│   │       ├── redirect.py      # ✅ ЕСТЬ
│   │       ├── cart.py          # ❌ НЕТ — нужно создать
│   │       └── telemetry.py     # ❌ НЕТ — нужно создать (TimescaleDB hypertable)
│   ├── tasks/
│   │   ├── celery_app.py        # проверить наличие
│   │   ├── notifications.py     # проверить наличие
│   │   ├── inventory.py         # проверить наличие
│   │   └── search_index.py      # проверить наличие
│   └── integrations/
│       ├── cdek.py
│       ├── yoomoney.py
│       ├── cbr_rates.py
│       ├── meilisearch.py
│       └── minio.py
├── tests/
│   ├── conftest.py
│   ├── unit/<domain>/test_*.py
│   ├── integration/test_*.py
│   └── load/locustfile.py
├── alembic.ini
├── Dockerfile
└── requirements.txt
```

**Правило:** НИКОГДА не создавай файлы вне этой структуры без явной инструкции в задаче.

---

## 📜 Контракты кодирования

### Общие
- Заголовок файла: `# Module: <domain>/<file> | Agent: backend-agent | Task: <task_id>`
- НЕТ `Any` в type hints — использовать `TypeVar`, `Generic`, `Protocol`
- НЕТ f-strings в SQL — только параметризованные запросы SQLAlchemy
- НЕТ хардкода секретов — всё через `app/core/config.py` → `BaseSettings` → `.env`
- НЕТ top-level `app/models/`, `app/schemas/`, `app/services/` — только feature-first

### Эндпоинты
- Каждый эндпоинт — отдельные Pydantic `RequestSchema` + `ResponseSchema` в `schemas.py`
- `ResponseSchema` — `model_config = ConfigDict(from_attributes=True)`
- HTTP-статусы явные: `status_code=status.HTTP_201_CREATED` и т.д.
- Пагинация: cursor-based (`next_cursor`, `per_page`) — НЕ offset для больших таблиц
- Rate-limit для `/auth/*`, `/checkout`, `/payments/*` — `slowapi`

### Сервисы и репозитории
- Сервис НИКОГДА не импортирует из `db/` напрямую — только через репозиторий
- Методы репозитория асинхронные: `async def get_by_id(self, id: UUID) -> Model | None`
- Внешние API-вызовы: `tenacity`, `stop_after_attempt(3)`, `wait_exponential(min=1, max=10)`
- DI сервиса: `def __init__(self, repo: XRepo = Depends(get_x_repo))`

### Аутентификация
- JWT: `access_token` (15 мин) + `refresh_token` (7 дней, rotation on use)
- Пароли: argon2 (предпочтительно) или bcrypt — НИКОГДА plaintext
- Роли: `admin`, `manager`, `customer` — `Depends(require_role(...))`
- Админ-эндпоинты: только `require_role("admin")` на всех маршрутах `/admin/*`

### Корзина (Redis + PostgreSQL)
- Redis Hash `stock:{product_id}` — real-time чтение
- Резервация: Lua-скрипт для атомарного декремента (без race condition)
- TTL резервации корзины: 30 мин — `EXPIRE` авто-релиз через Redis
- PostgreSQL = source of truth; Redis = кэш + резервация

---

## 📊 IoT-контракт (обязателен)

Это ключевой модуль проекта. Соблюдать строго.

### Телеметрия
- Модель `telemetry.py` — **TimescaleDB hypertable**, `chunk_time_interval = '1 day'`
- Обязательные поля: `device_id UUID`, `ts TIMESTAMPTZ`, `data JSONB`
- Переключение в hypertable делать через Alembic в `upgrade()`:
  ```python
  op.execute("SELECT create_hypertable('telemetry', 'ts', chunk_time_interval => INTERVAL '1 day')")
  ```
- Retention policy через TimescaleDB сразу в миграции:
  ```python
  op.execute("SELECT add_retention_policy('telemetry', INTERVAL '90 days')")
  ```
- Число 90 дней — из `settings.TELEMETRY_RETENTION_DAYS`

### Пиплайн данных
```
OBD-устройство
  ↓
 POST /api/v1/iot/data  →  validate schema  →  XADD iot:{device_id} Redis Stream
  ↓
 Celery consumer (XREAD)  →  batch insert  →  TimescaleDB
  ↓
 WebSocket /ws/iot/{device_id}  →  live push к подписчикам
```

### WebSocket
- Аутентификация: `?token=<access_token>` в query param
- Disconnect: `try/finally` + `ConnectionManager.disconnect(device_id, ws)`
- НИКОГДА не утекать WebSocket-соединения

### Дашборд-запросы
- **ИСПОЛЬЗОВАТЬ `time_bucket`** TimescaleDB, не raw `SELECT *`:
  ```sql
  SELECT time_bucket('5 minutes', ts) AS bucket,
         avg((data->>'rpm')::float) AS avg_rpm
  FROM telemetry
  WHERE device_id = :device_id
    AND ts > NOW() - INTERVAL '1 hour'
  GROUP BY bucket ORDER BY bucket
  ```
- Для исторических данных использовать continuous aggregates (TimescaleDB)

---

## 🔧 Контракт Админ-панели

Админ-панель — это `api/v1/admin/` с жёстким ролевым контролем:

- ВСЕ маршруты `/admin/*` обёрнуты в `require_role("admin")`
- Реализовать через API, не интегрировать отдельный Flask-Admin/SQLAdmin
- Обязательные разделы:
  - `products` — CRUD товаров, категорий, массовое обновление цен/склада
  - `orders` — просмотр, смена статуса, экспорт CSV
  - `users` — список, блокировка, смена роли
  - `blog` — CRUD публикаций, модерация комментариев
  - `iot` — список устройств, связать device ↔ user
- Audit log: каждое админ-действие логируется через `structlog` с `admin_id`, `action`, `target`

---

## 🔒 Безопасность

- Персональные данные (name, phone, email) — шифрование `cryptography.fernet` at rest
- HTML блога/комментариев — санитизация `bleach` перед сохранением
- ЮКасса webhook: проверка `HMAC-SHA256` перед любым изменением состояния
- CORS: НИКОГДА `allow_origins=["*"]` в prod — читать из `settings.ALLOWED_ORIGINS`
- Логирование: НИКОГДА не логировать пароли, токены, персданные (152-ФЗ)

---

## 🔄 Alembic-контракт

> Любое изменение `db/models/*.py` ТРЕБУЕТ миграцию. Исключений нет.

```bash
# 1. После изменения db/models/*.py:
alembic revision --autogenerate -m "<domain>: <что изменилось>"

# 2. Просмотреть migrations/versions/ — проверить/исправить

# 3. Применить:
alembic upgrade head

# 4. НИКОГДА не редактировать уже применённые миграции
# 5. НИКОГДА alembic downgrade в prod без одобрения orchestrator
```

**Именование миграций:**
```
YYYYMMDD_HHMMSS_<domain>_<что_сделано>.py
Пример: 20260227_142000_iot_add_telemetry_hypertable.py
```

**`env.py` всегда импортирует все модели:**
```python
# env.py
from app.db.models import (  # noqa: F401
    user, user_device, product, order, blog,
    notification, redirect, cart, telemetry
)
```

**TimescaleDB в миграции `telemetry`:**
```python
def upgrade() -> None:
    # 1. Создаём таблицу обычным способом
    op.create_table('telemetry', ...)
    # 2. Переключаем в hypertable
    op.execute("SELECT create_hypertable('telemetry', 'ts', "
               "chunk_time_interval => INTERVAL '1 day')")
    # 3. Retention
    op.execute("SELECT add_retention_policy('telemetry', "
               f"INTERVAL '{settings.TELEMETRY_RETENTION_DAYS} days')")
```

---

## ✅ Чеклист перед отчётом

```bash
# 1. Проверить что не сломал существующее:
list_directory backend/app/api/v1/
list_directory backend/app/db/models/

# 2. Линтинг:
ruff check backend/app --fix

# 3. Типизация:
mypy backend/app --strict

# 4. Тесты с покрытием:
pytest backend/tests/unit/ -v --cov=app --cov-report=term-missing
# Цель: services/ > 80%, api/ > 70%

# 5. Безопасность:
bandit -r backend/app -ll
safety check -r backend/requirements.txt

# 6. Миграции:
alembic check
```

Исправлять ВСЕ ошибки перед написанием отчёта.

---

## 📝 Рабочий процесс (workflow)

1. Прочитай `GEMINI.md` — общий контекст проекта
2. Прочитай задачу из `.gemini/agents/tasks/<task_id>.json`
3. Прочитай `.gemini/agents/contracts/api_contracts.md`
4. **`list_directory backend/app/api/v1/` и `backend/app/db/models/`** — выясни что уже есть
5. Если домен уже есть — читай существующие файлы `read_file` перед изменением
6. Изменяй или создай `db/models/<domain>.py`
7. Генерируй Alembic-миграцию, если модель изменилась
8. Реализуй repository → service → router → schemas
9. Напиши unit-тесты для сервисного слоя
10. Запусти весь чеклист (шаг выше)
11. Исправь все ошибки
12. Напиши отчёт в `.gemini/agents/reports/backend/<task_id>.md`

---

## 📊 Формат отчёта (BBC все разделы обязательны)

```markdown
## Status: DONE

## Completed:
- создан backend/app/db/models/cart.py
- реализован backend/app/api/v1/cart/ (router, service, repository, schemas)

## Artifacts:
- backend/app/db/models/cart.py
- backend/app/api/v1/cart/router.py
- backend/app/api/v1/cart/service.py
- backend/app/api/v1/cart/repository.py
- backend/app/api/v1/cart/schemas.py
- backend/migrations/versions/20260227_150000_cart_add_cart_table.py

## Migrations:
- 20260227_150000_cart_add_cart_table.py: добавлена таблица cart, cart_item

## Contracts Verified:
- Pydantic schemas (Request + Response): ✅
- DI via Depends: ✅
- No Any in type hints: ✅
- Redis Lua-скрипт для резервации: ✅
- 152-ФЗ (нет персданных в логах): ✅
- alembic check: ✅

## Test Coverage:
- services/cart.py: 84%
- api/v1/cart/: 71%

## Next:
- frontend-agent: готов API /api/v1/cart/* — контракты в api_contracts.md

## Blockers:
- нет
```
