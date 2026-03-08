# Task Report: p11_cdek_order_tracking

## Status: DONE

## Completed:
- Создана модель OrderTrackingEvent для хранения истории статусов доставки
- Расширена модель Order полями: tracking_number, tracking_url, delivery_status, delivery_provider
- Создана Alembic миграция 20260308_1207-c3d4e5f6a7b8_add_order_tracking
- Добавлены методы get_tracking_url() во все провайдеры (CDEK, Pochta, Ozon, WB)
- Добавлен метод get_shipment_status() в pochta_client для polling
- Создан webhook router /api/v1/webhooks/delivery/{provider} для приёма статусов
- Создан Celery task poll_delivery_statuses для опроса статусов каждые 6 часов
- Расширен OrderRepository методами: get_by_cdek_uuid, get_by_tracking_number, get_orders_in_transit
- Добавлен метод create_shipment() в OrderService для auto-fulfillment (CDEK, Pochta)
- Обновлён .env.example с документацией webhook URLs

## Artifacts:
- backend/app/db/models/order_tracking.py
- backend/app/db/models/order.py (добавлены поля tracking)
- backend/app/db/migrations/versions/20260308_1207-c3d4e5f6a7b8_add_order_tracking.py
- backend/app/integrations/cdek.py (метод get_tracking_url)
- backend/app/integrations/pochta.py (методы get_tracking_url, get_shipment_status)
- backend/app/integrations/ozon_delivery.py (функция get_tracking_url)
- backend/app/integrations/wb_delivery.py (функция get_tracking_url)
- backend/app/api/v1/webhooks/delivery.py
- backend/app/api/v1/webhooks/__init__.py
- backend/app/tasks/delivery.py
- backend/app/api/v1/orders/repository.py (новые методы)
- backend/app/api/v1/orders/service.py (метод create_shipment)
- .env.example (webhook URLs)

## Migrations:
- 20260308_1207-c3d4e5f6a7b8: добавлены поля tracking в orders, создана таблица order_tracking_events

## Contracts Verified:
- ruff check: ✅ (0 errors)
- mypy --ignore-missing-imports: ✅ (0 errors)
- alembic check: ⚠️ (не проверено — БД не существует, миграция создана вручную)
- Celery task использует asyncio.run(): ✅
- Все env vars документированы в .env.example: ✅

## Implementation Details:

### Tracking URLs:
- CDEK: https://www.cdek.ru/ru/tracking?order_id={tracking_number}
- Pochta: https://www.pochta.ru/tracking#{tracking_number}
- Ozon: https://www.ozon.ru/my/orderdetails?orderId={tracking_number}
- WB: https://www.wildberries.ru/lk/myorders/delivery?id={tracking_number}

### Webhooks:
- POST /api/v1/webhooks/delivery/cdek — принимает статусы от CDEK
- POST /api/v1/webhooks/delivery/pochta — принимает статусы от Почты России
- Идемпотентность: всегда возвращают {"ok": true}, даже при ошибках (webhook contract)

### Celery Task:
- Задача: tasks.delivery.poll_delivery_statuses
- Периодичность: каждые 6 часов (настраивается в celery beat schedule)
- Опрашивает заказы в статусах SHIPPED, PROCESSING с tracking_number
- Создаёт OrderTrackingEvent при изменении статуса
- Обновляет Order.delivery_status и Order.status (при DELIVERED)

### Auto-fulfillment:
- OrderService.create_shipment(order_id, provider) — создаёт отправление через API провайдера
- Поддерживаются: CDEK (create_order), Pochta (create_shipment)
- Устанавливает tracking_number, tracking_url, delivery_provider
- Меняет статус заказа на SHIPPED
- Отправляет email уведомление с tracking_url

## Next:
- frontend-agent: добавить UI для отображения tracking_url и истории статусов
- testing-agent: написать тесты для webhook endpoints и Celery task
- devops-agent: настроить Celery beat schedule для poll_delivery_statuses (каждые 6 часов)
- devops-agent: зарегистрировать webhook URLs в личных кабинетах CDEK и Почты России

## Blockers:
- none

## Notes:
- Ozon и WB не имеют API для трекинга — используются статические tracking URLs
- Pochta.get_shipment_status() может требовать дополнительную авторизацию (проверить в production)
- CDEK webhook payload может отличаться от документации — требуется тестирование с реальными данными
