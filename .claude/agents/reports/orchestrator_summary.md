# Orchestrator Summary — WifiOBD Site

Обновлено: 2026-03-08

## Текущая фаза: 19 (OpenCart Address Migration)
## Выполнено задач: 15 / 25 ✅

---

## Статус задач

| task_id | Агент | Титул | Статус | Приоритет |
|---|---|---|---|---|
| p1_devops_001 | devops-agent | Infrastructure Setup | ⏳ PENDING | high |
| p2_backend_001 | backend-agent | Backend Core | BLOCKED (p1) | high |
| p3_backend_001 | backend-agent | Catalog & Blog | BLOCKED (p2) | high |
| p4_backend_001 | backend-agent | E-Commerce Core | BLOCKED (p3) | high |
| p4_cdek_001 | cdek-agent | CDEK + YooKassa | BLOCKED (p4_b) | high |
| p5_backend_001 | backend-agent | IoT Layer | BLOCKED (p2) | medium |
| p6_cdek_001 | cdek-agent | CBR Rates + Celery | BLOCKED (p4_c) | medium |
| p7_frontend_001 | frontend-agent | Nuxt 3 Frontend | BLOCKED (p3,p4) | high |
| p8_testing_001 | testing-agent | Tests + Locust | BLOCKED (p4,p5,p6) | high |
| p8_e2e_backend_001 | backend-agent | seed_e2e.py | BLOCKED (p2,p3,p4) | critical |
| p8_e2e_frontend_001 | frontend-agent | data-testid расстановка | BLOCKED (p7) | critical |
| p8_e2e_testing_001 | testing-agent | Запуск E2E + отчёт | BLOCKED (p8_e2e_b + p8_e2e_f) | high |
| p9_security_001 | security-agent | Security Audit | BLOCKED (p8) | high |
| **p10_devops_delivery_secrets** | devops-agent | Env vars для новых провайдеров доставки | ✅ DONE | high |
| **p10_backend_delivery_providers** | backend-agent | 3 новых провайдера доставки + агрегатор | ✅ DONE | high |
| **p10_frontend_delivery_selector** | frontend-agent | UI выбора провайдера доставки | ✅ DONE | high |
| **p10_backend_migration_fixes** | backend-agent | Reset endpoint, blog-categories, additional images, bleach | ⏳ PENDING | high |
| **p10_frontend_migration_ux** | frontend-agent | Fix empty page, polling, reset button + dialog | BLOCKED (p10_backend_migration_fixes) | high |
| **p11_backend_user_addresses** | backend-agent | User Delivery Addresses Management | ✅ DONE | high |
| **p11_cdek_order_tracking** | cdek-agent | Order Tracking and Auto-fulfillment | ✅ DONE | high |
| **p11_frontend_address_management** | frontend-agent | Address Management UI and Order Tracking | ✅ DONE | high |
| **p11_testing_addresses_tracking** | testing-agent | Tests for Address Management and Order Tracking | ✅ DONE | medium |
| **p12_backend_migration_images_fix** | backend-agent | Fix Image Download in OpenCart Migration | ✅ DONE | medium |

---

## Готовы к запуску

- **p1_devops_001** [devops-agent] — Infrastructure Setup

```
/agents:run devops-agent p1_devops_001
```

---

## Граф зависимостей

```
p1 → p2 → p3 → p4_backend → p4_cdek → p6
              p3 → p7
    p2 → p5
              p4_b + p4_c + p5 + p6 → p8 → p9

E2E подграф (параллельно с p8):
    p2+p3+p4 → p8_e2e_backend ──┐
              p7 → p8_e2e_frontend ──┤→ p8_e2e_testing → p9
```

---

## E2E цикл — порядок запуска когда p7 и p4 готовы

```bash
# Параллельно:
/agents:run backend-agent p8_e2e_backend_001
/agents:run frontend-agent p8_e2e_frontend_001

# После завершения обоих:
/agents:run testing-agent p8_e2e_testing_001
```

Контракт data-testid: `.claude/agents/contracts/e2e_testid_contract.md`
Отчёт testing-agent: `.claude/agents/reports/testing/p8_e2e_testing_001.md`

---

## Блокеры

- none

## Hotfixes Applied (2026-03-06)

| task_id | Статус | Что исправлено |
|---|---|---|
| bugfix_backend_001 | ✅ DONE | config.py CORS empty-string, inventory.py enum .value, blog 401 |
| bugfix_frontend_001 | ✅ DONE | frontend/public/placeholder-product.png |
| bugfix_media_001 | ✅ DONE | nuxt.config.ts devProxy /media, nginx.dev.conf, nginx.conf |

После деплоя: пересобрать backend+celery контейнеры; перезапустить Nuxt dev-сервер.

## Задача p13_frontend_alerts_fix — DONE (2026-03-08)

Заменены все нативные диалоги браузера на UI-компоненты дизайн-системы:
- 7 × `alert()` → `useToast()` с типами warning/error
- 8 × `confirm()` → `useConfirm()` с Promise API и вариантами danger/warning/default
- 4 × `prompt()` / `window.prompt()` → `usePrompt()` с Promise API

Созданы: `useConfirm.ts`, `usePrompt.ts`, `UConfirmDialog.vue`, `UPromptDialog.vue`, `UToast.vue`.
Подключены глобально в `app.vue`.
Затронуто 13 файлов в frontend/.

Отчёт: `.claude/agents/reports/frontend/p13_frontend_alerts_fix.md`

---

## Фаза 14 — Critical Bug Fixes (2026-03-08)

| task_id | Агент | Титул | Статус | Приоритет |
|---|---|---|---|---|
| **p14_backend_migration_fix** | backend-agent | UniqueViolationError в миграции + очистка пользователей | ⏳ PENDING | high |
| **p14_backend_user_edit** | backend-agent | PATCH /admin/users/{id} + адреса пользователя | ⏳ PENDING | high |
| **p14_frontend_migration_reactivity** | frontend-agent | Реактивность миграции + пагинация товаров + описание | ⏳ PENDING | high |
| **p14_frontend_user_edit** | frontend-agent | Редактирование пользователя в админке | ⏳ PENDING (depends: p14_backend_user_edit) | high |

### Порядок запуска:
```
# Шаг 1 — параллельно:
/agents:run backend-agent p14_backend_migration_fix
/agents:run backend-agent p14_backend_user_edit
/agents:run frontend-agent p14_frontend_migration_reactivity

# Шаг 2 — после завершения p14_backend_user_edit:
/agents:run frontend-agent p14_frontend_user_edit
```

---

## Фаза 15 — OpenCart SEO Redirects (2026-03-08)

### Анализ проблем (оркестратор, 2026-03-08)

| Направление | Статус | Вывод |
|---|---|---|
| redirect_router.py — query string | ПРОБЛЕМА | `{path:path}` не захватывает query string; `/index.php?route=...&path=61_67` обрезается до `index.php` |
| redirect_repository.py | ЗАВИСИТ от роутера | После исправления роутера логика корректна |
| migration_service.py — blog+теги+изображения | РЕАЛИЗОВАНО | Теги из meta_keyword, категории как теги, изображения — всё есть |
| Скрипт seed_redirects.py | ОТСУТСТВУЕТ | Нет ни одного скрипта для наполнения таблицы Redirect |
| GET /blog/posts фильтрация | РЕАЛИЗОВАНО | category и tag параметры присутствуют в router и repository |
| Frontend OpenCart URL interceptor | ОТСУТСТВУЕТ | В frontend/middleware/ только auth.ts; нет перехватчика index.php URLs |

### Созданные задачи

| task_id | Агент | Описание | Приоритет | Статус |
|---|---|---|---|---|
| p15_backend_redirect_fix | backend-agent | Исправить redirect_router (Query param вместо path:path), создать scripts/seed_redirects.py | high | ✅ DONE |
| p15_frontend_opencart_redirect | frontend-agent | Создать frontend/middleware/opencart-redirect.global.ts | high | ✅ DONE |


### Порядок запуска:
```
# Шаг 1:
/agents:run backend-agent p15_backend_redirect_fix

# Шаг 2 — после завершения backend задачи:
/agents:run frontend-agent p15_frontend_opencart_redirect
```

---

## Фаза 16 — C2C Shipment Card (2026-03-08)

### Описание

Система информирования администратора об отправке заказов через Ozon C2C и WB Track. Поскольку у обоих провайдеров нет публичного API, реализуется генерация "карточки отправки" с готовыми данными для копирования и deeplink в мобильное приложение.

| task_id | Агент | Описание | Статус | Приоритет |
|---|---|---|---|---|
| **p16_backend_c2c_shipment** | backend-agent | C2CShipmentPayload dataclass, generate_c2c_payload() для Ozon и WB, endpoint GET /api/v1/delivery/orders/{id}/c2c-shipment | ✅ DONE | high |
| **p16_frontend_c2c_card** | frontend-agent | Страница /admin/orders/[id].vue + блок карточки C2C с инструкцией, deeplink и копированием | ✅ DONE | high |

### Порядок запуска:
```
# Шаг 1:
/agents:run backend-agent p16_backend_c2c_shipment

# Шаг 2 — после завершения backend задачи:
/agents:run frontend-agent p16_frontend_c2c_card
```

### Новые API endpoints (после завершения):
- `GET /api/v1/delivery/orders/{order_id}/c2c-shipment` — карточка C2C отправки (auth: admin)

---

## Фаза 18 — OpenCart Migration Fixes (2026-03-08)

| task_id | Агент | Титул | Статус | Приоритет |
|---|---|---|---|------|
| **p18_backend_migration_opencart_fixes** | backend-agent | Fix OpenCart Migration: Information Pages, TipTap, Images, Tags | ✅ DONE | critical |

### Реализовано:
- ✅ HTML → TipTap JSON конвертер (_html_to_tiptap)
- ✅ Миграция OCInformation → BlogPost (новости/инструкции)
- ✅ Product.content_json и BlogPost.content_json заполняются TipTap JSON
- ✅ Поле oc_information_id в BlogPost
- ✅ Скрипт seed_redirects.py для information/information URLs
- ✅ Теги создаются из meta_keyword

### Верификация:
- ruff: ✅ | mypy: ✅ (141 files) | alembic heads: ✅

### Отчёт:
- [backend/p18_backend_migration_opencart_fixes.md](.claude/agents/reports/backend/p18_backend_migration_opencart_fixes.md)

---

## Фаза 17 — Celery Migration Fix (2026-03-08)

| task_id | Агент | Титул | Статус | Приоритет |
|---|---|---|---|------|
| **p17_backend_celery_migration_fix** | backend-agent | Fix Celery Migration: Permissions and Event Loop | ✅ DONE | critical |

### Описание проблемы:
- Permission denied при создании `/app/media/products` в Celery worker
- RuntimeError: Event loop is closed при dispose async engines

### Решение:
1. **Dockerfile**: Создание `/app/media/{products,blog}` с правильными правами в development и production stages
2. **docker-compose.yml**: Добавлен volume `./media:/app/media` для celery сервиса
3. **migration_tasks.py**: Убран вложенный `asyncio.run()`, обработка ошибок внутри основного event loop
4. **migration_service.py**: Добавлена обработка PermissionError с понятным сообщением

### Верификация:
- ruff: ✅ | mypy: ✅ (140 files) | alembic heads: ✅

### Отчёт:
- [backend/p17_backend_celery_migration_fix.md](.claude/agents/reports/backend/p17_backend_celery_migration_fix.md)

---

## Фаза 19 — OpenCart Address Migration (2026-03-08)

| task_id | Агент | Титул | Статус | Приоритет |
|---|---|---|---|------|
| **p19_backend_address_migration** | backend-agent | Import Customer Addresses from OpenCart | ⏳ PENDING | high |

---

## Фаза 20 — Admin Orders Enhancements (2026-03-08)

| task_id | Агент | Титул | Статус | Приоритет |
|---|---|---|---|------|
| **p22_backend_orders_date_filter** | backend-agent | Add Date Range Filters to Admin Orders API | ✅ DONE | medium |

### Реализовано:
- ✅ Добавлены параметры date_from и date_to в GET /api/v1/admin/orders
- ✅ OrderRepository.list_all() фильтрует по диапазону дат created_at
- ✅ Логика: created_at >= date_from AND created_at < date_to + 1 day

### Верификация:
- ruff: ✅ | mypy: ✅ (142 files)

### Отчёт:
- [backend/p22_backend_orders_date_filter.md](.claude/agents/reports/backend/p22_backend_orders_date_filter.md)

---

## Фаза 21 — Admin User Search Fix (2026-03-08)

| task_id | Агент | Титул | Статус | Приоритет |
|---|---|---|---|------|
| **p23_backend_user_search_fix** | backend-agent | Fix Admin User Search - Add Name Search Support | ⏳ PENDING | high |
| **p24_backend_address_import** | backend-agent | Import Customer Addresses from OpenCart | ⏳ PENDING (depends: p23) | medium |

### Проблемы:
1. **Поиск не работает**: Frontend отправляет `q=Alexand`, backend ожидает `search`
2. **Поиск только по email**: Текущая реализация ищет только по точному email через blind index
3. **Имена зашифрованы**: full_name зашифровано, поиск по имени невозможен
4. **Адреса не импортируются**: Нет логики импорта адресов из oc_address

### Решение:
- Добавить параметр `q` как алиас для `search`
- Добавить поле `full_name_normalized` (незашифрованное, lowercase)
- Реализовать ILIKE поиск по `full_name_normalized`
- Импортировать адреса из OpenCart после исправления поиска

### Порядок запуска:
```
# Шаг 1:
/agents:run backend-agent p23_backend_user_search_fix

# Шаг 2 — после завершения p23:
/agents:run backend-agent p24_backend_address_import
```

---

## Последнее действие

> **2026-03-08: ✅ Добавлена фильтрация заказов по дате**
>
> Выполнена задача:
> - ✅ p22_backend_orders_date_filter — добавлены параметры date_from/date_to в GET /admin/orders
>
> **Реализовано:**
> - Параметры date_from и date_to в GET /api/v1/admin/orders
> - OrderRepository.list_all() фильтрует по created_at >= date_from AND created_at < date_to + 1 day
> - Frontend может использовать фильтр по дате
>
> **Верификация:**
> - Backend: ruff ✅, mypy ✅ (142 files)
>
> **Новые проблемы обнаружены:**
> - Поиск пользователей не работает (q=Alexand возвращает пустой результат)
> - Frontend отправляет параметр `q`, backend ожидает `search`
> - Поиск работает только по точному email через blind index
> - Адреса пользователей не импортируются из OpenCart
>
> **Созданы задачи:**
> - p23_backend_user_search_fix — исправить поиск пользователей (добавить full_name_normalized)
> - p24_backend_address_import — импортировать адреса из oc_address
>
> **Следующие шаги:**
> ```
> /agents:run backend-agent p23_backend_user_search_fix
> ```
>
> **Отчёт:**
> - [backend/p22_backend_orders_date_filter.md](.claude/agents/reports/backend/p22_backend_orders_date_filter.md)
>
> Выполнена задача:
> - ✅ p18_backend_migration_opencart_fixes — исправлены критические проблемы миграции
>
> **Реализовано:**
> - HTML → TipTap JSON конвертер для Product и BlogPost
> - Миграция OCInformation (новости/инструкции) → BlogPost
> - Теги создаются из meta_keyword
> - Скрипт seed_redirects.py для information/information URLs
> - Добавлено поле oc_information_id в BlogPost
>
> **Верификация:**
> - Backend: ruff ✅, mypy ✅ (141 files), alembic heads ✅
>
> **Следующие шаги:**
> - Установить зависимости: `pip install -r backend/requirements.txt`
> - Применить миграцию: `alembic upgrade head`
> - Запустить миграцию через API
> - Запустить seed_redirects.py
>
> **Известные ограничения:**
> - Изображения 404: требует исследования frontend (Nuxt IPX)
>
> **Отчёт:**
> - [backend/p18_backend_migration_opencart_fixes.md](.claude/agents/reports/backend/p18_backend_migration_opencart_fixes.md)
