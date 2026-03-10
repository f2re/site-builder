# План реализации системы обработки изображений

## Текущее состояние
- ✅ Базовая обработка через Celery task `process_image`
- ✅ Конвертация в WebP (quality=85)
- ✅ Генерация thumbnail (480px max)
- ✅ Модели: ProductImage, BlogPostMedia
- ✅ Local storage через `storage_client`
- ❌ Нет множественных размеров (только original + thumb)
- ❌ Нет оптимизации при миграции
- ❌ Нет внутренней нумерации (используются UUID в именах файлов)
- ❌ Нет системы версионирования/обновления изображений

## Требования
1. **Множественные размеры** для разных контекстов:
   - `thumb` (150x150) — иконки, карточки товаров в списке
   - `small` (480x480) — карточки товаров, превью блога
   - `medium` (1024x1024) — страница товара, статья блога
   - `large` (1920x1920) — полноэкранный просмотр, hero-изображения
   - `original` — исходник (опционально хранить)

2. **Внутренняя нумерация** вместо UUID в именах:
   - Формат: `{entity}/{id}/{seq}.webp`
   - Пример: `product/a1b2c3d4/001.webp`, `product/a1b2c3d4/001_thumb.webp`
   - Избегаем нечитаемых символов в FS

3. **Оптимизация при миграции**:
   - Скачивание изображений из OpenCart
   - Обработка батчами через Celery
   - Прогресс-бар в admin UI

4. **Версионирование**:
   - При замене изображения — удалить старые варианты
   - Atomic операции (сначала загрузка новых, потом удаление старых)

5. **API для управления**:
   - Upload: POST /api/v1/products/{id}/images
   - Delete: DELETE /api/v1/products/{id}/images/{image_id}
   - Update: PUT /api/v1/products/{id}/images/{image_id}
   - Set cover: PUT /api/v1/products/{id}/images/{image_id}/cover

## Архитектурные решения

### 1. Структура хранения
```
media/
  product/
    {product_id}/
      001.webp          # original (1920px max)
      001_large.webp    # 1024px
      001_medium.webp   # 480px
      001_thumb.webp    # 150px
      002.webp
      002_large.webp
      ...
  blog/
    {post_id}/
      001.webp
      001_large.webp
      ...
  content/              # для контента в TipTap (inline images)
    {hash}_{filename}.webp
    {hash}_{filename}_thumb.webp
```

### 2. Модель ProductImage (изменения)
```python
class ProductImage(Base):
    id: UUID
    product_id: UUID
    sequence: int  # NEW: 1, 2, 3... для формирования имени файла
    base_path: str  # NEW: "product/{product_id}/{seq}" без расширения
    url: str  # DEPRECATED: оставить для обратной совместимости
    alt: str
    is_cover: bool
    sort_order: int
    width: int  # original width
    height: int  # original height
    formats: JSONB  # NEW: {"original": "001.webp", "large": "001_large.webp", ...}
```

### 3. Celery task: process_image_variants
```python
@celery_app.task
def process_image_variants(
    source_path: str,
    entity_type: Literal["product", "blog"],
    entity_id: UUID,
    sequence: int,
    image_id: UUID
):
    """
    1. Read source image
    2. Generate 4 variants: original (1920), large (1024), medium (480), thumb (150)
    3. Save all variants to storage
    4. Update DB record with formats JSON
    """
```

### 4. Migration: обработка изображений OpenCart
```python
async def migrate_product_images(job: MigrationJob):
    """
    1. Fetch batch of OCProductImage
    2. For each image:
       - Download from OpenCart URL
       - Dispatch Celery task process_image_variants
       - Store image_id in Redis queue for tracking
    3. Wait for Celery tasks completion (poll Redis)
    4. Update job progress
    """
```

## Задачи для агентов

### Задача 1: backend-agent — Расширить модель ProductImage и BlogPostMedia
- Добавить поля: `sequence`, `base_path`, `formats` (JSONB)
- Создать Alembic миграцию
- Обновить схемы Pydantic
- Добавить helper-методы: `get_url(size: str)`, `get_all_urls()`

### Задача 2: backend-agent — Реализовать process_image_variants
- Рефакторинг `app/tasks/media.py`
- Генерация 4 размеров: original (1920), large (1024), medium (480), thumb (150)
- Сохранение в структуру `{entity}/{id}/{seq}_{size}.webp`
- Обновление `formats` JSON в БД

### Задача 3: backend-agent — Обновить MediaService и ProductService
- Upload: генерировать sequence, вызывать process_image_variants
- Delete: удалять все варианты из storage
- Update: atomic замена (загрузка новых → удаление старых)

### Задача 4: backend-agent — Добавить обработку изображений в миграцию
- В `migration_service.py`: метод `migrate_product_images_batch`
- Скачивание из OpenCart URL
- Dispatch Celery tasks
- Tracking прогресса через Redis
- Обновление `extra_data` с прогрессом

### Задача 5: frontend-agent — Компонент ImageWithFallback
- Автоматический выбор размера по контексту
- Fallback на меньший размер при ошибке загрузки
- Lazy loading + placeholder

### Задача 6: testing-agent — Тесты обработки изображений
- Unit: генерация вариантов, sequence logic
- Integration: upload → process → verify all sizes
- Migration: mock OpenCart URLs, verify download + process

## Приоритеты
1. **P0**: Задачи 1, 2, 3 — базовая функциональность
2. **P1**: Задача 4 — миграция изображений
3. **P2**: Задачи 5, 6 — frontend + тесты
