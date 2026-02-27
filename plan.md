# Техническое задание: Интернет-магазин WifiOBD (FastAPI + Nuxt 3)

> **Статус проекта:** 🟡 Активная разработка — Этап 1 завершён, Этап 2 в процессе
> **Последнее обновление:** 2026-02-27
> **Репозиторий:** self-hosted GitLab CE (зеркало: GitHub `f2re/site-builder`)

---

## 1. Архитектурная концепция

Система строится на **модульной Clean Architecture**: каждый домен (товары, заказы, блог, IoT) — изолированный модуль со своими роутерами, схемами, сервисами и репозиториями. Асинхронность FastAPI + SQLAlchemy async обеспечивает максимальную производительность на I/O-операциях.

### Технологический стек

| Слой | Технология | Обоснование |
|------|-----------|-------------|
| Backend API | FastAPI (Python 3.12+) | Async-first, Swagger/ReDoc, type hints |
| ORM | SQLAlchemy 2.x async + Alembic | Миграции, type-safe запросы |
| БД | PostgreSQL 16 | ACID, JSONB для атрибутов товаров |
| Кэш / Очереди | Redis 7 | Кэш каталога, корзина, инвентарь в реальном времени |
| Фоновые задачи | Celery + Redis broker | Email, медиа-обработка, поиск, уведомления |
| Frontend | Nuxt 3 (Vue 3 + Pinia) | SSR для SEO блога и каталога |
| Хранилище медиа | MinIO (self-hosted S3) | Изображения/видео, presigned URL |
| Контейнеризация | Docker Compose (dev) + Nginx (prod) | Self-hosted, без внешних cloud-провайдеров |
| CI/CD | GitLab CE self-hosted + GitLab Runner + Container Registry | Локальный пайплайн без Docker Hub |
| Поиск | Meilisearch | Полнотекстовый поиск, лёгкий self-hosted |

---

## 2. Структура проекта

> ✅ Базовая структура **создана** — директории `backend/`, `frontend/`, `deploy/` существуют в репозитории.

```
project/
├── backend/
│   ├── Dockerfile                   ✅ готов
│   ├── alembic.ini                  ✅ готов
│   ├── requirements.txt             ✅ готов
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── products/            🔨 в разработке
│   │   │   ├── orders/              ⬜ запланировано
│   │   │   ├── cart/                ⬜ запланировано
│   │   │   ├── blog/                ⬜ запланировано
│   │   │   ├── media/               ⬜ запланировано
│   │   │   ├── delivery/            ⬜ запланировано
│   │   │   ├── payments/            ⬜ запланировано
│   │   │   ├── iot/                 ⬜ запланировано
│   │   │   └── users/               ✅ частично (auth готов)
│   │   ├── core/
│   │   │   ├── config.py            ✅ готов (Pydantic Settings)
│   │   │   ├── security.py          ✅ готов (JWT + bcrypt)
│   │   │   └── dependencies.py      ✅ готов
│   │   ├── db/
│   │   │   ├── models/              🔨 базовые модели готовы
│   │   │   └── migrations/          ✅ Alembic инициализирован
│   │   ├── tasks/                   ⬜ Celery-таски запланированы
│   │   └── integrations/            ⬜ внешние API запланированы
│   └── tests/                       ⬜ тесты запланированы
├── frontend/                        🔨 базовая структура Nuxt 3
├── deploy/                          ✅ docker-compose.prod.yml, nginx.conf
├── docker-compose.yml               ✅ dev-окружение готово
└── .gitlab-ci.yml                   ✅ CI/CD пайплайн готов
```

**Легенда:** ✅ готово · 🔨 в работе · ⬜ запланировано

---

## 3. Этапы разработки

### Этап 1 — Инфраструктура и ядро ✅ ЗАВЕРШЁН

**Что реализовано:**
- Docker Compose: сервисы `api`, `postgres`, `redis`, `celery_worker`, `celery_beat`, `frontend`, `meilisearch`, `minio`
- Конфигурация: `Pydantic BaseSettings` — все секреты из `.env`
- БД: асинхронное подключение через `asyncpg`, сессии через Dependency Injection
- Аутентификация: JWT (access 15 мин + refresh 7 дней), `bcrypt`/`argon2`, роли: `admin`, `manager`, `customer`
- Логирование: `structlog` JSON-логи, middleware логирует каждый запрос
- Обработка ошибок: глобальные exception handlers
- Alembic: инициализирован, базовые миграции

**`backend/requirements.txt` — зависимости:**
```
fastapi==0.110.0
uvicorn[standard]==0.27.1
pydantic-settings==2.2.1
sqlalchemy[asyncio]==2.0.28
asyncpg==0.29.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
structlog==24.1.0
tenacity==8.2.3
python-dotenv==1.0.1
alembic==1.13.1
python-multipart==0.0.9
miniopy-async==1.19.0
Pillow==10.3.0
bleach==6.1.0
meilisearch-python-sdk==3.0.0
celery[redis]==5.3.6
httpx==0.27.0
pytest==8.1.0
pytest-asyncio==0.23.6
respx==0.21.1
ruff==0.3.2
mypy==1.9.0
types-python-jose==3.3.4.20240106
types-passlib==1.7.7.20240311
```

---

### Этап 2 — Каталог товаров и инвентарь 🔨 В РАЗРАБОТКЕ

**Модели БД (`backend/app/db/models/products.py`):**
```python
class Category(Base):
    id: int, name: str, slug: str, parent_id: int | None
    # Adjacency List для дерева категорий

class Product(Base):
    id: int, name: str, slug: str          # unique, indexed
    description_html: str                   # sanitized HTML
    attributes: dict                        # JSONB
    category_id: int
    price: Decimal
    is_active: bool
    meta_title: str | None                  # SEO, max 60 символов
    meta_description: str | None            # SEO, max 160 символов
    og_image_url: str | None                # Open Graph
    created_at: datetime, updated_at: datetime

class ProductImage(Base):
    id: int, product_id: int
    url: str                                # MinIO путь
    alt: str                                # ОБЯЗАТЕЛЬНО для SEO/a11y
    is_cover: bool
    sort_order: int
    width: int, height: int                 # предотвращает CLS

class ProductVariant(Base):
    id: int, product_id: int
    sku: str (unique), name: str
    price: Decimal, stock: int

class StockMovement(Base):
    id: int, variant_id: int
    delta: int, reason: str                 # 'sale' | 'return' | 'correction'
    created_at: datetime
```

**Инвентарь — Redis + PostgreSQL:**
- PostgreSQL — источник правды
- Redis Hash `stock:{variant_id}` — быстрое чтение
- Резервирование через Redis lease с TTL 30 мин
- Lua-скрипты для атомарного списания (исключает race conditions)

**API эндпоинты:**
```
GET  /api/v1/products              — cursor-based пагинация (?after=cursor&limit=24)
GET  /api/v1/products/{slug}       — карточка товара
GET  /api/v1/categories            — дерево категорий (Redis TTL 10 мин)
GET  /api/v1/products/search?q=    — проксирует Meilisearch
```

**Meilisearch:**
- Индекс `products`: поля `name`, `description`, `attributes`
- Фасетный поиск по `category_id`, `price`, `attributes.*`
- Индексация при изменении товара — через Celery (`tasks/search.py`)
- Публичный ключ только для поиска: `NUXT_PUBLIC_MEILI_SEARCH_KEY`

---

### Этап 3 — Корзина, заказы, платежи ⬜ ЗАПЛАНИРОВАНО

**Корзина:**
- Redis Hash `cart:{user_id}` → `{variant_id: quantity}`
- Гостевая корзина: `cart:guest:{session_id}`, TTL 7 дней, синхронизация при логине

**Оформление заказа (workflow):**
1. Валидация остатков (Redis → резервирование)
2. Расчёт доставки через СДЭК API
3. Создание заказа в БД (статус `PENDING`)
4. Создание платёжной ссылки YooMoney
5. Webhook YooMoney → HMAC-SHA256 → подтверждение → статус `PAID`
6. Celery-таска: списание резерва + уведомление email/SMS

**Интеграция YooMoney:**
- `POST /api/v1/payments/create` → возвращает `confirmation_url`
- `POST /api/v1/payments/webhook` → идемпотентная обработка (ключ — `payment_id`)
- Проверка HMAC: `hmac.new(secret, body, sha256)`

**Интеграция СДЭК v2:**
- OAuth2 токен → кэшировать в Redis
- `POST /v2/calculator/tariff` — расчёт стоимости
- `GET  /v2/deliverypoints?city_code=` — список ПВЗ
- `POST /v2/orders` — создание накладной (после `PAID`)
- `GET  /v2/orders?cdek_number=` — трекинг

---

### Этап 4 — Блог, контент и медиа ⬜ ЗАПЛАНИРОВАНО

Блог — основной источник органического трафика для OBD2-тематики.

#### 4.1 Модели БД (`backend/app/db/models/blog.py`)

```python
class BlogCategory(Base):
    __tablename__ = "blog_category"
    id: int, name: str, slug: str, description: str | None

class Tag(Base):
    __tablename__ = "tag"
    id: int, name: str, slug: str

class BlogPost(Base):
    __tablename__ = "blog_post"
    id: int
    title: str
    slug: str               # unique, indexed; auto-generate via python-slugify
    excerpt: str            # до 300 символов — для карточки и meta_description
    content_json: dict      # JSONB — исходный формат TipTap/ProseMirror
    content_html: str       # pre-rendered HTML (быстрая отдача)
    meta_title: str | None         # fallback на title, max 60 символов
    meta_description: str | None   # fallback на excerpt, max 160 символов
    og_image_url: str | None       # URL MinIO; fallback — первое изображение
    category_id: int | None
    author_id: int
    status: str             # 'draft' | 'published' | 'archived'
    published_at: datetime | None  # для Schema.org datePublished
    created_at: datetime
    updated_at: datetime    # для Schema.org dateModified и sitemap lastmod
    views: int = 0
    reading_time_minutes: int = 0  # auto: len(words) / 200

class BlogPostTag(Base):           # M2M
    __tablename__ = "blog_post_tag"
    post_id: int, tag_id: int

class BlogPostMedia(Base):
    __tablename__ = "blog_post_media"
    id: int, post_id: int
    url: str                # путь в MinIO
    media_type: str         # 'image' | 'video'
    alt: str                # ОБЯЗАТЕЛЬНО для SEO/a11y
    caption: str | None
    width: int | None, height: int | None  # предотвращает CLS
    mime_type: str          # 'image/webp', 'video/mp4'
    size_bytes: int
    sort_order: int

class Comment(Base):
    __tablename__ = "comment"
    id: int, post_id: int, author_name: str
    author_email: str       # зашифровать Fernet (152-ФЗ)
    body: str
    status: str             # 'pending' | 'approved' | 'spam'
    created_at: datetime

class Author(Base):
    __tablename__ = "author"
    id: int, user_id: int
    display_name: str, bio: str | None
    avatar_url: str | None  # MinIO URL
```

#### 4.2 API блога

```
GET  /api/v1/blog/posts              — список (?status=published&category=&tag=&after=&limit=12)
GET  /api/v1/blog/posts/{slug}       — статья (инкремент views через Redis background_task)
GET  /api/v1/blog/categories
GET  /api/v1/blog/tags
POST /api/v1/blog/posts/{id}/comments  — создать комментарий (status=pending)
# Admin (JWT scope=admin):
POST   /api/v1/admin/blog/posts
PUT    /api/v1/admin/blog/posts/{id}
DELETE /api/v1/admin/blog/posts/{id}
PUT    /api/v1/admin/blog/comments/{id}/approve
```

**Кэширование:** Redis `blog:list:{page}:{category}:{tag}` TTL 5 мин.
Инвалидация при публикации — Celery `tasks/blog.py:invalidate_blog_cache`.

**Счётчик просмотров (fire-and-forget):**
```python
background_tasks.add_task(increment_views, post_id)
# Redis INCR blog:views:{post_id}, flush в PG каждые 10 мин через Celery Beat
```

#### 4.3 Редактор TipTap

**`frontend/package.json` зависимости:**
```json
"@tiptap/vue-3": "^2.4.0",
"@tiptap/starter-kit": "^2.4.0",
"@tiptap/extension-image": "^2.4.0",
"@tiptap/extension-youtube": "^2.4.0",
"@tiptap/extension-link": "^2.4.0",
"@tiptap/extension-placeholder": "^2.4.0",
"@tiptap/extension-character-count": "^2.4.0",
"@tiptap/extension-code-block-lowlight": "^2.4.0",
"lowlight": "^3.1.0"
```

**Сохранение:** клиент отправляет `content_json`. Backend при сохранении:
1. Генерирует `content_html` через `tiptap-python` / `lxml`
2. Санитизирует через `bleach.clean()` (whitelist тегов + атрибутов)
3. Auto-вычисляет `reading_time_minutes = max(1, len(words) // 200)`

**`bleach` whitelist:**
```python
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS | {
    'h1','h2','h3','h4','p','br','ul','ol','li',
    'strong','em','blockquote','code','pre',
    'img','figure','figcaption','a','table','thead','tbody','tr','th','td',
    'iframe',  # только YouTube/RuTube с проверкой src
}
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'width', 'height', 'loading'],
    'iframe': ['src', 'width', 'height', 'allowfullscreen'],
}
```

#### 4.4 Загрузка медиа — MinIO

**API загрузки:**
```
POST /api/v1/media/upload-url
  Body: { filename, content_type, context: "blog"|"product" }
  Response: { upload_url, object_name, public_url }
  → Клиент PUT напрямую на MinIO presigned URL

POST /api/v1/media/confirm
  Body: { object_name, alt, context, entity_id }
  → Создаёт BlogPostMedia / ProductImage
  → Запускает Celery tasks.process_image
```

**Celery обработка изображений (`tasks/media.py`):**
1. Скачать оригинал из MinIO
2. Определить `width`, `height` через Pillow → сохранить в БД
3. Конвертировать в WebP (quality=85), создать thumbnail 480px
4. Создать варианты 480px, 800px, 1200px для `srcset`
5. Загрузить все варианты обратно в MinIO
6. Обновить URL в БД на WebP-версию

**Видео в блоге:**

| Вариант | Когда использовать |
|---|---|
| A — embed YouTube/RuTube (рекомендуется) | Внешнее видео; TipTap YouTube extension; whitelist `frame-src` в CSP |
| B — загрузка MP4 в MinIO | Собственное видео; `MAX_VIDEO_SIZE_MB=200`; thumbnail через ffmpeg |

---

### Этап 5 — Административная панель ⬜ ЗАПЛАНИРОВАНО

Раздел `/admin/*` в Nuxt, защищённый JWT scope `admin`.

**Разделы:**
- **Товары**: CRUD, загрузка фото через `/api/v1/media/upload-url`
- **Заказы**: список + фильтры по статусу, смена статуса, накладная СДЭК
- **Клиенты**: список, история заказов, блокировка
- **Блог**: CRUD через TipTap-редактор, комментарии, предпросмотр
- **Медиа**: галерея, удаление из MinIO + БД
- **Интеграции**: статус СДЭК / YooMoney / MinIO / Meilisearch
- **IoT-мониторинг**: статусы устройств, очереди Redis
- **Аналитика**: выручка, топ товаров, конверсия

---

### Этап 6 — Уведомления ⬜ ЗАПЛАНИРОВАНО

Паттерн: **Event → Celery Task → Notification Channel (параллельно)**.

#### Каналы уведомлений

| Канал | Получатель | Статус |
|---|---|---|
| Email (собственный SMTP) | Пользователь + Администратор | ⬜ реализовать |
| Telegram Bot (aiogram 3) | Пользователь + Администратор | ⬜ реализовать |
| ВКонтакте (VK Notify) | Пользователь по phone/vk_id | ⬜ реализовать |
| SMS через smsc.ru | Пользователь | 🔌 заглушка |
| In-app (WebSocket) | Пользователь в ЛК | ⬜ реализовать |

#### Статусы заказа

```python
class OrderStatus(str, Enum):
    PENDING    = "pending"      # создан, ожидает оплаты
    PAID       = "paid"
    PROCESSING = "processing"
    SHIPPED    = "shipped"      # передан в СДЭК
    IN_TRANSIT = "in_transit"
    DELIVERED  = "delivered"
    CANCELLED  = "cancelled"
    REFUNDED   = "refunded"
```

#### Зависимости (добавить в requirements.txt)

```
fastapi-mail==1.4.1
jinja2==3.1.3
premailer==3.10.0    # инлайнит CSS в письмо (Gmail-совместимость)
aiogram==3.9.0
```

#### Email шаблоны (`backend/app/templates/email/`)

```
base.html              # layout: шапка, подвал, стили
order_created.html
order_paid.html
order_processing.html
order_shipped.html     # трек-номер СДЭК
order_in_transit.html
order_delivered.html
order_cancelled.html
order_refunded.html
welcome.html
password_reset.html
comment_approved.html
```

#### Celery-оркестратор (`tasks/notifications/dispatcher.py`)

```python
@celery_app.task(name="tasks.notify_order_status_changed", bind=True, max_retries=3)
def notify_order_status_changed(self, order_id: int, new_status: str, user_id: int):
    # Запускает все каналы параллельно через chord
    chord(tasks)(log_notifications_result.s(order_id=order_id))
```

#### In-App уведомления

```python
class InAppNotification(Base):
    __tablename__ = "in_app_notification"
    id: int, user_id: int, title: str, body: str
    link: str | None      # /orders/{id}
    is_read: bool = False
    created_at: datetime

# API:
GET   /api/v1/notifications
PATCH /api/v1/notifications/{id}/read
DELETE /api/v1/notifications/read-all
```

Real-time через WebSocket `/ws/notifications/{user_id}` (переиспользует инфраструктуру IoT).

#### Переменные окружения (Этап 6)

```env
MAIL_SERVER=mail.wifiobd.shop
MAIL_PORT=465
MAIL_USERNAME=noreply@wifiobd.shop
MAIL_PASSWORD=secret
MAIL_FROM=WifiOBD Shop <noreply@wifiobd.shop>
MAIL_SSL_TLS=true
MAIL_ADMIN=admin@wifiobd.shop

TELEGRAM_BOT_TOKEN=
TELEGRAM_ADMIN_CHAT_ID=

VK_NOTIFY_API_KEY=
VK_COMMUNITY_TOKEN=
VK_COMMUNITY_ID=

# SMS — заглушка, не заполнять:
# SMSC_LOGIN=
# SMSC_PASSWORD=
```

---

### Этап 7 — Безопасность ⬜ (параллельно со всеми этапами)

- **152-ФЗ**: шифрование персональных данных (имя, телефон, email) через Fernet (`cryptography`)
- **Валидация**: Pydantic-схемы на входе; параметризованные запросы SQLAlchemy
- **XSS**: `bleach.clean()` для любого HTML из пользовательского ввода
- **Rate Limiting**: `slowapi` на `/auth/*`, `/checkout`, `/media/upload-url`
- **HTTPS**: Nginx + Certbot
- **Секреты**: только через env-переменные; в CI/CD — GitLab CI/CD Variables
- **CSP**: `frame-src youtube.com rutube.ru` в Nginx-заголовке

---

### Этап 8 — IoT-интеграция (OBD2) ⬜ ЗАПЛАНИРОВАНО

- `UserDevice` модель: устройства привязаны к аккаунту
- `POST /iot/data` → Redis Stream `XADD`
- Celery-воркер: `XREAD` → PostgreSQL (TimescaleDB / партиционированные таблицы)
- WebSocket `/ws/iot/{device_id}` — real-time данные в ЛК

---

### Этап 9 — SEO и Core Web Vitals ⬜ ЗАПЛАНИРОВАНО

> Отдельный этап — не совмещать с другими. SEO требует внимательного тестирования.

#### useSeoMeta + Open Graph

```typescript
// frontend/composables/useSeo.ts
export const usePageSeo = (opts: {
  title: string; description: string; image?: string
  type?: 'website' | 'article'
  publishedAt?: string; modifiedAt?: string; author?: string
}) => {
  useSeoMeta({
    title: opts.title, description: opts.description,
    ogTitle: opts.title, ogDescription: opts.description,
    ogImage: opts.image ?? `${siteUrl}/og-default.png`,
    ogType: opts.type ?? 'website',
    ogLocale: 'ru_RU', ogSiteName: 'WifiOBD Shop',
    twitterCard: 'summary_large_image',
    ...(opts.publishedAt && { articlePublishedTime: opts.publishedAt }),
    ...(opts.modifiedAt && { articleModifiedTime: opts.modifiedAt }),
  })
  useHead({ link: [{ rel: 'canonical', href: `${siteUrl}${useRoute().path}` }] })
}
```

#### Schema.org (JSON-LD)

Реализовать через `frontend/composables/useSchemaOrg.ts`:
- `useArticleSchema(post)` — `BlogPosting` для статей блога
- `useProductSchema(product)` — `Product` + `Offer` для карточек товаров
- `useBreadcrumbSchema(crumbs)` — `BreadcrumbList` на всех вложенных страницах

#### Динамический sitemap.xml

`frontend/server/routes/sitemap.xml.ts`:
- Включает все активные товары + опубликованные статьи
- Кэш `Cache-Control: public, max-age=3600`
- `lastmod` из `updated_at` объекта

#### robots.txt

```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /cart
Disallow: /checkout
Disallow: /profile
Disallow: /api/
Disallow: /products?*
Allow: /products/$
Sitemap: https://wifiobd.shop/sitemap.xml
```

#### Canonical и дубли URL

Каталог с фильтрами (`/products?sort=price&page=2`) — canonical без сортировки/страницы, но с фильтром:
```typescript
const canonicalPath = computed(() => {
  const params = new URLSearchParams()
  if (route.query.category) params.set('category', route.query.category as string)
  return params.toString() ? `/products?${params}` : '/products'
})
```

#### Изображения и CWV

- Обязательные атрибуты каждого `<img>`: `src` (WebP), `alt`, `width`, `height`, `loading="lazy"`
- Hero-изображение: `loading="eager" fetchpriority="high"`
- `srcset` с 3 вариантами: 480w, 800w, 1200w (генерирует Celery `process_image`)
- Цели: LCP < 2.5s, CLS < 0.1, FID < 100ms, Lighthouse SEO = 100

#### Редиректы при смене slug

```python
class Redirect(Base):
    __tablename__ = "redirect"
    id: int
    old_path: str  # indexed, unique
    new_path: str
    status_code: int  # 301 или 302
    created_at: datetime
```

---

### Этап 10 — Тестирование и деплой ⬜ ЗАПЛАНИРОВАНО

**Тестирование:**
- Unit: `pytest` + `pytest-asyncio`, моки внешних API через `respx`
- Интеграционные: `TestClient` FastAPI + тестовая PostgreSQL в Docker
- Нагрузочное: `Locust` — сценарии каталога, блога, checkout
- SEO: `curl -I` на наличие canonical, OG-тегов, Schema.org
- Lighthouse CI в GitLab CI (score не блокирует деплой, но сохраняется артефактом)

---

## 4. Деплой — GitLab CI/CD (Self-Hosted)

### Инфраструктура

| Компонент | Размещение |
|---|---|
| GitLab CE | сервер `ci.internal` |
| GitLab Container Registry | встроен в GitLab CE |
| GitLab Runner (docker executor) | тот же или отдельный сервер |
| Продакшн-сервер | `prod.internal` — Docker Compose + Nginx |

### Схема пайплайна

```
git push → GitLab CE → GitLab Runner
                           ↓
                  build → test → push → deploy (manual)
                                    ↓           ↓
                        GitLab Registry    SSH → prod
                                          docker-compose up
```

### CI/CD Variables

| Переменная | Описание |
|---|---|
| `SSH_PRIVATE_KEY` | Приватный SSH-ключ (type: File) |
| `PROD_SERVER_IP` | IP prod-сервера |
| `PROD_SERVER_USER` | Пользователь `deploy` |
| `POSTGRES_PASSWORD` | Пароль БД |
| `SECRET_KEY` | FastAPI secret key |
| `YOOMONEY_SECRET` | Ключ YooMoney |
| `CDEK_CLIENT_SECRET` | Ключ СДЭК |
| `MINIO_ROOT_PASSWORD` | Пароль MinIO |
| `NUXT_PUBLIC_SITE_URL` | Canonical domain |

### `.gitlab-ci.yml` — стадии

```yaml
stages: [build, test, push, deploy]

# build:backend, build:frontend  → Docker образы → GitLab Registry
# test:backend                   → pytest в контейнере (postgres + redis)
# test:lighthouse                → @lhci/cli, allow_failure: true
# push:images                    → только main/master
# deploy:production              → SSH rsync + docker-compose pull + up, when: manual
```

### `deploy/docker-compose.prod.yml` — сервисы

```
api, celery_worker, celery_beat, frontend, postgres, redis, meilisearch, minio, nginx
```

Nginx: `Content-Security-Policy` с `frame-src youtube.com rutube.ru`, MinIO proxy `/media/` с `Cache-Control: max-age=604800, immutable`.

### Мониторинг (self-hosted)

- **Prometheus + Grafana**: `prometheus-fastapi-instrumentator`, `postgres_exporter`, `redis_exporter`
- **Loki + Promtail**: сбор JSON-логов контейнеров
- **Alerting**: Grafana → Telegram/Email при деградации

---

## 5. Ключевые паттерны

- **Repository Pattern**: сервисный слой обращается только через репозиторий
- **Dependency Injection**: сессии БД, пользователь, настройки — через `Depends()`
- **Idempotency Keys**: для платёжных операций и создания заказов
- **Optimistic Locking**: при списании остатков через поле `version` в PostgreSQL
- **Event-driven**: изменение статуса заказа → Celery-таска → уведомления
- **Circuit Breaker**: для СДЭК, YooMoney — `tenacity` с exponential backoff
- **SEO-first**: каждая публичная страница — `useSeoMeta` + Schema.org + canonical
- **Media-first**: каждое `<img>` — `alt`, `width`, `height`; WebP из MinIO
- **Sanitize always**: любой HTML из ввода пользователя → `bleach.clean()`

---

## 6. Чек-лист готовности к запуску

### Backend ✅/🔨/⬜

- [x] Этап 1: Docker Compose, auth, config, logging
- [ ] Этап 2: модули `products`, `categories`, `inventory` + Meilisearch
- [ ] Этап 3: `cart`, `orders`, YooMoney, СДЭК
- [ ] Этап 4: `blog`, `media`, TipTap, MinIO pipeline
- [ ] Alembic-миграции: `BlogPost`, `BlogPostMedia`, `Redirect`
- [ ] `bleach.clean()` для `content_html` перед сохранением
- [ ] Celery-таски: `process_image` (WebP + thumbnail + srcset), `invalidate_blog_cache`, `increment_views`

### Frontend ✅/🔨/⬜

- [ ] `useSeoMeta` на каждой публичной странице
- [ ] `useSchemaOrg` на `/blog/[slug]` (Article) и `/products/[slug]` (Product)
- [ ] `AppBreadcrumbs` с Schema.org BreadcrumbList
- [ ] `sitemap.xml`, `robots.txt`, `rss.xml` server routes
- [ ] `rel=canonical` с учётом параметров фильтрации
- [ ] `error.vue` с `robots: 'noindex'`
- [ ] Все `<img>` — `alt`, `width`, `height`, `loading="lazy"` (кроме hero)
- [ ] TipTap-редактор в `/admin/blog`

### SEO-проверка перед запуском

- [ ] `curl https://wifiobd.shop/sitemap.xml` — XML с товарами и статьями
- [ ] `curl https://wifiobd.shop/robots.txt` — `Sitemap:` и `Disallow: /admin/`
- [ ] Google Rich Results Test — товар и статья проходят Schema.org валидацию
- [ ] Lighthouse: Performance ≥ 90, SEO = 100, Accessibility ≥ 90
- [ ] PageSpeed Insights: LCP < 2.5s, CLS < 0.1, FID < 100ms

---

## 7. Переменные окружения (`.env.example`)

```env
# ── App ───────────────────────────────────────────────────────────────────────
SECRET_KEY=
DEBUG=false
ALLOWED_ORIGINS=https://wifiobd.shop

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/wifiobd
POSTGRES_USER=user
POSTGRES_PASSWORD=
POSTGRES_DB=wifiobd

# ── Redis ─────────────────────────────────────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ── MinIO ─────────────────────────────────────────────────────────────────────
MINIO_ENDPOINT=minio:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=
MINIO_BUCKET_MEDIA=media
MINIO_PUBLIC_DOMAIN=wifiobd.shop
MINIO_USE_SSL=false

# ── Meilisearch ───────────────────────────────────────────────────────────────
MEILI_MASTER_KEY=
NUXT_PUBLIC_MEILI_SEARCH_KEY=
NUXT_PUBLIC_MEILI_HOST=https://wifiobd.shop/search

# ── Payments & Delivery ───────────────────────────────────────────────────────
YOOMONEY_SHOP_ID=
YOOMONEY_SECRET=
CDEK_CLIENT_ID=
CDEK_CLIENT_SECRET=

# ── Notifications ─────────────────────────────────────────────────────────────
MAIL_SERVER=mail.wifiobd.shop
MAIL_PORT=465
MAIL_USERNAME=noreply@wifiobd.shop
MAIL_PASSWORD=
MAIL_FROM=WifiOBD Shop <noreply@wifiobd.shop>
MAIL_SSL_TLS=true
MAIL_ADMIN=admin@wifiobd.shop
TELEGRAM_BOT_TOKEN=
TELEGRAM_ADMIN_CHAT_ID=
VK_NOTIFY_API_KEY=
VK_COMMUNITY_TOKEN=
VK_COMMUNITY_ID=
# SMSC_LOGIN=      # SMS — заглушка
# SMSC_PASSWORD=

# ── SEO ───────────────────────────────────────────────────────────────────────
NUXT_PUBLIC_SITE_URL=https://wifiobd.shop
NUXT_PUBLIC_OG_DEFAULT_IMAGE=/og-default.png
NUXT_API_BASE=http://api:8000
NUXT_PUBLIC_API_BASE=https://wifiobd.shop
```
