# P36: Миграция девайсов v2 (oc_token_to_device → user_devices)

> **Статус**: READY_TO_DEPLOY
> **Создан**: 2026-03-15
> **Источник**: oc_token_to_device (~800 записей) + oc_complectation_to_device (M2M)
> **Приемник**: user_devices + user_device_complectations (NEW) + module_complectations

---

## Контекст

Текущий `migrate_devices()` читает из `oc_devices` (~174 записи) — старая таблица.
Основные данные (~800 девайсов) лежат в `oc_token_to_device`.
`oc_tokens` используется только как lookup для связи девайс → пользователь.
Комплектации (`oc_complectations` + `oc_complectation_to_device`) не импортируются вообще.

---

## Фазы выполнения

### Фаза 1: Backend — модели и миграция БД
**Агент**: `backend-agent`
**Задача**: `p36_backend_device_models.json`
**Отчет**: `.claude/agents/reports/backend/p36_backend_device_models.md`

- [x] Добавить OC-модели в `opencart_models.py`:
  - `OCComplectation` (oc_complectations: id, code, caption, label, simple, date_added)
  - `OCComplectationToDevice` (oc_complectation_to_device: complectation_id, serial, date_added)
- [x] Создать M2M таблицу `user_device_complectations` в `user_device.py`:
  ```
  user_device_id UUID → FK user_devices.id (CASCADE)
  complectation_id UUID → FK module_complectations.id (CASCADE)
  PK (user_device_id, complectation_id)
  ```
- [x] Добавить relationship `complectations` в `UserDevice`
- [x] Alembic миграция: создать таблицу `user_device_complectations`
- [x] Проверить: `alembic check && alembic heads`
- [x] ruff: 0 errors, mypy: 0 issues, pytest: 4 passed

### Фаза 2: Backend — переписать migrate_devices()
**Агент**: `backend-agent`
**Задача**: `p36_backend_migrate_devices_v2.json`
**Отчет**: `.claude/agents/reports/backend/p36_backend_migrate_devices_v2.md`

**ВАЖНО**: не менять остальные миграции (users, addresses, orders, blog и т.д.)

#### Подфаза A: Справочник комплектаций
- [x] `oc_complectations` (7 записей) → `module_complectations`
- [x] One-shot, идемпотентность по `label`
- [x] Флаг: `extra_data.complectations_done`

#### Подфаза B: Девайсы
- [x] Источник: `oc_token_to_device`, батчами по 50, cursor по `id`
- [x] Resolve user: `token_id` → `oc_tokens.customer_id` → `oc_customer.email` → `email_hash` → User
- [x] Мердж по MAC (serial = device_uid):
  - Существует в user_devices → обновить model, registered_at = min(текущее, date_added)
  - Не существует → создать. name берем из oc_devices по device_serial если есть
- [x] Маппинг типов: OBD → WIFI_OBD2, AFR → WIFI_OBD2_ADVANCED
- [x] SAVEPOINT per device
- [x] Флаг: `extra_data.token_devices_done`

#### Подфаза C: Комплектации девайсов (M2M)
- [x] Источник: `oc_complectation_to_device`, батчами
- [x] Найти UserDevice по device_uid == serial
- [x] Найти ModuleComplectation по mapping oc_id → uuid (из подфазы A)
- [x] INSERT в user_device_complectations
- [x] Идемпотентность: PK (user_device_id, complectation_id)
- [x] SAVEPOINT per row
- [x] Флаг: `extra_data.device_complectations_done`

#### Прочее
- [x] Изменить count для entity=DEVICES: `OCDevice` → `OCTokenToDevice`
- [x] Подробное логирование каждого шага (structlog)

### Фаза 3: Верификация
**Агент**: `backend-agent`
**Задача**: (в рамках Фазы 2)

- [x] `ruff check app/` — 0 errors
- [x] `mypy app/ --ignore-missing-imports` — 0 issues (162 files)
- [x] `alembic check && alembic heads` — 1 head
- [ ] Тест: пересборка контейнеров + запуск миграции + проверка логов

---

## Что НЕ меняется

- Миграция users, addresses, orders, categories, products, blog
- Таблицы module_tokens, module_devices, device_complectations — не трогаем
- user_devices.module_device_id — оставляем nullable, не заполняем
- API эндпоинты миграции, Celery task

---

## Маппинг типов устройств

| oc_token_to_device.device_type | user_devices.model |
|---|---|
| `'OBD'` | `DeviceModel.WIFI_OBD2` |
| `'AFR'` | `DeviceModel.WIFI_OBD2_ADVANCED` |

---

## Логика мерджа по MAC-адресу

| Поле | oc_token_to_device | oc_devices | Результат |
|---|---|---|---|
| device_uid | serial | device_serial | MAC (ключ мерджа) |
| user_id | через oc_tokens → customer → User | через customer_id → User | oc_token_to_device |
| name | нет | device_name | из oc_devices |
| model | OBD/AFR маппинг | WiFi OBD2/Advanced | oc_token_to_device |
| registered_at | date_added | register_date | min(оба) |
| comment | comment | comment | oc_token_to_device, fallback oc_devices |
