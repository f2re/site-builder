---
id: BE-01
status: TODO
agent: backend-agent
stage: 2 (Каталог товаров)
priority: HIGH
depends_on: []
blocks: [BE-03, FE-02]
---

# BE-01 — Каталог товаров и инвентарь

## Цель
Реализовать полный домен `products` и `categories`: модели, миграции, API, инвентарь Redis.

## ⚠️ Перед началом

```bash
list_directory backend/app/api/v1/products/
list_directory backend/app/db/models/
# Если product.py уже есть — read_file, потом расширяй, не перезаписывай
```

## Задачи

### 1. Модели (`backend/app/db/models/`)

Проверить наличие `product.py`. Если нет — создать со следующими классами:

```python
# Category: id, name, slug (unique+indexed), parent_id (Adjacency List), is_active
# Product: id, name, slug (unique+indexed), description_html (bleach-sanitized),
#   attributes (JSONB), category_id, price (Decimal), is_active,
#   meta_title (max 60), meta_description (max 160), og_image_url,
#   created_at, updated_at
# ProductImage: id, product_id, url, alt (NOT NULL), is_cover, sort_order, width, height
# ProductVariant: id, product_id, sku (unique), name, price (Decimal), stock (int ≥ 0)
# StockMovement: id, variant_id, delta (int), reason ('sale'|'return'|'correction'), created_at
```

### 2. Миграция Alembic

```bash
alembic revision --autogenerate -m "products: add category, product, variant, stock_movement"
# Проверить файл вручную перед upgrade
alembic upgrade head
```

### 3. Repository (`backend/app/api/v1/products/repository.py`)

```python
class ProductRepository:
    async def get_by_slug(self, slug: str) -> Product | None
    async def list_cursor(
        self, after: int | None, limit: int,
        category_id: int | None, is_active: bool = True
    ) -> tuple[list[Product], int | None]  # (items, next_cursor)
    async def get_stock(self, variant_id: int) -> int  # из Redis, fallback БД

class CategoryRepository:
    async def get_tree(self) -> list[Category]  # кэш Redis TTL 10 мин
    async def get_by_slug(self, slug: str) -> Category | None
```

### 4. Service (`backend/app/api/v1/products/service.py`)

- `get_product(slug)` — enriches с images + variants + stock из Redis
- `list_products(...)` — cursor pagination
- `get_categories()` — дерево, Redis cache `categories:tree` TTL 10 мин
- `reserve_stock(variant_id, qty)` — **Lua-скрипт** Redis, TTL 30 мин
- `release_stock(variant_id, qty)` — Lua-скрипт
- `confirm_stock(variant_id, qty)` — финальное списание, StockMovement запись

### 5. Router (`backend/app/api/v1/products/router.py`)

```
GET  /api/v1/products              ?after=&limit=24&category=
GET  /api/v1/products/{slug}
GET  /api/v1/categories
GET  /api/v1/products/search?q=   (проксирует Meilisearch)
```

- Все эндпоинты публичные (нет JWT)
- Ответы кэшировать: `Cache-Control: public, max-age=60`

### 6. Schemas (`backend/app/api/v1/products/schemas.py`)

```python
class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; slug: str; name: str; price: Decimal
    description_html: str; attributes: dict
    images: list[ProductImageResponse]
    variants: list[ProductVariantResponse]
    meta_title: str | None; meta_description: str | None

class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    next_cursor: int | None
    total: int
```

### 7. Meilisearch-индексация (Celery)

Файл `backend/app/tasks/search_index.py` — проверить наличие, создать если нет:

```python
@celery_app.task(name="tasks.index_product")
def index_product(product_id: int): ...

@celery_app.task(name="tasks.delete_product_from_index")
def delete_product_from_index(product_id: int): ...
```

Триггер в service при create/update/delete продукта.

## Контракты (обязательно)

- `description_html` — **bleach.clean()** перед сохранением
- `slug` — `python-slugify`, уникальность на уровне БД
- Нет `Any` в type hints
- `ProductImage.alt` — NOT NULL (SEO/a11y)
- `ProductImage.width/height` — заполнить при загрузке (предотвращает CLS)

## Критерии готовности

- [ ] `alembic check` — чисто
- [ ] `mypy backend/app/api/v1/products/ --strict` — 0 ошибок
- [ ] `pytest tests/unit/products/ -v` — все зелёные
- [ ] GET /api/v1/products — отдаёт список с cursor
- [ ] GET /api/v1/products/{slug} — карточка с images + variants + stock
- [ ] reserve/confirm/release через Lua без race condition

## Отчёт

После завершения: `.gemini/agents/reports/backend/BE-01.md`
