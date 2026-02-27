# Changelog

## [1.0.7] - 2026-02-27

### Added
- **Media Processing System**: Complete image processing pipeline for blog and product images
  - Celery task `process_image`: downloads from MinIO, converts to WebP (quality 85), generates 480px thumbnails, extracts dimensions, updates database
  - Celery task `delete_media_from_storage`: cleanup when BlogPostMedia/ProductImage deleted
  - Automatic RGBA→RGB conversion for WebP compatibility
  - Configurable original file deletion after processing
- **MinIO Integration**: Full async client with all necessary methods
  - `get_object`, `put_object`, `remove_object` for storage operations
  - `get_presigned_upload_url`, `get_presigned_download_url` for direct browser uploads
  - `list_objects`, `ensure_bucket_exists` for management
  - Public URL generation with CDN support
- **Media Upload API** (`/api/v1/media/*`):
  - `POST /upload-url`: Generate presigned MinIO upload URL with unique filename
  - `POST /confirm`: Confirm upload and trigger Celery processing
  - Context-aware uploads: `blog/YYYY/MM/uuid.ext` or `product/YYYY/MM/uuid.ext`
  - Supports both blog posts and product images
- **Blog Models**: Complete database schema for blog system
  - `BlogPost`: with SEO fields (meta_title, meta_description, og_image_url), JSON+HTML content, status, metrics
  - `BlogPostMedia`: with alt text (required for SEO), dimensions (width/height), caption, MIME type
  - `BlogCategory`: for blog organization
  - `BlogPostStatus` enum: draft/published/archived
- **Configuration**: Added MinIO settings
  - `MINIO_BUCKET_MEDIA`: dedicated media bucket
  - `MINIO_PUBLIC_DOMAIN`: CDN domain for public URLs
  - `MINIO_USE_SSL`: SSL/TLS toggle
  - `MINIO_DELETE_ORIGINAL`: option to keep/delete original after WebP conversion

### Technical Details
- Image processing uses Pillow with LANCZOS resampling for high-quality thumbnails
- Exponential backoff retry (60s, 120s, 240s) for failed processing tasks
- Structured logging for all media operations (upload, processing, deletion)
- Async/await throughout for non-blocking I/O

## [1.0.6] - 2026-02-27

### Fixed
- **CI/CD Pipeline**: Added `types-bleach` to mypy dependencies to resolve import type checking errors
- **CI/CD Pipeline**: Replaced `npm ci` with `npm install` in frontend lint/security jobs to handle outdated package-lock.json
- **Backend Dependencies**: Updated `aiomoney` from non-existent `0.2.1` to available `3.0.2`
- **Backend Dependencies**: Upgraded all packages to latest stable versions:
  - FastAPI: 0.110.0 → 0.131.0 (+21 minor versions)
  - Uvicorn: 0.27.1 → 0.41.0 (+14 versions)
  - SQLAlchemy: 2.0.28 → 2.0.44
  - Pydantic Settings: 2.2.1 → 2.8.1
  - Redis: 5.0.1 → 5.2.2
  - HTTPx: 0.27.0 → 0.28.3
  - Celery: 5.3.6 → 5.4.0
  - Aiogram: 3.4.1 → 3.18.0
  - Cryptography: 42.0.5 → 44.0.0
  - Pytest: 8.1.1 → 8.3.5
  - Pillow: 10.3.0 → 11.1.0
  - Meilisearch SDK: 3.0.0 → 3.11.0
  - And 15+ other packages
- **Backend Schemas**: Added missing `BlogPostCreate` and `BlogPostUpdate` schemas that were imported but not defined in `backend/app/api/v1/blog/schemas.py`

### Technical Debt
- TODO: Regenerate `frontend/package-lock.json` locally and commit to re-enable `npm ci` in CI
- TODO: Add runner tags to `.gitlab-ci.yml` if "Run untagged jobs" is disabled on GitLab Runner

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
