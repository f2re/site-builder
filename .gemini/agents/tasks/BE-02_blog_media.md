---
id: BE-02
status: TODO
agent: backend-agent
stage: 4 (Блог и медиа)
priority: HIGH
depends_on: []
blocks: [FE-03]
---

# BE-02 — Блог и медиа (локальное хранилище)

## Цель

Реализовать домен `blog`: модели, миграции, API. Медиа — **локальное хранилище** `/media/` через Nginx + Celery WebP-обработка. MinIO в проекте отсутствует.

## ⚠️ Перед началом

```bash
read_file backend/app/db/models/blog.py  # модель уже есть — проверь состав
list_directory backend/app/api/v1/blog/
list_directory backend/app/tasks/
```

## Задачи

### 1. Модели — проверить/дополнить (`backend/app/db/models/blog.py`)

Модель `blog.py` уже существует. Убедиться что присутствуют:
- `BlogPost`: `content_json (JSONB)`, `content_html`, `og_image_url` (локальный путь `/media/...`),
  `views (int=0)`, `reading_time_minutes (int=0)`, `status ('draft'|'published'|'archived')`
- `BlogPostMedia`: `url (str)` — **локальный путь**, `alt (NOT NULL)`, `width`, `height`, `mime_type`, `size_bytes`
- `Comment`: `author_email` — шифровать Fernet (152-ФЗ)
- `Author`: связь с `User`

Если полей не хватает — добавить и создать миграцию.

### 2. Медиа — локальное хранилище

**Эндпоинты `backend/app/api/v1/media/router.py`:**

```
POST /api/v1/media/upload
  Content-Type: multipart/form-data
  Body: file, context ("blog"|"product"), entity_id
  → сохраняет в /media/{context}/{YYYY}/{MM}/{uuid}.{ext}
  → запускает Celery tasks.process_image
  → возвращает { url, object_name, width, height }

DELETE /api/v1/media/{object_name}
  → удаляет файл + все варианты + запись BlogPostMedia/ProductImage
```

**Celery `backend/app/tasks/media.py` — проверить наличие, если нет создать:**

```python
@celery_app.task(name="tasks.process_image")
def process_image(file_path: str, entity_id: int, context: str):
    # 1. Pillow: определить width, height → сохранить в БД
    # 2. Конвертировать в WebP quality=85
    # 3. Создать варианты 480w, 800w, 1200w для srcset
    # 4. Обновить url в BlogPostMedia / ProductImage на WebP-версию
```

### 3. API блога (`backend/app/api/v1/blog/`)

**Публичные:**
```
GET  /api/v1/blog/posts          ?status=published&category=&tag=&after=&limit=12
GET  /api/v1/blog/posts/{slug}   + background_task: increment views
GET  /api/v1/blog/categories
GET  /api/v1/blog/tags
POST /api/v1/blog/posts/{id}/comments  (status=pending)
```

**Административные (require_role="admin"):**
```
POST   /api/v1/admin/blog/posts
PUT    /api/v1/admin/blog/posts/{id}
DELETE /api/v1/admin/blog/posts/{id}
PUT    /api/v1/admin/blog/comments/{id}/approve
DELETE /api/v1/admin/blog/comments/{id}
```

### 4. Кэширование и счётчик просмотров

```python
# Кэш списка:
Redis key: blog:list:{page}:{category}:{tag}, TTL 5 мин
# Инвалидация при публикации — tasks/blog.py:invalidate_blog_cache

# Счётчик просмотров:
Redis INCR blog:views:{post_id}
# Celery Beat: каждые 10 мин flush → UPDATE blog_post SET views = views + delta
```

### 5. bleach-санитизация

Перед каждым сохранением `content_html`:
```python
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS | {
    'h1','h2','h3','h4','p','br','ul','ol','li',
    'strong','em','blockquote','code','pre',
    'img','figure','figcaption','a','table','thead','tbody','tr','th','td',
    'iframe',  # только YouTube/RuTube — проверять src
}
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'width', 'height', 'loading'],
    'iframe': ['src', 'width', 'height', 'allowfullscreen'],
}
```

### 6. Поле reading_time_minutes

```python
def calc_reading_time(html: str) -> int:
    words = len(BeautifulSoup(html, 'html.parser').get_text().split())
    return max(1, words // 200)
```

Авто-вычислять при каждом save.

## Контракты

- `Comment.author_email` — шифровать Fernet, НИКОГДА не логировать
- `BlogPostMedia.alt` — NOT NULL
- `og_image_url` — локальный путь `/media/...`, не MinIO
- `reading_time_minutes` — пересчитывать при update

## Критерии готовности

- [ ] `alembic check` — чисто (если модели менялись)
- [ ] POST /api/v1/media/upload — файл сохраняется, Celery запускается
- [ ] GET /api/v1/blog/posts/{slug} — отдаёт `content_html` + `reading_time_minutes`
- [ ] POST comment — статус `pending`, email зашифрован в БД
- [ ] Admin CRUD — только role=admin
- [ ] bleach.clean() вызывается при каждом save

## Отчёт

`.gemini/agents/reports/backend/BE-02.md`
