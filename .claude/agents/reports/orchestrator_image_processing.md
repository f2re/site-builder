# Отчёт оркестратора: Система обработки изображений

**Дата:** 2026-03-10
**Статус:** План создан, задачи делегированы агентам

---

## Цель
Реализовать полноценную систему обработки изображений с множественными размерами, внутренней нумерацией и оптимизацией при миграции.

---

## Архитектурные решения

### 1. Множественные размеры
- **thumb** (150x150 crop) — иконки, карточки в списке
- **small** (320px) — мобильные списки
- **medium** (480px) — карточки товаров, превью блога
- **large** (1024px) — страница товара, статья блога
- **original** (max 1920px) — полноэкранный просмотр

### 2. Структура хранения
```
media/
  product/{product_id}/
    001.webp          # original
    001_large.webp
    001_medium.webp
    001_small.webp
    001_thumb.webp
  blog/{post_id}/
    001.webp
    001_large.webp
    ...
```

### 3. Модель данных
```python
class ProductImage:
    sequence: int  # 1, 2, 3...
    base_path: str  # "product/{id}/{seq}"
    formats: JSONB  # {"thumb": "001_thumb.webp", ...}
    url: str  # deprecated
```

### 4. Обработка
- Celery task: `process_image_variants`
- Умный resize: не апскейлить изображения меньше целевого размера
- Crop для thumb: центрированный квадрат 150x150
- WebP quality=85

---

## Делегированные задачи

### P0 — Базовая функциональность

#### 1. p3_backend_image_model_extension
**Агент:** backend-agent
**Статус:** pending
**Описание:** Расширить модели ProductImage и BlogPostMedia полями sequence, base_path, formats
**Файлы:**
- backend/app/db/models/product.py
- backend/app/db/models/blog.py
- backend/app/api/v1/products/schemas.py
- backend/app/db/migrations/versions/YYYYMMDD_add_image_variants_support.py

#### 2. p3_backend_image_variants_processing
**Агент:** backend-agent
**Статус:** pending (зависит от задачи 1)
**Описание:** Реализовать Celery task для генерации 5 размеров изображений
**Файлы:**
- backend/app/tasks/media.py

**Особенности:**
- Генерация 5 размеров: original (1920), large (1024), medium (480), small (320), thumb (150x150 crop)
- Умный resize: не апскейлить изображения меньше целевого размера
- Thumb: центрированный квадрат 150x150

#### 3. p3_backend_image_upload_service
**Агент:** backend-agent
**Статус:** pending (зависит от задач 1, 2)
**Описание:** Обновить MediaService и ProductService для работы с множественными размерами
**Файлы:**
- backend/app/api/v1/media/service.py
- backend/app/api/v1/products/service.py

**Особенности:**
- Генерация sequence: SELECT MAX(sequence) + 1
- Atomic update: загрузка новых → удаление старых
- Удаление всех вариантов при delete

---

### P1 — Миграция и Frontend

#### 4. p3_backend_migration_images
**Агент:** backend-agent
**Статус:** pending (зависит от задач 1, 2)
**Описание:** Добавить обработку изображений в миграцию OpenCart с прогресс-трекингом
**Файлы:**
- backend/app/api/v1/admin/migration_service.py
- backend/app/tasks/media.py

**Особенности:**
- Batch processing: 50 изображений за раз
- Redis tracking: HSET migration:images:{job_id}
- Retry logic: 3 попытки с exponential backoff
- Timeout: 30s на скачивание

#### 5. p3_frontend_image_component
**Агент:** frontend-agent
**Статус:** pending (зависит от задачи 1)
**Описание:** Создать компонент ImageWithFallback для автоматического выбора размера
**Файлы:**
- frontend/components/ImageWithFallback.vue
- frontend/composables/useImageLoader.ts

**Особенности:**
- Автоматический выбор размера по контексту
- Fallback: medium → small → thumb при ошибке
- Lazy loading через IntersectionObserver
- Placeholder: blur-up эффект

---

### P2 — Тестирование

#### 6. p3_testing_image_processing
**Агент:** testing-agent
**Статус:** pending (зависит от задач 1, 2, 3)
**Описание:** Unit и integration тесты для системы обработки изображений
**Файлы:**
- tests/unit/tasks/test_media.py
- tests/unit/api/test_image_service.py
- tests/integration/test_image_upload.py
- tests/integration/test_image_migration.py

**Coverage target:** > 80%

---

## Порядок выполнения

1. **Фаза 1 (P0):** backend-agent выполняет задачи 1 → 2 → 3 последовательно
2. **Фаза 2 (P1):** параллельно backend-agent (задача 4) + frontend-agent (задача 5)
3. **Фаза 3 (P2):** testing-agent (задача 6) после завершения фазы 1

---

## Риски и митигация

### Риск 1: Большой объём изображений при миграции
**Митигация:** Batch processing (50 за раз), Redis tracking, retry logic

### Риск 2: Долгая обработка блокирует миграцию
**Митигация:** Async Celery tasks, прогресс-бар в UI, возможность паузы

### Риск 3: Обратная совместимость со старыми записями
**Митигация:** Поле url помечено deprecated, но оставлено; helper-методы поддерживают оба формата

---

## Следующие шаги

1. Запустить backend-agent с задачей p3_backend_image_model_extension
2. После завершения — запустить p3_backend_image_variants_processing
3. После завершения — запустить p3_backend_image_upload_service
4. Параллельно запустить p3_backend_migration_images и p3_frontend_image_component
5. В конце — запустить p3_testing_image_processing

---

## Команды для запуска

```bash
# Фаза 1
/agents:run backend-agent p3_backend_image_model_extension
# После завершения:
/agents:run backend-agent p3_backend_image_variants_processing
# После завершения:
/agents:run backend-agent p3_backend_image_upload_service

# Фаза 2 (параллельно)
/agents:run backend-agent p3_backend_migration_images
/agents:run frontend-agent p3_frontend_image_component

# Фаза 3
/agents:run testing-agent p3_testing_image_processing
```

---

## Метрики успеха

- ✅ Все изображения имеют 5 размеров
- ✅ Имена файлов читаемые (001.webp, 002.webp)
- ✅ Миграция обрабатывает изображения батчами с прогресс-баром
- ✅ Frontend автоматически выбирает оптимальный размер
- ✅ Coverage тестов > 80%
- ✅ Обратная совместимость со старыми записями

---

**Оркестратор:** Все задачи созданы и готовы к выполнению. Начинаем с задачи p3_backend_image_model_extension.
