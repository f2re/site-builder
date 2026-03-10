# Task Report: p3_backend_image_variants_processing

## Status: DONE

## Completed:
- Создан новый Celery task `process_image_variants` для генерации 5 размеров изображений
- Реализованы helper-функции `_smart_resize()` (умный resize без апскейлинга) и `_generate_thumb_crop()` (центрированный квадрат 150x150)
- Генерируются 5 размеров: original (max 1920px), large (1024px), medium (480px), small (320px), thumb (150x150 crop)
- Все варианты сохраняются в формате WebP (quality=85)
- Имена файлов: {seq}.webp, {seq}_large.webp, {seq}_medium.webp, {seq}_small.webp, {seq}_thumb.webp
- Обновление ProductImage.formats и BlogPostMedia.formats с путями ко всем вариантам
- Старый task `process_image` помечен как DEPRECATED в комментариях
- Добавлено детальное логирование размеров каждого варианта

## Artifacts:
- /Users/meteo/Documents/WWW/site-builder/backend/app/tasks/media.py

## Implementation Details:

### New Task Signature:
```python
@celery_app.task(name="tasks.process_image_variants", bind=True, max_retries=3)
def process_image_variants(
    self,
    source_path: str,
    entity_type: Literal["product", "blog"],
    entity_id: str,
    sequence: int,
    image_id: str,
)
```

### Smart Resize Logic:
- `_smart_resize()`: не апскейлит изображения меньше целевого размера
- Если исходник 800px — не создаётся large (1024px), используется исходник
- Сохраняет aspect ratio при resize

### Thumb Generation:
- `_generate_thumb_crop()`: использует `ImageOps.fit()` для центрированного crop
- Размер: 150x150 квадрат
- Centering: (0.5, 0.5) — центр изображения

### Storage Pattern:
- Базовый путь: `media/{entity_type}/{entity_id}/`
- Имена файлов: `001.webp`, `001_large.webp`, `001_medium.webp`, `001_small.webp`, `001_thumb.webp`
- Sequence форматируется как 3-значное число с ведущими нулями

### Database Update:
- Обновляются поля: `base_path`, `formats`, `width`, `height`
- Для BlogPostMedia дополнительно обновляется `mime_type = "image/webp"`
- `formats` содержит словарь: `{"original": "path", "large": "path", ...}`

### Logging:
- Логируется каждый сгенерированный вариант с размерами и размером файла
- Флаг `was_resized` показывает, был ли применён resize

## Contracts Verified:
- Pydantic schemas: N/A (task only)
- DI via Depends: N/A (Celery task)
- No Any: ✅ (используется cast для PIL Image)
- ruff: ✅ (All checks passed)
- mypy: ✅ (Success: no issues found)
- Celery async pattern: ✅ (asyncio.run() используется корректно)

## Backward Compatibility:
- Старый task `process_image` сохранён и помечен как DEPRECATED
- Существующий код продолжит работать без изменений
- Новый task использует новые поля `formats`, `base_path`, `sequence` из p3_backend_image_model_extension

## Next:
- media-agent: интегрировать `process_image_variants` в upload endpoints
- frontend-agent: обновить компоненты для использования новых размеров через `get_url(size)`
- Опционально: добавить настройку `KEEP_ORIGINAL` в config.py для удаления исходника после обработки

## Blockers:
- none

## Notes:
- Task готов к использованию, но требует интеграции в upload flow
- Исходный файл не удаляется (настройка KEEP_ORIGINAL не реализована)
- Все размеры генерируются атомарно в одной транзакции
- При ошибке используется exponential backoff: 60s, 120s, 240s
