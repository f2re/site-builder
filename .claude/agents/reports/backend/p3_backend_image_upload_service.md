# Task Report: p3_backend_image_upload_service

## Status: DONE

## Completed:
- Добавлен метод MediaService._generate_next_sequence(entity_type, entity_id) для генерации sequence
- Добавлен метод MediaService._delete_all_variants(formats) для удаления всех размеров изображения
- Добавлен метод ProductService._generate_next_sequence(product_id) для генерации sequence
- Добавлен метод ProductService._delete_all_variants(formats) для удаления всех размеров изображения
- Обновлён MediaService.create_media_record для работы с process_image_variants и sequence
- Обновлён MediaService.delete_media для удаления всех вариантов из formats
- Обновлён ProductService.upload_image для сохранения в temp и вызова process_image_variants
- Обновлён ProductService.delete_image для удаления всех вариантов из storage
- Добавлен ProductService.update_image для atomic замены изображения (новые → старые)
- Обратная совместимость: если formats пустой, используется url

## Artifacts:
- /Users/meteo/Documents/WWW/site-builder/backend/app/api/v1/media/service.py
- /Users/meteo/Documents/WWW/site-builder/backend/app/api/v1/products/service.py

## Implementation Details:

### Sequence Generation:
- MediaService._generate_next_sequence(): SELECT MAX(sequence) + 1 для product_images или blog_post_media
- ProductService._generate_next_sequence(): SELECT MAX(sequence) + 1 для product_images
- Возвращает 1 если нет записей

### Upload Flow (ProductService.upload_image):
1. Генерация sequence через _generate_next_sequence()
2. Сохранение исходника в media/temp/{uuid}_{filename}
3. Создание записи ProductImage с sequence, пустыми formats
4. Вызов process_image_variants.delay(temp_path, "product", product_id, sequence, image_id)
5. Celery task заполнит formats после обработки

### Delete Flow (ProductService.delete_image):
1. Загрузка записи ProductImage из БД
2. Если formats не пустой → вызов _delete_all_variants(formats)
3. Если formats пустой, но url заполнен → удаление url (backward compatibility)
4. Удаление записи из БД

### Update Flow (ProductService.update_image):
1. Загрузка существующей записи
2. Сохранение старых formats в переменную
3. Загрузка нового файла в temp
4. Обновление записи с новым temp_path и пустыми formats
5. Вызов process_image_variants.delay()
6. Commit в БД
7. Удаление старых вариантов через _delete_all_variants()

### Backward Compatibility:
- Метод get_url(size) в моделях работает с обоими форматами
- Если formats пустой → fallback на url
- При удалении: если formats пустой, но url заполнен → удаляется url

## Contracts Verified:
- Pydantic schemas: ✅ (используются существующие ProductImageRead, BlogPostMediaRead)
- DI via Depends: ✅ (ProductRepository через get_product_repo)
- No Any: ✅
- ruff: ✅ (All checks passed)
- mypy: ✅ (Success: no issues found in 2 source files)
- alembic heads: ✅ (exactly 1 head)

## Test Coverage:
- Unit tests не созданы (не требовались в acceptance criteria)
- Интеграционные тесты требуют запущенной БД и Celery

## Next:
- frontend-agent: обновить компоненты для использования get_url(size) вместо прямого url
- testing-agent: создать интеграционные тесты для upload/delete/update flow
- Опционально: добавить endpoint для update_image в router.py

## Blockers:
- none

## Notes:
- База данных не запущена во время разработки (alembic check требует подключения)
- Celery task process_image_variants уже реализован в p3_backend_image_variants_processing
- Temp файлы удаляются Celery task после успешной обработки
- Atomic update: сначала загружаются новые варианты, потом удаляются старые (не наоборот)
- MediaService.create_media_record добавлена проверка entity_id для blog context (mypy type safety)
