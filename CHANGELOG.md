# Changelog

## [Unreleased]

### Added — 2026-02-26 (stage3_wiring)

#### Routing
- `api/v1/router.py` — подключены `admin_router` (`/admin/*`) и `users_router` (`/users/*`) к главному `api_router`
- `main.py` уже подключает `api_router` через `app.include_router`, дополнительных изменений не потребовалось

#### Alembic migrations
- `backend/alembic.ini` — конфиг Alembic, `script_location = app/db/migrations`
- `db/migrations/env.py` — async-среда на базе `async_engine_from_config`, читает `DATABASE_URL` из Pydantic settings, импортирует все модели через `app.db.models`
- `db/migrations/versions/0001_init_users.py` — создание таблицы `users`
- `db/migrations/versions/0002_add_orders_user_devices.py` — таблицы `orders` (с enum `orderstatus`) и `user_devices`
- `db/migrations/script.py.mako` — шаблон для новых ревизий

#### Models registry
- `db/models/__init__.py` — импортирует `User`, `Order`, `UserDevice` для Alembic autogenerate

#### Config
- `core/config.py` — полный список переменных окружения: DB, Redis, CORS, SMTP, YooMoney, СДЭК, MinIO

### Added — 2026-02-26 (stage2_rbac)

#### Security & RBAC
- `core/security.py` — поле `role` добавлено в JWT access token
- `core/dependencies.py` — `get_current_user`, `require_admin`, `require_manager`, `require_customer`
- `auth/schemas.py` — поле `role` в `TokenPayload`
- `auth/service.py` — передача `role` в `create_access_token`

#### Admin panel (`/api/v1/admin/*`)
- Dashboard / аналитика продаж
- CRUD товаров + обновление наличия
- Управление заказами + смена статуса
- CRUD блога + модерация комментариев
- Управление пользователями + блокировка
- IoT-мониторинг: список устройств, статус Redis-очередей

#### User cabinet (`/api/v1/users/*`)
- Просмотр и редактирование профиля
- История покупок
- Управление OBD2-устройствами
- WebSocket `/users/me/devices/{id}/connect` — real-time поток данных

#### Models
- `db/models/order.py` — `Order` + `OrderStatus` enum
- `db/models/user_device.py` — `UserDevice`
- `db/models/user.py` — relationships `orders`, `devices`
