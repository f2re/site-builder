# ТЗ: Миграция данных из OpenCart в site-builder

## Что уже есть (анализ репозиториев)

**В `wifiobd-bot` — готовый рабочий код:**

- [`opencart_models.py`](opencart_models.py) — SQLAlchemy-модели всех таблиц OpenCart: `OCCustomer`, `OCProduct`, `OCProductDescription`, `OCProductToCategory`, `OCCategory`, `OCCategoryDescription`, `OCOrder`, `OCOrderProduct`
- [`opencart.py`](opencart.py) — `OpenCartService` с рабочими методами чтения из БД: `get_root_categories`, `get_subcategories`, `get_products_by_category(limit, offset)`, `get_products_batch`, `search_products` — всё протестировано

**В `site-builder/backend` — целевая инфраструктура:**

- Уже есть admin router с CRUD для Product, Order, Blog, User
- Модель `User` использует **Fernet-шифрование** email и blind index — прямой SQL INSERT не работает
- `security.py` экспортирует `encrypt_data()`, `get_blind_index()`, `get_password_hash()`

***

## Архитектура системы миграции

```
OpenCart MySQL (read-only)
    ↓
opencart_models.py (скопировать из wifiobd-bot)
    ↓
MigrationService (новый сервис в site-builder)
    ↓
Celery Task (асинхронное выполнение)
    ↓
migration_jobs table (состояние: прогресс, паузы, ошибки)
    ↓
Target: users / products / categories / orders / media
```


***

## Фаза 0 — Модель состояния миграции

### Новая таблица `MigrationJob`

```python
# backend/app/db/models/migration.py
import uuid, enum
from sqlalchemy import String, Integer, DateTime, Text, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class MigrationStatus(str, enum.Enum):
    PENDING  = "pending"
    RUNNING  = "running"
    PAUSED   = "paused"
    DONE     = "done"
    FAILED   = "failed"

class MigrationEntity(str, enum.Enum):
    USERS      = "users"
    CATEGORIES = "categories"
    PRODUCTS   = "products"
    IMAGES     = "images"
    ORDERS     = "orders"
    BLOG       = "blog"

class MigrationJob(Base):
    __tablename__ = "migration_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity:     Mapped[str] = mapped_column(String(50))   # MigrationEntity
    status:     Mapped[str] = mapped_column(String(20), default="pending")
    total:      Mapped[int] = mapped_column(Integer, default=0)
    processed:  Mapped[int] = mapped_column(Integer, default=0)
    skipped:    Mapped[int] = mapped_column(Integer, default=0)  # уже есть
    failed:     Mapped[int] = mapped_column(Integer, default=0)
    last_oc_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # курсор
    errors:     Mapped[list | None] = mapped_column(JSON, nullable=True)   # [{id, msg}]
    started_at: Mapped[datetime | None] = ...
    updated_at: Mapped[datetime | None] = ...
```

> **`last_oc_id`** — курсор для возобновления с места остановки. При паузе/сбое — следующий запуск начинает с `WHERE id > last_oc_id`.

***

## Фаза 1 — Подключение к OpenCart DB

### Добавить в `.env.prod`

```ini
OC_DB_HOST=<OC_DB_HOST>
OC_DB_PORT=3306
OC_DB_NAME=<OC_DB_NAME>
OC_DB_USER=<OC_DB_USER>
OC_DB_PASSWORD=<OC_DB_PASSWORD>
OC_SITE_URL=<OC_SITE_URL>          # для скачивания картинок
OC_LANGUAGE_ID=1                   # ID языка в opencart (обычно 1=RU)
```


### Скопировать из wifiobd-bot без изменений:

- `wifiobd-bot/app/database/opencart_models.py` → `backend/app/db/opencart_models.py`

Готовые модели содержат все нужные таблицы и проверены в production .

### Конфигурация соединения

```python
# backend/app/db/opencart_session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

oc_engine = create_async_engine(
    f"mysql+aiomysql://{settings.OC_DB_USER}:{settings.OC_DB_PASSWORD}"
    f"@{settings.OC_DB_HOST}:{settings.OC_DB_PORT}/{settings.OC_DB_NAME}",
    pool_pre_ping=True
)
OCSession = sessionmaker(oc_engine, class_=AsyncSession, expire_on_commit=False)
```


***

## Фаза 2 — MigrationService

Новый файл `backend/app/services/migration_service.py`. Переиспользует методы из `opencart.py` как есть.

### 2.1 Миграция пользователей (OCCustomer → User)

**Источник (opencart):** `oc_customer` — `customer_id`, `firstname`, `lastname`, `email`, `telephone`, `date_added`, `status`

**Маппинг:**

```python
# Взять из opencart.py логику чтения, адаптировать:
async def migrate_users(self, job: MigrationJob, batch_size=50):
    async with OCSession() as oc:
        query = (
            select(OCCustomer)
            .where(OCCustomer.customer_id > (job.last_oc_id or 0))
            .order_by(OCCustomer.customer_id)
            .limit(batch_size)
        )
        for oc_user in await oc.execute(query):
            email_hash = get_blind_index(oc_user.email)
            # Проверка: уже мигрирован?
            exists = await self.sb_session.execute(
                select(User).where(User.email_hash == email_hash)
            )
            if exists.scalar_one_or_none():
                job.skipped += 1
                continue

            user = User(
                email=encrypt_data(oc_user.email),
                email_hash=email_hash,
                full_name=encrypt_data(f"{oc_user.firstname} {oc_user.lastname}".strip()),
                hashed_password=get_password_hash(secrets.token_hex(16)),  # временный
                role="customer",
                is_active=oc_user.status,
                auth_provider="opencart",      # маркер источника
                created_at=oc_user.date_added,
            )
            self.sb_session.add(user)
            job.last_oc_id = oc_user.customer_id
            job.processed += 1
```

> ⚠️ `auth_provider="opencart"` — маркер для отличия мигрированных пользователей. При первом входе они будут получать ссылку на сброс пароля.

### 2.2 Миграция категорий и товаров (OCCategory → Category, OCProduct → Product)

**Готовые методы из `opencart.py` — использовать напрямую:**

- `get_root_categories()` → создать корневые категории
- `get_subcategories(parent_id)` → рекурсивное построение дерева
- `get_products_by_category(category_id, limit, offset)` → batch-загрузка с курсором

**Маппинг товара:**

```python
# OCProduct + OCProductDescription → Product + ProductVariant
Product(
    name=description.name,
    slug=slugify(description.name),
    description=description.description,    # HTML из OpenCart
    meta_title=description.meta_title,
    meta_description=description.meta_description,
    oc_product_id=product.product_id,       # поле для idempotency
)
ProductVariant(
    sku=product.model or product.sku,
    price=float(product.price),
    stock=product.quantity,
    is_available=product.status and product.quantity > 0,
)
```

> Добавить поле `oc_product_id: int | None` в модель `Product` для idempotency-проверки — `WHERE oc_product_id = ?`.

### 2.3 Миграция изображений

**Источник:** `product.image` → относительный путь вида `catalog/xxx.jpg`

```python
async def download_image(self, oc_image_path: str) -> str | None:
    url = f"{settings.OC_SITE_URL}/image/{oc_image_path}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as resp:
            if resp.status != 200:
                return None
            content = await resp.read()
            # Сохранить в /app/media/products/
            filename = Path(oc_image_path).name
            dest = settings.MEDIA_ROOT / "products" / filename
            dest.write_bytes(content)
            return f"/media/products/{filename}"
```

> Запускать в отдельной Celery-таске с приоритетом ниже основных данных.

### 2.4 Миграция заказов (OCOrder → Order)

**Зависимость:** сначала должны быть мигрированы пользователи и товары.

```python
# Маппинг: найти user по email_hash, найти product по oc_product_id
async def migrate_orders(self, job, batch_size=50):
    for oc_order in oc_orders_batch:
        # Найти мигрированного пользователя
        email_hash = get_blind_index(oc_order.email)
        user = await self.find_user_by_hash(email_hash)

        order = Order(
            user_id=user.id if user else None,    # guest если не найден
            total_amount=float(oc_order.total),
            status=self._map_status(oc_order.order_status_id),
            comment=oc_order.comment,
            shipping_address={
                "city":    oc_order.shipping_city,
                "address": oc_order.shipping_address_1,
                "country": oc_order.shipping_country,
            },
            created_at=oc_order.date_added,
            oc_order_id=oc_order.order_id,        # idempotency
        )
        # OrderItem из OCOrderProduct
        for item in oc_order_products:
            product_variant = await self.find_variant_by_oc_id(item.product_id)
            order.items.append(OrderItem(
                product_variant_id=product_variant.id if product_variant else None,
                product_name_snapshot=item.name,  # сохранить как есть
                quantity=item.quantity,
                unit_price=float(item.price),
            ))
```

**Маппинг статусов OpenCart:**


| `order_status_id` | OpenCart | site-builder |
| :-- | :-- | :-- |
| 1 | Pending | `PENDING` |
| 2 | Processing | `PROCESSING` |
| 5 | Complete | `DELIVERED` |
| 7 | Canceled | `CANCELLED` |
| 14 | Canceled Reversal | `CANCELLED` |
| 15 | Shipped | `SHIPPED` |

### 2.5 Миграция блога

Блога в OpenCart нет — источником будет отдельная CMS (WordPress или другая). Этот модуль — **отдельная задача фазы 3**. Структура та же: `MigrationJob(entity="blog")`, курсор по `wp_post_id`.

***

## Фаза 3 — Celery-таски

```python
# backend/app/tasks/migration_tasks.py
from celery import shared_task
from app.services.migration_service import MigrationService

@shared_task(bind=True, max_retries=3)
def run_migration_task(self, job_id: str, entity: str):
    """Одна таска = один батч одного entity"""
    service = MigrationService()
    job = service.get_job(job_id)

    if job.status == "paused":
        return {"status": "paused"}

    try:
        service.run_batch(job, entity)
        if not service.is_done(job):
            # Рекурсивно запланировать следующий батч
            run_migration_task.apply_async(
                args=[job_id, entity],
                countdown=1   # 1 секунда между батчами
            )
    except Exception as exc:
        job.status = "failed"
        raise self.retry(exc=exc, countdown=5)
```


***

## Фаза 4 — Admin API эндпоинты

Добавить в `backend/app/api/v1/admin/router.py` :

```python
# POST  /api/v1/admin/migration/start
# GET   /api/v1/admin/migration/status
# POST  /api/v1/admin/migration/{job_id}/pause
# POST  /api/v1/admin/migration/{job_id}/resume
# GET   /api/v1/admin/migration/{job_id}/log
```

**Ответ `/status`:**

```json
{
  "jobs": [
    {
      "entity": "users",
      "status": "done",
      "total": 3847,
      "processed": 3847,
      "skipped": 12,
      "failed": 0
    },
    {
      "entity": "products",
      "status": "running",
      "total": 1200,
      "processed": 650,
      "skipped": 0,
      "failed": 2,
      "last_oc_id": 784,
      "eta_seconds": 110
    }
  ]
}
```


***

## Порядок выполнения

1. **Фаза 0** — Alembic-миграция: добавить `migration_jobs`, `oc_product_id` в `products`, `oc_order_id` в `orders`
2. **Фаза 1** — Скопировать `opencart_models.py`, настроить `OCSession`, добавить env-переменные
3. **Фаза 2** — `MigrationService`: users → categories → products → images (параллельно) → orders
4. **Фаза 3** — Celery-таски с `countdown` между батчами
5. **Фаза 4** — Admin API + UI-кнопки в Nuxt-фронтенде

## Ключевые акценты

- **Idempotency везде:** проверка `email_hash` / `oc_product_id` / `oc_order_id` перед каждой вставкой — повторный запуск не создаёт дубликатов
- **Курсор `last_oc_id`:** миграция прерывается и возобновляется с последнего успешного ID
- **Изображения отдельно:** не блокируют миграцию данных, запускаются параллельной Celery-таской
- **Email-шифрование:** весь код маппинга пользователей обязан использовать `encrypt_data()` и `get_blind_index()` из `security.py`  — иначе поиск по email сломается
- **`auth_provider="opencart"`:** маркирует мигрированных пользователей для последующего flow сброса пароля

s