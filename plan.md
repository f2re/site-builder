> Документ обновлён: добавлены технические детали по блогу (TipTap, MinIO, медиа, видео),
> SEO (sitemap, robots.txt, Schema.org, Open Graph, canonical, breadcrumbs, Core Web Vitals),
> а также исправлены пробелы в requirements и моделях, выявленные в ходе UI/UX-аудита.

---

# Техническое задание: Интернет-магазин на FastAPI + Nuxt 3

## 1. Архитектурная концепция

Система строится на **модульной Clean Architecture**: каждый домен (товары, заказы, блог, IoT) — изолированный модуль со своими роутерами, схемами, сервисами и репозиториями. Это позволяет масштабировать и тестировать каждый модуль независимо. Асинхронность FastAPI + SQLAlchemy async обеспечивает максимальную производительность на I/O-операциях.

**Технологический стек:**

| Слой | Технология | Обоснование |
|------|-----------|-------------|
| Backend API | FastAPI (Python 3.12+) | Async-first, автодокументация Swagger/ReDoc, type hints |
| ORM | SQLAlchemy 2.x (async) + Alembic | Миграции, type-safe запросы |
| БД основная | PostgreSQL 16 | ACID, JSONB для атрибутов товаров |
| Кэш / Очереди | Redis 7 | Кэш каталога, корзина, инвентарь в реальном времени |
| Фоновые задачи | Celery + Redis broker | Email/SMS, обновление курсов, обработка заказов, ресайз медиа |
| Frontend | Nuxt 3 (Vue 3 + Pinia) | SSR для SEO блога и каталога, `useSeoMeta`, `useSchemaOrg` |
| Хранилище медиа | MinIO (self-hosted S3) | Изображения и видео товаров/блога, presigned URL |
| Контейнеризация | Docker Compose (dev) / Docker Compose + Nginx (prod) | Self-hosted, без внешних cloud-провайдеров |
| CI/CD | GitLab CE (self-hosted) + GitLab Runner + GitLab Container Registry | Полностью локальный пайплайн без Docker Hub |
| Поиск | Meilisearch | Полнотекстовый поиск товаров, лёгкий self-hosted |

---

## 2. Структура проекта

```
project/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── products/    # роутер, схемы, сервис, репозиторий
│   │   │       ├── orders/
│   │   │       ├── cart/
│   │   │       ├── blog/        # см. Этап 4 — полный модуль
│   │   │       ├── media/       # см. Этап 4 — загрузка в MinIO
│   │   │       ├── delivery/    # СДЭК
│   │   │       ├── payments/    # YooMoney
│   │   │       ├── iot/
│   │   │       └── users/
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic Settings
│   │   │   ├── security.py      # JWT, bcrypt
│   │   │   └── dependencies.py
│   │   ├── db/
│   │   │   ├── models/
│   │   │   └── migrations/      # Alembic
│   │   ├── tasks/               # Celery tasks (email, медиа, поиск)
│   │   └── integrations/
│   │       ├── cdek.py
│   │       ├── yoomoney.py
│   │       ├── minio.py         # MinIO/S3 клиент
│   │       └── cbr_rates.py
├── frontend/
│   ├── pages/
│   │   ├── index.vue
│   │   ├── products/
│   │   │   ├── index.vue        # каталог
│   │   │   └── [slug].vue       # карточка товара (Schema.org Product)
│   │   ├── blog/
│   │   │   ├── index.vue        # список статей
│   │   │   └── [slug].vue       # статья (Schema.org Article)
│   │   ├── cart/index.vue
│   │   └── [...].vue            # 404 catch-all → error.vue
│   ├── composables/
│   │   ├── useSchemaOrg.ts      # хелперы для JSON-LD
│   │   └── useSeo.ts            # обёртка над useSeoMeta
│   ├── components/
│   │   ├── AppHeader.vue
│   │   ├── AppFooter.vue
│   │   ├── AppBreadcrumbs.vue   # Schema.org BreadcrumbList
│   │   └── U/
│   │       ├── UThemeToggle.vue
│   │       └── USearchModal.vue
│   ├── server/
│   │   ├── routes/
│   │   │   ├── sitemap.xml.ts   # динамический sitemap
│   │   │   ├── robots.txt.ts    # robots.txt
│   │   │   └── rss.xml.ts       # RSS-фид блога
│   │   └── plugins/
│   ├── assets/css/
│   │   ├── tokens.css
│   │   └── main.css
│   └── stores/
│       ├── themeStore.ts
│       └── cartStore.ts
├── deploy/
│   ├── docker-compose.prod.yml
│   └── nginx/nginx.conf
└── .gitlab-ci.yml
```

---

## 3. Этапы разработки

### Этап 1 — Инфраструктура и ядро (2–3 нед.)

- **Docker Compose**: сервисы `api`, `postgres`, `redis`, `celery_worker`, `celery_beat`, `frontend`, `meilisearch`, `minio`
- **Конфигурация**: `Pydantic BaseSettings` — все секреты из `.env`, никаких хардкодов
- **БД**: асинхронное подключение через `asyncpg`, сессии через Dependency Injection
- **Аутентификация**: JWT (access 15 мин + refresh 7 дней), `bcrypt`/`argon2`, роли: `admin`, `manager`, `customer`
- **Логирование**: `structlog` JSON-логи, middleware логирует каждый запрос (метод, путь, статус, время)
- **Обработка ошибок**: глобальные exception handlers, никаких internal details в ответах клиенту

**requirements.txt — полный список зависимостей:**
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
# MinIO / S3
miniopy-async==1.19.0          # async MinIO клиент
# Медиа-обработка
Pillow==10.3.0                  # ресайз изображений, WebP конвертация
# Безопасность контента
bleach==6.1.0                   # санитизация HTML из TipTap
# Полнотекстовый поиск
meilisearch-python-sdk==3.0.0
# Celery
celery[redis]==5.3.6
# Курсы валют, HTTP
httpx==0.27.0
# Тесты
pytest==8.1.0
pytest-asyncio==0.23.6
httpx==0.27.0                   # для TestClient
respx==0.21.1                   # мокирование HTTP
# Линтеры
ruff==0.3.2
mypy==1.9.0
types-python-jose==3.3.4.20240106
types-passlib==1.7.7.20240311
```

---

### Этап 2 — Каталог товаров и инвентарь (2–3 нед.)

**Модели БД (`backend/app/db/models/products.py`):**
```python
class Category(Base):
    id: int, name: str, slug: str, parent_id: int | None
    # LTREE или Adjacency List для дерева категорий
    # Индекс: CREATE INDEX ON category USING GIST(path) — если LTREE

class Product(Base):
    id: int, name: str, slug: str (unique, indexed)
    description_html: str      # sanitized HTML
    attributes: dict           # JSONB — динамические хар-ки
    category_id: int
    price: Decimal
    is_active: bool
    meta_title: str | None     # SEO
    meta_description: str | None  # SEO, max 160 символов
    og_image_url: str | None   # Open Graph
    created_at: datetime, updated_at: datetime

class ProductImage(Base):
    id: int, product_id: int
    url: str                   # MinIO URL (без домена — только путь)
    alt: str                   # ОБЯЗАТЕЛЬНО для SEO и a11y
    is_cover: bool
    sort_order: int
    width: int, height: int    # для <img width height> предотвращает CLS

class ProductVariant(Base):
    id: int, product_id: int
    sku: str (unique), name: str
    price: Decimal, stock: int

class StockMovement(Base):
    id: int, variant_id: int
    delta: int, reason: str    # 'sale', 'return', 'correction'
    created_at: datetime
```

**Инвентарь (остатки) — Redis + PostgreSQL:**
- PostgreSQL — источник правды для остатков
- Redis Hash `stock:{variant_id}` — быстрое чтение
- При добавлении в корзину — резервирование через Redis lease с TTL 30 мин
- Lua-скрипты для атомарного списания (исключает race conditions)

**API эндпоинты:**
```
GET  /api/v1/products              — пагинация cursor-based (?after=cursor&limit=24)
GET  /api/v1/products/{slug}       — карточка товара
GET  /api/v1/categories            — дерево категорий (Redis TTL 10 мин)
GET  /api/v1/products/search?q=    — проксирует Meilisearch
```

**Поиск — Meilisearch:**
- Индекс `products`: поля `name`, `description`, `attributes`
- Фасетный поиск по `category_id`, `price`, `attributes.*`
- Индексация при изменении товара — через Celery-таску (`tasks/search.py`)
- Ключ только для поиска (`searchApiKey`) публикуется в `NUXT_PUBLIC_MEILI_SEARCH_KEY`

---

### Этап 3 — Корзина, заказы, платежи (2–3 нед.)

**Корзина:**
- Redis Hash `cart:{user_id}` → `{variant_id: quantity}`
- Для гостей — `cart:guest:{session_id}`, синхронизация при логине
- TTL корзины гостя — 7 дней

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

**Интеграция СДЭК v2 API:**
- OAuth2: `POST https://api.cdek.ru/v2/oauth/token` → кэшировать токен в Redis
- `POST /v2/calculator/tariff` — расчёт стоимости
- `GET  /v2/deliverypoints?city_code=` — список ПВЗ
- `POST /v2/orders` — создание накладной (после `PAID`)
- `GET  /v2/orders?cdek_number=` — трекинг

---

### Этап 4 — Блог, контент и медиа (2–3 нед.)

Это ключевой SEO-этап. Блог — основной источник органического трафика для OBD2-тематики.

#### 4.1 Модели БД (`backend/app/db/models/blog.py`)

```python
class BlogCategory(Base):
    __tablename__ = "blog_category"
    id: int
    name: str
    slug: str  # unique, indexed
    description: str | None

class Tag(Base):
    __tablename__ = "tag"
    id: int
    name: str
    slug: str  # unique

class BlogPost(Base):
    __tablename__ = "blog_post"
    id: int
    title: str
    slug: str               # unique, indexed; auto-generate из title через python-slugify
    excerpt: str            # краткое описание (до 300 символов) — для карточки и meta_description
    # Контент хранится в двух форматах:
    content_json: dict      # JSONB — исходный формат TipTap/ProseMirror (для редактирования)
    content_html: str       # pre-rendered HTML (для быстрой отдачи без рендера на лету)
    # SEO поля
    meta_title: str | None         # если пусто — fallback на title, max 60 символов
    meta_description: str | None   # если пусто — fallback на excerpt, max 160 символов
    og_image_url: str | None       # URL из MinIO; если пусто — первое изображение из content
    # Отношения
    category_id: int | None
    author_id: int
    # Статус и даты
    status: str             # 'draft' | 'published' | 'archived'
    published_at: datetime | None  # для Schema.org datePublished
    created_at: datetime
    updated_at: datetime    # для Schema.org dateModified и sitemap lastmod
    # Метрики
    views: int = 0
    reading_time_minutes: int = 0   # auto-calculate: len(words) / 200

class BlogPostTag(Base):
    __tablename__ = "blog_post_tag"
    post_id: int, tag_id: int  # M2M

class BlogPostMedia(Base):
    __tablename__ = "blog_post_media"
    id: int
    post_id: int
    url: str                # путь в MinIO (без домена)
    media_type: str         # 'image' | 'video'
    alt: str                # ОБЯЗАТЕЛЬНО — для SEO и a11y изображений
    caption: str | None     # подпись под медиа
    width: int | None       # для изображений (предотвращает CLS)
    height: int | None
    mime_type: str          # 'image/webp', 'image/jpeg', 'video/mp4'
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

#### 4.2 API эндпоинты блога (`backend/app/api/v1/blog/router.py`)

```
GET  /api/v1/blog/posts              — список статей (?status=published&category=&tag=&after=cursor&limit=12)
GET  /api/v1/blog/posts/{slug}       — статья (+ инкремент views через Redis, async)
GET  /api/v1/blog/categories         — список категорий
GET  /api/v1/blog/tags               — список тегов
POST /api/v1/blog/posts/{id}/comments — создать комментарий (status=pending)
# Admin-only (JWT scope=admin):
POST   /api/v1/admin/blog/posts      — создать статью
PUT    /api/v1/admin/blog/posts/{id} — обновить
DELETE /api/v1/admin/blog/posts/{id} — удалить / архивировать
PUT    /api/v1/admin/blog/comments/{id}/approve
```

**Кэширование:** Redis ключ `blog:list:{page}:{category}:{tag}` TTL 5 мин.
Инвалидация при публикации/обновлении — через Celery-таску `tasks/blog.py:invalidate_blog_cache`.

**Счётчик просмотров без блокировки:**
```python
# В GET /blog/posts/{slug} — не ждём, fire-and-forget
background_tasks.add_task(increment_views, post_id)
# increment_views: Redis INCR blog:views:{post_id}, flush в PG каждые 10 мин через Celery Beat
```

#### 4.3 Редактор контента — TipTap

**Frontend установка (`frontend/package.json`):**
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

**Компонент редактора (`frontend/components/Admin/BlogEditor.vue`):**
```vue
<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Youtube from '@tiptap/extension-youtube'
// ...

const editor = useEditor({
  extensions: [
    StarterKit,
    Image.configure({ HTMLAttributes: { loading: 'lazy' } }),
    Youtube.configure({ width: 640, height: 360 }),
    // ...
  ],
  content: props.modelValue,
  onUpdate: ({ editor }) => emit('update:modelValue', editor.getJSON()),
})
</script>
```

**Сохранение:** клиент отправляет `content_json` (TipTap JSON).
Backend (`blog/service.py`) при сохранении:
1. Генерирует `content_html` через `tiptap-python` или `lxml`
2. Санитизирует `content_html` через `bleach`:
```python
import bleach
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS | {
    'h1','h2','h3','h4','p','br','ul','ol','li',
    'strong','em','blockquote','code','pre',
    'img','figure','figcaption','a','table','thead','tbody','tr','th','td',
    'iframe',  # только для YouTube embed с проверкой src
}
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'width', 'height', 'loading'],
    'iframe': ['src', 'width', 'height', 'allowfullscreen'],  # src whitelist: youtube.com, rutube.ru
}
clean_html = bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
```
3. Auto-вычисляет `reading_time_minutes = max(1, len(clean_html.split()) // 200)`

#### 4.4 Загрузка медиафайлов — MinIO

**Backend интеграция (`backend/app/integrations/minio.py`):**
```python
from miniopy_async import Minio

minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=settings.MINIO_USE_SSL,
)

async def get_presigned_upload_url(object_name: str, content_type: str) -> str:
    """Возвращает presigned PUT URL для прямой загрузки из браузера."""
    return await minio_client.presigned_put_object(
        settings.MINIO_BUCKET_MEDIA,
        object_name,
        expires=timedelta(minutes=15),
    )

async def get_public_url(object_name: str) -> str:
    return f"https://{settings.MINIO_PUBLIC_DOMAIN}/{settings.MINIO_BUCKET_MEDIA}/{object_name}"
```

**API загрузки (`backend/app/api/v1/media/router.py`):**
```
POST /api/v1/media/upload-url
  Body: { filename: str, content_type: str, context: "blog"|"product" }
  Response: { upload_url: str, object_name: str, public_url: str }
  → Клиент делает PUT напрямую на MinIO presigned URL (без проксирования через FastAPI)
  → После загрузки клиент вызывает:
POST /api/v1/media/confirm
  Body: { object_name: str, alt: str, context: "blog"|"product", entity_id: int }
  → Создаёт запись BlogPostMedia или ProductImage в БД
  → Запускает Celery-таску process_image
```

**Celery-таска обработки изображений (`backend/app/tasks/media.py`):**
```python
@celery_app.task(name="tasks.process_image")
def process_image(object_name: str, media_id: int):
    """
    1. Скачать оригинал из MinIO
    2. Получить реальные размеры (width, height) через Pillow — сохранить в БД
    3. Конвертировать в WebP (quality=85): Pillow img.save(..., 'WEBP', quality=85)
    4. Создать thumbnail 480px (для карточек): img.thumbnail((480, 480))
    5. Загрузить WebP + thumbnail обратно в MinIO с именами:
       - {original_name}.webp
       - {original_name}_thumb.webp
    6. Обновить url в BlogPostMedia/ProductImage на WebP-версию
    7. Удалить оригинальный файл из MinIO (опционально — оставить как fallback)
    """
```

**Видео в блоге — два подхода:**

*Вариант A — embed (YouTube/RuTube, рекомендуется):*
- TipTap YouTube extension встраивает `<iframe>` по URL
- В `content_json` хранится `{ type: "youtube", attrs: { src: "https://youtube.com/..." } }`
- Добавить `.env` переменную `ALLOWED_VIDEO_HOSTS=youtube.com,rutube.ru`
- Bleach whitelist для `<iframe src>`: проверять `urlparse(src).hostname in ALLOWED_VIDEO_HOSTS`

*Вариант B — загрузка MP4 в MinIO (для собственного видео):*
- Поле `media_type='video'` в `BlogPostMedia`
- Ограничение размера: `MAX_VIDEO_SIZE_MB=200` (проверка до presigned URL)
- Frontend рендер: `<video controls preload="none" poster="{thumbnail_url}"><source src="{url}" type="video/mp4"></video>`
- Thumbnail для видео: генерировать через `ffmpeg` в Celery-таске (опционально)

---

### Этап 5 — Административная панель (2 нед.)

Отдельный раздел Nuxt (`/admin/*`), защищённый JWT scope `admin`:

**Разделы:**
- **Товары**: CRUD, загрузка фото (использует `/api/v1/media/upload-url`)
- **Заказы**: список с фильтрами по статусу, ручная смена статуса, накладная СДЭК
- **Клиенты**: список, история заказов, блокировка
- **Блог**: CRUD статей через TipTap-редактор, управление комментариями, предпросмотр
- **Медиа**: галерея загруженных файлов, удаление из MinIO + БД
- **Интеграции**: статус СДЭК/YooMoney/MinIO/Meilisearch
- **IoT-мониторинг**: статусы устройств, очереди Redis
- **Аналитика**: выручка, топ товаров, конверсия

---

### Этап 6 — Уведомления и курсы валют (1 нед.)

**Email** через `fastapi-mail` (SMTP):
- Подтверждение заказа, смена статуса, регистрация, одобрение комментария

**SMS** через `smsc.ru` API:
- Уведомление о доставке

**Курсы валют ЦБ РФ:**
- Celery Beat раз в час: `GET https://www.cbr-xml-daily.ru/daily_json.js`
- Сохранение в PostgreSQL + Redis-кэш `cbr:rates`

---

### Этап 7 — Безопасность (параллельно со всеми этапами)

- **152-ФЗ**: шифрование персональных данных (имя, телефон, email) в БД через Fernet (`cryptography`)
- **Валидация**: Pydantic-схемы на входе; параметризованные запросы SQLAlchemy
- **XSS**: `bleach.clean()` для любого HTML из пользовательского ввода (TipTap, комментарии)
- **Rate Limiting**: `slowapi` на `/auth/*`, `/checkout`, `/media/upload-url`
- **HTTPS**: Nginx + Certbot / самоподписанные сертификаты
- **Секреты**: только через переменные окружения; в CI/CD — GitLab CI/CD Variables
- **Content Security Policy**: Nginx заголовок, разрешающий `frame-src youtube.com rutube.ru`

---

### Этап 8 — IoT-интеграция (OBD2) (2 нед.)

- `UserDevice` модель: устройства привязаны к аккаунту
- `POST /iot/data` → Redis Stream `XADD`
- Celery-воркер читает `XREAD` → PostgreSQL (TimescaleDB / партиционированные таблицы по дате)
- WebSocket `/ws/iot/{device_id}` — real-time данные в личном кабинете

---

### Этап 9 — SEO и техническая оптимизация (1–2 нед.)

**Это отдельный этап, не совмещать с другими — SEO требует внимательного тестирования.**

#### 9.1 SSR и мета-теги (Nuxt 3)

Использовать `useSeoMeta` во всех страницах:

```typescript
// frontend/composables/useSeo.ts
export const usePageSeo = (opts: {
  title: string
  description: string
  image?: string
  type?: 'website' | 'article'
  publishedAt?: string
  modifiedAt?: string
  author?: string
}) => {
  const siteUrl = useRuntimeConfig().public.siteUrl

  useSeoMeta({
    title: opts.title,
    description: opts.description,
    ogTitle: opts.title,
    ogDescription: opts.description,
    ogImage: opts.image ?? `${siteUrl}/og-default.png`,
    ogType: opts.type ?? 'website',
    ogLocale: 'ru_RU',
    ogSiteName: 'WifiOBD Shop',
    twitterCard: 'summary_large_image',
    twitterTitle: opts.title,
    twitterDescription: opts.description,
    twitterImage: opts.image,
    // Article-specific
    ...(opts.publishedAt && { articlePublishedTime: opts.publishedAt }),
    ...(opts.modifiedAt && { articleModifiedTime: opts.modifiedAt }),
    ...(opts.author && { articleAuthor: opts.author }),
  })

  // Canonical URL — предотвращает дубли при фильтрации
  useHead({
    link: [{ rel: 'canonical', href: `${siteUrl}${useRoute().path}` }],
  })
}
```

**Пример использования на странице статьи (`pages/blog/[slug].vue`):**
```typescript
usePageSeo({
  title: post.meta_title || post.title,
  description: post.meta_description || post.excerpt,
  image: post.og_image_url,
  type: 'article',
  publishedAt: post.published_at,
  modifiedAt: post.updated_at,
  author: post.author.display_name,
})
```

#### 9.2 Schema.org (JSON-LD)

Реализовать через composable `frontend/composables/useSchemaOrg.ts`:

```typescript
export const useArticleSchema = (post: BlogPost) => {
  const siteUrl = useRuntimeConfig().public.siteUrl
  useHead({
    script: [{
      type: 'application/ld+json',
      children: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        headline: post.title,
        description: post.excerpt,
        image: post.og_image_url,
        datePublished: post.published_at,
        dateModified: post.updated_at,
        author: {
          '@type': 'Person',
          name: post.author.display_name,
        },
        publisher: {
          '@type': 'Organization',
          name: 'WifiOBD Shop',
          logo: { '@type': 'ImageObject', url: `${siteUrl}/logo.png` },
        },
        mainEntityOfPage: { '@type': 'WebPage', '@id': `${siteUrl}/blog/${post.slug}` },
        wordCount: post.content_html?.split(' ').length,
        timeRequired: `PT${post.reading_time_minutes}M`,
      }),
    }],
  })
}

export const useProductSchema = (product: Product) => {
  useHead({
    script: [{
      type: 'application/ld+json',
      children: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'Product',
        name: product.name,
        description: product.excerpt,
        image: product.cover_image_url,
        sku: product.sku,
        offers: {
          '@type': 'Offer',
          price: product.price,
          priceCurrency: 'RUB',
          availability: product.in_stock
            ? 'https://schema.org/InStock'
            : 'https://schema.org/OutOfStock',
          seller: { '@type': 'Organization', name: 'WifiOBD Shop' },
        },
      }),
    }],
  })
}

export const useBreadcrumbSchema = (crumbs: { name: string; url: string }[]) => {
  useHead({
    script: [{
      type: 'application/ld+json',
      children: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        itemListElement: crumbs.map((c, i) => ({
          '@type': 'ListItem',
          position: i + 1,
          name: c.name,
          item: c.url,
        })),
      }),
    }],
  })
}
```

#### 9.3 Динамический `sitemap.xml`

Реализовать Nuxt server route `frontend/server/routes/sitemap.xml.ts`:

```typescript
import { defineEventHandler } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.apiBase  // внутренний URL FastAPI
  const siteUrl = config.public.siteUrl

  // Получить данные из FastAPI (SSR-side, без CORS)
  const [products, posts] = await Promise.all([
    $fetch<{ items: Product[] }>(`${apiBase}/api/v1/products?limit=1000&status=active`),
    $fetch<{ items: BlogPost[] }>(`${apiBase}/api/v1/blog/posts?limit=1000&status=published`),
  ])

  const staticUrls = [
    { loc: siteUrl, priority: '1.0', changefreq: 'daily' },
    { loc: `${siteUrl}/products`, priority: '0.9', changefreq: 'daily' },
    { loc: `${siteUrl}/blog`, priority: '0.8', changefreq: 'daily' },
    { loc: `${siteUrl}/about`, priority: '0.5', changefreq: 'monthly' },
    { loc: `${siteUrl}/delivery`, priority: '0.5', changefreq: 'monthly' },
    { loc: `${siteUrl}/contacts`, priority: '0.5', changefreq: 'monthly' },
  ]

  const productUrls = products.items.map(p => ({
    loc: `${siteUrl}/products/${p.slug}`,
    lastmod: p.updated_at.split('T')[0],
    priority: '0.8',
    changefreq: 'weekly',
  }))

  const postUrls = posts.items.map(p => ({
    loc: `${siteUrl}/blog/${p.slug}`,
    lastmod: p.updated_at.split('T')[0],
    priority: '0.7',
    changefreq: 'monthly',
  }))

  const allUrls = [...staticUrls, ...productUrls, ...postUrls]

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${allUrls.map(u => `  <url>
    <loc>${u.loc}</loc>
    ${u.lastmod ? `<lastmod>${u.lastmod}</lastmod>` : ''}
    <changefreq>${u.changefreq}</changefreq>
    <priority>${u.priority}</priority>
  </url>`).join('\n')}
</urlset>`

  setHeader(event, 'Content-Type', 'application/xml')
  setHeader(event, 'Cache-Control', 'public, max-age=3600')  // кэш 1 час
  return xml
})
```

#### 9.4 `robots.txt`

`frontend/server/routes/robots.txt.ts`:
```typescript
export default defineEventHandler((event) => {
  const siteUrl = useRuntimeConfig().public.siteUrl
  setHeader(event, 'Content-Type', 'text/plain')
  return `User-agent: *
Allow: /
Disallow: /admin/
Disallow: /cart
Disallow: /checkout
Disallow: /profile
Disallow: /api/
Disallow: /products?*     # блокировать параметрические дубли
Allow: /products/$         # разрешить основную страницу каталога

Sitemap: ${siteUrl}/sitemap.xml
`
})
```

#### 9.5 RSS-фид (`frontend/server/routes/rss.xml.ts`)

```typescript
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const posts = await $fetch(`${config.apiBase}/api/v1/blog/posts?limit=20&status=published`)

  const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>WifiOBD Blog</title>
    <link>${config.public.siteUrl}/blog</link>
    <description>Статьи об OBD2 диагностике автомобилей</description>
    <language>ru</language>
    <atom:link href="${config.public.siteUrl}/rss.xml" rel="self" type="application/rss+xml"/>
    ${posts.items.map(p => `
    <item>
      <title><![CDATA[${p.title}]]></title>
      <link>${config.public.siteUrl}/blog/${p.slug}</link>
      <guid isPermaLink="true">${config.public.siteUrl}/blog/${p.slug}</guid>
      <description><![CDATA[${p.excerpt}]]></description>
      <pubDate>${new Date(p.published_at).toUTCString()}</pubDate>
    </item>`).join('')}
  </channel>
</rss>`

  setHeader(event, 'Content-Type', 'application/rss+xml; charset=utf-8')
  setHeader(event, 'Cache-Control', 'public, max-age=1800')
  return rss
})
```

#### 9.6 Хлебные крошки (`frontend/components/AppBreadcrumbs.vue`)

```vue
<script setup lang="ts">
import { useBreadcrumbSchema } from '~/composables/useSchemaOrg'

interface Crumb { label: string; to?: string }
const props = defineProps<{ crumbs: Crumb[] }>()
const config = useRuntimeConfig()

// Inject Schema.org
useBreadcrumbSchema(
  props.crumbs.map(c => ({
    name: c.label,
    url: c.to ? `${config.public.siteUrl}${c.to}` : config.public.siteUrl,
  }))
)
</script>
<template>
  <nav aria-label="Хлебные крошки">
    <ol class="breadcrumbs" itemscope itemtype="https://schema.org/BreadcrumbList">
      <li
        v-for="(crumb, i) in crumbs"
        :key="i"
        itemprop="itemListElement"
        itemscope
        itemtype="https://schema.org/ListItem"
      >
        <NuxtLink v-if="crumb.to" :to="crumb.to" itemprop="item">
          <span itemprop="name">{{ crumb.label }}</span>
        </NuxtLink>
        <span v-else itemprop="name">{{ crumb.label }}</span>
        <meta itemprop="position" :content="String(i + 1)" />
      </li>
    </ol>
  </nav>
</template>
```

**Использование на странице товара:**
```typescript
// pages/products/[slug].vue
useBreadcrumbs([
  { label: 'Главная', to: '/' },
  { label: 'Каталог', to: '/products' },
  { label: product.category.name, to: `/products?category=${product.category.slug}` },
  { label: product.name },  // текущая страница — без ссылки
])
```

#### 9.7 `rel=canonical` и дубли URL

Каталог с фильтрами (`/products?category=obd2&sort=price&page=2`) генерирует дубли.
Правило: canonical всегда указывает на URL **без** query-параметров сортировки/страницы, но **с** параметрами фильтра:

```typescript
// pages/products/index.vue
const route = useRoute()
const canonicalPath = computed(() => {
  const params = new URLSearchParams()
  if (route.query.category) params.set('category', route.query.category as string)
  const q = params.toString()
  return q ? `/products?${q}` : '/products'
})
useHead({
  link: [{ rel: 'canonical', href: `${siteUrl}${canonicalPath.value}` }],
})
```

#### 9.8 Изображения и Core Web Vitals

Все изображения в блоге и каталоге должны:

```html
<!-- Обязательные атрибуты для каждого <img> -->
<img
  :src="image.url"           <!-- WebP из MinIO -->
  :alt="image.alt"           <!-- из поля alt в BlogPostMedia / ProductImage -->
  :width="image.width"       <!-- из БД — предотвращает CLS (Cumulative Layout Shift) -->
  :height="image.height"
  loading="lazy"             <!-- для всех изображений кроме первого (above the fold) -->
  decoding="async"
/>
<!-- Первое изображение (hero / cover) — без lazy, с fetchpriority: -->
<img ... loading="eager" fetchpriority="high" />
```

**`srcset` для адаптивных изображений:**
Celery-таска `process_image` создаёт 3 размера: 480px, 800px, 1200px.
Frontend использует `srcset`:
```html
<img
  :srcset="`${img_480} 480w, ${img_800} 800w, ${img_1200} 1200w`"
  sizes="(max-width: 600px) 480px, (max-width: 1024px) 800px, 1200px"
  :src="img_800"
  :alt="alt"
/>
```

#### 9.9 `hreflang` (для будущей локализации)

В `nuxt.config.ts` добавить уже сейчас — для однозначной идентификации языка:
```typescript
app: {
  head: {
    link: [
      { rel: 'alternate', hreflang: 'ru', href: process.env.NUXT_PUBLIC_SITE_URL },
    ]
  }
}
```

#### 9.10 Страница 404 и редиректы

`frontend/error.vue`:
```vue
<script setup lang="ts">
const error = useError()
useSeoMeta({ title: 'Страница не найдена — WifiOBD Shop', robots: 'noindex' })
</script>
<template>
  <div v-if="error.statusCode === 404">
    <h1>404 — Страница не найдена</h1>
    <NuxtLink to="/">На главную</NuxtLink>
  </div>
</template>
```

**Редиректы при смене slug** — server middleware `frontend/server/middleware/redirects.ts`:
```typescript
// Хранить таблицу редиректов в PostgreSQL: old_path → new_path, status_code
// При GET запросе — проверять Redis-кэш `redirect:{path}`, fallback → PG
export default defineEventHandler(async (event) => {
  const path = getRequestURL(event).pathname
  const redirect = await getRedirect(path)  // Redis → PG
  if (redirect) {
    await sendRedirect(event, redirect.new_path, redirect.status_code)
  }
})
```

**Backend модель редиректов:**
```python
class Redirect(Base):
    __tablename__ = "redirect"
    id: int
    old_path: str   # indexed, unique
    new_path: str
    status_code: int  # 301 или 302
    created_at: datetime
```

#### 9.11 Переменные окружения для SEO

Добавить в `.env.example`:
```env
# ── SEO ───────────────────────────────────────────────────────────────────────
NUXT_PUBLIC_SITE_URL=https://wifiobd.shop     # canonical domain
NUXT_PUBLIC_OG_DEFAULT_IMAGE=/og-default.png  # fallback OG image
```

И в `nuxt.config.ts`:
```typescript
runtimeConfig: {
  apiBase: process.env.NUXT_API_BASE || 'http://api:8000',  // server-side
  public: {
    siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000',
    apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
  },
},
```

---

### Этап 10 — Тестирование и деплой (1–2 нед.)

**Тестирование:**
- Unit: `pytest` + `pytest-asyncio`, моки внешних API через `respx`
- Интеграционные: `TestClient` FastAPI + тестовая PostgreSQL в Docker
- SEO-тестирование: проверить все страницы через `curl -I` на наличие canonical, OG-тегов, Schema.org
- Нагрузочное: `Locust` — сценарии каталога, блога, checkout
- Lighthouse CI: интегрировать в GitLab CI для автоматической проверки Core Web Vitals

**Lighthouse CI в `.gitlab-ci.yml`:**
```yaml
test:lighthouse:
  stage: test
  image: node:20-alpine
  script:
    - npm install -g @lhci/cli
    - lhci autorun --upload.target=filesystem --upload.outputDir=./lhci-results
  artifacts:
    paths: [lhci-results/]
  allow_failure: true  # не блокировать деплой, но сохранять отчёт
```

---

## Деплой — GitLab CI/CD (Self-Hosted, без Docker Hub)

### Инфраструктурные требования

| Компонент | Размещение | Описание |
|---|---|---|
| **GitLab CE** | сервер CI (`ci.internal`) | Хранит код, запускает пайплайны |
| **GitLab Container Registry** | встроен в GitLab CE | Хранит Docker-образы |
| **GitLab Runner** | тот же или отдельный сервер | executor: `docker` |
| **Продакшн-сервер** | `prod.internal` | Docker Compose + Nginx |

### Схема пайплайна

```
git push → GitLab CE (self-hosted)
              ↓
         GitLab Runner (Docker executor)
              ↓
     build → test → push → deploy
                       ↓         ↓
           GitLab Container   SSH → prod-сервер
              Registry           docker-compose pull + up
```

### GitLab CI/CD Variables

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
| `NUXT_PUBLIC_SITE_URL` | Canonical domain (для sitemap/SEO) |

### `.gitlab-ci.yml`

```yaml
stages: [build, test, push, deploy]

variables:
  DOCKER_DRIVER: overlay2
  BACKEND_IMAGE:  $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHORT_SHA
  FRONTEND_IMAGE: $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHORT_SHA
  BACKEND_IMAGE_LATEST:  $CI_REGISTRY_IMAGE/backend:latest
  FRONTEND_IMAGE_LATEST: $CI_REGISTRY_IMAGE/frontend:latest

build:backend:
  stage: build
  image: docker:26
  services: [docker:26-dind]
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
  script:
    - docker build --cache-from "$BACKEND_IMAGE_LATEST" --build-arg BUILDKIT_INLINE_CACHE=1
        -t "$BACKEND_IMAGE" -t "$BACKEND_IMAGE_LATEST" -f backend/Dockerfile ./backend
  tags: [docker]

build:frontend:
  stage: build
  image: docker:26
  services: [docker:26-dind]
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
  script:
    - docker build --cache-from "$FRONTEND_IMAGE_LATEST" --build-arg BUILDKIT_INLINE_CACHE=1
        -t "$FRONTEND_IMAGE" -t "$FRONTEND_IMAGE_LATEST" -f frontend/Dockerfile ./frontend
  tags: [docker]

test:backend:
  stage: test
  image: $BACKEND_IMAGE
  services: [postgres:16-alpine, redis:7-alpine]
  variables:
    DATABASE_URL: "postgresql+asyncpg://postgres:postgres@postgres/testdb"
    REDIS_URL: "redis://redis:6379/0"
    POSTGRES_DB: testdb
    POSTGRES_PASSWORD: postgres
  script:
    - cd /app && pytest tests/ -v --tb=short
  tags: [docker]

test:lighthouse:
  stage: test
  image: node:20-alpine
  script:
    - npm install -g @lhci/cli
    - lhci autorun --upload.target=filesystem --upload.outputDir=./lhci-results
  artifacts:
    paths: [lhci-results/]
  allow_failure: true
  tags: [docker]

push:images:
  stage: push
  image: docker:26
  services: [docker:26-dind]
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
  script:
    - docker push "$BACKEND_IMAGE" && docker push "$BACKEND_IMAGE_LATEST"
    - docker push "$FRONTEND_IMAGE" && docker push "$FRONTEND_IMAGE_LATEST"
  tags: [docker]
  only: [main, master]

deploy:production:
  stage: deploy
  image: alpine:3.19
  before_script:
    - apk add --no-cache openssh-client rsync
    - chmod 600 "$SSH_PRIVATE_KEY"
    - mkdir -p ~/.ssh
    - ssh-keyscan -H "$PROD_SERVER_IP" >> ~/.ssh/known_hosts
  script:
    - rsync -az -e "ssh -i $SSH_PRIVATE_KEY"
        deploy/docker-compose.prod.yml
        $PROD_SERVER_USER@$PROD_SERVER_IP:/opt/app/docker-compose.prod.yml
    - ssh -i "$SSH_PRIVATE_KEY" $PROD_SERVER_USER@$PROD_SERVER_IP "
        docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY &&
        export BACKEND_IMAGE=$BACKEND_IMAGE FRONTEND_IMAGE=$FRONTEND_IMAGE &&
        cd /opt/app &&
        docker-compose -f docker-compose.prod.yml pull &&
        docker-compose -f docker-compose.prod.yml up -d --remove-orphans &&
        docker image prune -f"
  environment:
    name: production
    url: https://wifiobd.shop
  tags: [docker]
  only: [main, master]
  when: manual
```

### `deploy/docker-compose.prod.yml`

```yaml
version: "3.9"
services:
  api:
    image: ${BACKEND_IMAGE}
    restart: unless-stopped
    env_file: /opt/app/.env.prod
    depends_on: [postgres, redis, minio]
    networks: [backend_net]

  celery_worker:
    image: ${BACKEND_IMAGE}
    command: celery -A app.tasks.celery_app worker -l info -c 4 -Q default,media,search
    restart: unless-stopped
    env_file: /opt/app/.env.prod
    depends_on: [redis, postgres, minio]
    networks: [backend_net]

  celery_beat:
    image: ${BACKEND_IMAGE}
    command: celery -A app.tasks.celery_app beat -l info
    restart: unless-stopped
    env_file: /opt/app/.env.prod
    depends_on: [redis]
    networks: [backend_net]

  frontend:
    image: ${FRONTEND_IMAGE}
    restart: unless-stopped
    networks: [frontend_net]

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    volumes: [pg_data:/var/lib/postgresql/data]
    env_file: /opt/app/.env.prod
    networks: [backend_net]

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --save 60 1 --loglevel warning
    volumes: [redis_data:/data]
    networks: [backend_net]

  meilisearch:
    image: getmeili/meilisearch:v1.7
    restart: unless-stopped
    volumes: [meili_data:/meili_data]
    env_file: /opt/app/.env.prod
    networks: [backend_net]

  minio:
    image: minio/minio:latest
    restart: unless-stopped
    command: server /data --console-address ":9001"
    volumes: [minio_data:/data]
    env_file: /opt/app/.env.prod
    networks: [backend_net]
    # Nginx проксирует /media/* → minio:9000

  nginx:
    image: nginx:stable-alpine
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on: [api, frontend, minio]
    networks: [frontend_net, backend_net]

volumes:
  pg_data: redis_data: meili_data: minio_data:

networks:
  backend_net:
  frontend_net:
```

**Nginx конфиг (`deploy/nginx/nginx.conf`) — ключевые блоки:**
```nginx
# Content Security Policy — разрешает YouTube/RuTube iframe
add_header Content-Security-Policy
  "default-src 'self'; frame-src youtube.com www.youtube.com rutube.ru; img-src 'self' data: https:; script-src 'self' 'unsafe-inline';"
  always;

# MinIO проксирование для медиафайлов
location /media/ {
    proxy_pass http://minio:9000/media/;
    proxy_cache_valid 200 7d;
    add_header Cache-Control "public, max-age=604800, immutable";
    # WebP: если браузер поддерживает — отдавать .webp версию
    add_header Vary Accept;
}

# Sitemap, robots, RSS — без кэша
location ~ ^/(sitemap\.xml|robots\.txt|rss\.xml)$ {
    proxy_pass http://frontend:3000;
    add_header Cache-Control "public, max-age=3600";
}
```

### Мониторинг (self-hosted)

- **Prometheus + Grafana**: `prometheus-fastapi-instrumentator`, `postgres_exporter`, `redis_exporter`
- **Loki + Promtail**: сбор JSON-логов контейнеров
- **Alerting**: Grafana → Telegram/Email при деградации
- **Uptime**: проверка `/health` эндпоинта каждые 30 сек

---

## 4. Ключевые паттерны (Best Practices)

- **Repository Pattern**: сервисный слой → только через репозиторий, не напрямую к БД
- **Dependency Injection**: сессии БД, текущий пользователь, настройки — через `Depends()`
- **Idempotency Keys**: для платёжных операций и создания заказов
- **Optimistic Locking**: при списании остатков через `version` поле в PostgreSQL
- **Event-driven**: изменение статуса заказа → Celery-таска → уведомления
- **Circuit Breaker**: для внешних API (СДЭК, YooMoney) — `tenacity` с exponential backoff
- **CI/CD секреты**: только GitLab CI/CD Variables и `.env.prod` на сервере
- **SEO-first**: каждая публичная страница обязана иметь `useSeoMeta` + Schema.org + canonical
- **Media-first**: каждое изображение обязано иметь `alt`, `width`, `height`; использовать WebP
- **Sanitize always**: любой HTML из пользовательского ввода → `bleach.clean()` перед сохранением

---

## 5. Чек-лист готовности к запуску

### Backend
- [ ] Все модули в `backend/app/api/v1/` реализованы: products, blog, media, orders, cart, payments, delivery, users, iot
- [ ] `requirements.txt` включает: `miniopy-async`, `Pillow`, `bleach`, `celery`, `meilisearch-python-sdk`
- [ ] Alembic-миграции для всех моделей (включая `BlogPost`, `BlogPostMedia`, `Redirect`)
- [ ] `bleach.clean()` применяется к `content_html` перед сохранением
- [ ] Celery-таски: `process_image` (WebP + thumbnail + размеры), `invalidate_blog_cache`, `increment_views`

### Frontend
- [ ] `useSeoMeta` на каждой публичной странице
- [ ] `useSchemaOrg` на `/blog/[slug]` (Article) и `/products/[slug]` (Product)
- [ ] `AppBreadcrumbs` с Schema.org BreadcrumbList на товарах и статьях
- [ ] `sitemap.xml` server route — возвращает все товары и статьи
- [ ] `robots.txt` server route — закрывает `/admin`, `/cart`, параметрические дубли
- [ ] `rss.xml` server route — последние 20 статей блога
- [ ] `rel=canonical` на всех страницах каталога с фильтрами
- [ ] `error.vue` с `robots: 'noindex'` и ссылкой на главную
- [ ] Все `<img>` имеют `alt`, `width`, `height`, `loading="lazy"` (кроме hero)
- [ ] TipTap установлен, редактор в `/admin/blog`
- [ ] `NUXT_PUBLIC_SITE_URL` в `.env` и `runtimeConfig`

### SEO-проверка перед запуском
- [ ] `curl https://wifiobd.shop/sitemap.xml` — возвращает XML с товарами и статьями
- [ ] `curl https://wifiobd.shop/robots.txt` — содержит Sitemap: и Disallow: /admin/
- [ ] Google Rich Results Test — страница товара и статьи проходят валидацию Schema.org
- [ ] Lighthouse Score: Performance ≥ 90, SEO = 100, Accessibility ≥ 90
- [ ] PageSpeed Insights: LCP < 2.5s, CLS < 0.1, FID < 100ms
