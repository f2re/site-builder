# Task Report: p3_backend_image_model_extension

## Status: DONE

## Completed:
- Добавлены поля в ProductImage: sequence (Integer, NOT NULL), base_path (String(500)), formats (JSONB, default={})
- Добавлены поля в BlogPostMedia: sequence (Integer, NOT NULL), base_path (String(500)), formats (JSONB, default={})
- Реализованы helper-методы get_url(size: str) -> str и get_all_urls() -> dict в обеих моделях
- Создана Alembic миграция 20260311_0000_add_image_variants_support.py с заполнением дефолтных значений для существующих записей
- Обновлена Pydantic схема ProductImageRead с новыми полями
- Создана новая Pydantic схема BlogPostMediaRead с полной поддержкой новых полей
- Поле url помечено как DEPRECATED в комментариях моделей

## Artifacts:
- /Users/meteo/Documents/WWW/site-builder/backend/app/db/models/product.py
- /Users/meteo/Documents/WWW/site-builder/backend/app/db/models/blog.py
- /Users/meteo/Documents/WWW/site-builder/backend/app/api/v1/products/schemas.py
- /Users/meteo/Documents/WWW/site-builder/backend/app/api/v1/blog/schemas.py
- /Users/meteo/Documents/WWW/site-builder/backend/app/db/migrations/versions/20260311_0000_add_image_variants_support.py

## Migrations:
- 20260311_0000_add_image_variants_support: добавлены поля sequence, base_path, formats в product_images и blog_post_media с заполнением дефолтных значений для существующих записей

## Contracts Verified:
- Pydantic schemas: ✅
- DI via Depends: N/A (модели и схемы)
- No Any: ✅
- ruff: ✅ (All checks passed)
- mypy: ✅ (Success: no issues found)
- Migration syntax: ✅
- Helper methods: ✅ (tested get_url() and get_all_urls())

## Implementation Details:

### Model Changes:
- ProductImage.sequence: порядковый номер для формирования имени файла (001, 002, ...)
- ProductImage.base_path: базовый путь без расширения (product/{product_id}/{seq})
- ProductImage.formats: JSONB словарь с путями к разным размерам {"thumb": "...", "small": "...", "medium": "...", "large": "...", "original": "..."}
- Аналогичные поля добавлены в BlogPostMedia

### Helper Methods:
- get_url(size: str) -> str: возвращает URL для указанного размера, fallback на url если formats пустой
- get_all_urls() -> dict[str, str]: возвращает все доступные размеры изображений

### Migration Strategy:
- Поля добавлены как nullable=True
- Заполнены дефолтные значения: sequence = sort_order + 1, base_path извлечён из url, formats = {}
- После заполнения данных sequence сделан NOT NULL

### Backward Compatibility:
- Поле url сохранено и помечено как DEPRECATED в комментариях
- Helper-методы используют url как fallback если formats пустой
- Существующий код продолжит работать без изменений

## Next:
- frontend-agent: обновить компоненты для использования новых полей formats и метода get_url()
- media-agent: реализовать генерацию множественных размеров изображений при загрузке
- API contracts: обновить документацию с новыми полями ProductImageRead и BlogPostMediaRead

## Blockers:
- none

## Notes:
- База данных не была запущена во время разработки, миграция создана вручную
- Миграция протестирована на синтаксис и импорты
- Для применения миграции требуется запустить: `alembic upgrade head`
- Структура хранения: media/{entity}/{entity_id}/{seq}_{size}.webp
- Поддерживаемые размеры: thumb (150px), small (480px), medium (1024px), large (1920px), original
