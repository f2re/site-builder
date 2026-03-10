# Orchestrator Summary — WifiOBD Site

Обновлено: 2026-03-11

## Текущая фаза: 33 (Critical Migration Bugs Fix)
## Выполнено задач: 24 / 35 (1 новая критическая задача поставлена в очередь)

---

## Статус задач

| task_id | Агент | Титул | Статус | Приоритет |
|---|---|---|---|---|
| p1_devops_001 | devops-agent | Infrastructure Setup | ⏳ PENDING | high |
| ... | ... | ... | ... | ... |
| **p28_backend_blog_categories** | backend-agent | Blog Category CRUD + Stable Composite Cursor Pagination | ✅ DONE | high |
| **p28_frontend_blog_admin** | frontend-agent | Blog Admin UI (Categories CRUD, Post Pagination) | ✅ DONE | high |
| **p28_devops_nginx_api_proxy** | devops-agent | API Proxy Refinements (trailing slash, /media) | ✅ DONE | medium |
| **p31_backend_product_options** | backend-agent | Product Option Groups & Values (Models, API, Migration) | ✅ DONE | high |
| **p31_backend_cart_options** | backend-agent | Cart/Order Options Snapshot & Migration | ✅ DONE | high |
| **p31_frontend_product_options** | frontend-agent | Product Options UI (Selector, Calculation, Admin CRUD) | ✅ DONE | high |

---

## Фаза 31 — Product Option Groups (2026-03-08)

| task_id | Агент | Описание | Приоритет | Статус |
|---|---|---|---|---|
| p31_backend_product_options | backend-agent | Модели, миграция, схемы, сервис, admin CRUD, публичный эндпоинт | high | ✅ DONE |
| p31_backend_cart_options | backend-agent | CartItem.selected_options JSONB, миграция, обновить AddToCart | high | ✅ DONE |
| p31_frontend_product_options | frontend-agent | UI выбора опций, расчёт цены, admin CRUD (зависит от backend) | high | ✅ DONE |

### Реализовано:
- ✅ **Option Models**: Добавлены `ProductOptionGroup` и `ProductOptionValue` с поддержкой модификаторов цены.
- ✅ **Cart/Order Snapshots**: Опции сохраняются как JSON-снэпшот в `CartItem` и `OrderItem`, фиксируя цену и название на момент заказа.
- ✅ **Composite Cart Keys**: Корзина в Redis теперь поддерживает несколько записей одного товара с разными опциями.
- ✅ **UI Selector**: На странице товара добавлен выбор опций с реактивным пересчетом цены.
- ✅ **Admin CRUD**: В админке реализован менеджер групп и значений опций прямо в карточке товара.

### Отчёты:
- [backend/p31_backend_product_options.md](.claude/agents/reports/backend/p31_backend_product_options.md)
- [backend/p31_backend_cart_options.md](.claude/agents/reports/backend/p31_backend_cart_options.md)
- [frontend/p31_frontend_product_options.md](.claude/agents/reports/frontend/p31_frontend_product_options.md)

---

## Фаза 32 — Миграция устройств из OpenCart (2026-03-09)

| task_id | Агент | Описание | Приоритет | Статус |
|---|---|---|---|---|
| p32_backend_devices_migration | backend-agent | UserDevice модель (+comment, +oc_device_id), Alembic, OC-модели, migrate_devices(), Admin CRUD API | high | ⏳ PENDING |
| p32_frontend_devices_admin | frontend-agent | Страница /admin/devices, сайдбар, вкладка Devices в карточке пользователя | high | ⏳ PENDING (зависит от backend) |

---

## Фаза 33 — Исправление критических багов миграции (2026-03-11)

| task_id | Агент | Описание | Приоритет | Статус |
|---|---|---|---|---|
| p33_backend_migration_critical_bugs | backend-agent | Исправить 4 критических бага: rollback убивает batch, пустой email теряет данные, PAUSED/FAILED jobs не перезапускаются, devices без idempotency check | critical | ⏳ PENDING |

### Критические баги:
1. **Rollback убивает весь batch** — при ошибке на 3-й из 50 записей откатываются все flush(), но счётчики уже увеличены. Фикс: SAVEPOINT (begin_nested).
2. **Пустой email — потеря данных** — get_blind_index("") возвращает одинаковый hash для всех пустых email. Фикс: уникальный hash с customer_id.
3. **PAUSED/FAILED jobs не перезапускаются** — get_active_job_by_entity ищет только PENDING/RUNNING. Фикс: добавить PAUSED/FAILED в фильтр.
4. **Devices без idempotency check** — полагается на UNIQUE + rollback (см. баг 1). Фикс: проверка oc_device_id перед INSERT.

### Что нужно реализовать:
- Добавить 2 поля в `UserDevice`: `comment` и `oc_device_id`
- 3 новых OC-модели в `opencart_models.py`: `OCDevice`, `OCToken`, `OCTokenToDevice`
- Метод `migrate_devices()` в `MigrationService` с пагинацией batch_size=50
- 5 Admin CRUD эндпоинтов: GET list, GET detail, PATCH, DELETE, GET by user
- Frontend: страница `/admin/devices/index.vue` с таблицей, фильтрами, пагинацией
- Сайдбар: пункт "Устройства" перед "Миграция"

---

## Последнее действие

> **2026-03-08: ✅ Полная реализация комплектаций (опций) товаров**
>
> Выполнены задачи:
> - ✅ p31_backend_product_options — Модели, миграция, API
> - ✅ p31_backend_cart_options — Снэпшоты опций в корзине и заказах
> - ✅ p31_frontend_product_options — UI выбора и админка
>
> **Новые возможности:**
> - Админ может добавлять опции (напр. "Длина кабеля", "Цвет") к любому товару.
> - Опции могут быть обязательными и влиять на итоговую цену.
> - Покупатель видит выбранные опции в корзине и при оформлении заказа.
>
> **Верификация:**
> - ruff: ✅ | mypy: ✅ (150 files)
> - pytest: 57 passed
> - frontend build: ✅
