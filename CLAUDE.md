# CLAUDE.md — Точка входа Claude Code агентов

> **Читай этот файл ПЕРВЫМ при каждой новой задаче.**
> Этот файл — адаптация GEMINI.md + AGENTS.md + .gemini/system.md для [Claude Code](https://docs.anthropic.com/en/docs/claude-code).
> **Архитектурные инварианты:** [ARCHITECTURE.md](ARCHITECTURE.md)
> **DevOps-детали:** [DEVOPS.md](DEVOPS.md)
> **Детальный план разработки:** [plan.md](plan.md)
> **Активные задачи:** [.claude/agents/tasks/](.claude/agents/tasks/)
> **Отчёты агентов:** [.claude/agents/reports/](.claude/agents/reports/)

---

## 🎯 Концепция проекта

**WifiOBD Site** — интернет-магазин автомобильной электроники (OBD-адаптеры, телематика) с:
- 🛒 **Магазином** — каталог товаров, корзина, оформление заказа, оплата, доставка СДЭК
- 📝 **Блогом** — статьи, документация, обзоры
- 📊 **IoT-дашбордом** — онлайн телеметрия от OBD-устройств (WebSocket, TimescaleDB)
- 🔧 **Админ-панелью** — управление товарами, заказами, контентом, пользователями

**Аудитория:** небольшой трафик (до 1000 DAU). Приоритет — надёжность и простота поддержки, не масштаб.

---

## 🔧 Технологический стек

### Backend
- **Python 3.12**, FastAPI (async), SQLAlchemy 2.x (async), Alembic
- **PostgreSQL 16 + TimescaleDB** — основная БД + IoT-телеметрия (hypertable)
- **Redis 7** — сессии, кэш, Celery broker
- **Celery + Beat** — фоновые задачи (уведомления, обновление курсов, индексация)
- **Meilisearch** — полнотекстовый поиск по товарам и статьям

### Frontend
- **Nuxt 3** (SSR), Vue 3 Composition API, TypeScript, Pinia
- Design tokens: `frontend/assets/css/tokens.css` — единственный источник цветов/отступов
- Темы: dark (default) / light — управляет `themeStore` + `UThemeToggle`
- PWA: `@vite-pwa/nuxt` | i18n: `@nuxtjs/i18n` (ru/en)

### Интеграции
- **СДЭК v2 API** — расчёт и оформление доставки
- **ЮKassa / aiomoney** — приём платежей
- **ЦБ РФ** — актуальные курсы валют (USD, EUR, CNY)

### Инфраструктура
- **Docker Compose** — dev: `docker-compose.yml`, prod: `deploy/docker-compose.prod.yml`
- **Nginx** — reverse proxy + раздача статики
- **CI/CD: GitLab CI** (`.gitlab-ci.yml`) — **НИКОГДА не GitHub Actions**
- **Registry: GitLab Container Registry** — **НИКОГДА не Docker Hub**
- Секреты: `.env` (в git не коммитить), шаблон: `.env.example`

---

## 🤖 Мультиагентная система — Claude Code

### Роль оркестратора (этот файл)

Ты — ОРКЕСТРАТОР мультиагентной системы разработки проекта **WifiOBD Site**.

**Обязанности оркестратора:**
1. Читать задачи из `.claude/agents/tasks/*.json`
2. Декомпозировать запрос пользователя на подзадачи для агентов
3. Создавать `.json`-файлы задач в `.claude/agents/tasks/` перед вызовом агента
4. Делегировать задачи специализированным агентам (самому код **НЕ** писать)
5. Читать и валидировать отчёты из `.claude/agents/reports/`
6. Писать сводку в `.claude/agents/reports/orchestrator_summary.md`
7. Эскалировать блокеры пользователю

### Агенты и зоны ответственности

| Агент | Зона ответственности | Запускать после | Контекст |
|---|---|---|---|
| `devops-agent` | Docker, Nginx, GitLab CI/CD, мониторинг | — (первый) | `deploy/CLAUDE.md` |
| `backend-agent` | FastAPI, SQLAlchemy, Alembic, REST API, WebSocket, IoT | `devops-agent` | `backend/CLAUDE.md` |
| `cdek-agent` | СДЭК v2, ЮKassa, ЦБ РФ, Celery-задачи интеграций | `backend-agent` | `backend/CLAUDE.md` |
| `frontend-agent` | Nuxt 3, Vue 3, Pinia, UI kit, темы, PWA, админ-панель | `backend-agent` (API-контракты готовы) | `frontend/CLAUDE.md` |
| `testing-agent` | pytest, интеграционные тесты, WebSocket, Locust | `backend-agent` + `cdek-agent` | `tests/CLAUDE.md` |
| `security-agent` | OWASP, 152-ФЗ, аудит (READ-ONLY, код не меняет) | `testing-agent` | `CLAUDE.md` (root) |

**Порядок в фазе:**
```
devops-agent → backend-agent → cdek-agent → frontend-agent → testing-agent → security-agent
```

### Граф зависимостей фаз (9 фаз)

```
Фаза 1: Инфраструктура          → devops-agent
Фаза 2: Backend Core            → backend-agent        (depends: Фаза 1)
Фаза 3: Каталог и Блог          → backend-agent        (depends: Фаза 2)
Фаза 4: E-Commerce Core         → backend-agent + cdek-agent (depends: Фаза 3)
Фаза 5: IoT Layer               → backend-agent        (depends: Фаза 2)
Фаза 6: Валюта и интеграции     → cdek-agent           (depends: Фаза 4)
Фаза 7: Frontend                → frontend-agent       (depends: Фаза 3 + 4)
Фаза 8: Тестирование            → testing-agent        (depends: Фаза 4 + 5 + 6)
Фаза 9: Безопасность + Deploy   → security-agent + devops-agent (depends: Фаза 8)
```

```
Фаза1 → Фаза2 → Фаза3 → Фаза4 → Фаза6
                  Фаза3 → Фаза7
       Фаза2 → Фаза5
                  Фаза4+5+6 → Фаза8 → Фаза9
```

---

## 🔄 Рабочий цикл агента (4 фазы — ОБЯЗАТЕЛЬНЫ)

### Фаза 1 — PLAN [режим: расширенное рассуждение]
**НЕ ПИШИ КОД.** Только:
- Прочитай задачу и этот файл
- Изучи затронутые файлы (Read, Glob, Grep)
- Сформулируй план в 5–10 шагах
- Опиши стратегию верификации (какие команды докажут готовность)

### Фаза 2 — IMPLEMENT
- Пиши код с учётом тестируемости
- Создавай unit-тесты параллельно с кодом (не в конце)

### Фаза 3 — VERIFY [режим: расширенное рассуждение]
- Запусти ВСЕ команды из раздела Tooling ниже
- Проверь полный вывод — не «пробегай глазами»
- Сверь результат с Definition of Done

### Фаза 4 — FIX
- Исправляй по конкретным ошибкам из Фазы 3
- Повторяй с Фазы 3 до полного соответствия DoD

> ⚠️ Если один файл правился 3+ раза — рассмотри другой подход целиком.

---

## 🛠 Tooling — обязательные команды

```bash
# Backend (из директории /backend):
ruff check app/ --fix && ruff check app/ && mypy app/ --ignore-missing-imports

# Frontend (из директории /frontend):
npm install --quiet && npm run lint

# База данных:
alembic check && alembic heads

# Тесты:
pytest tests/ -x -v
```

---

## ✅ Definition of Done (DoD)

Задача считается выполненной ТОЛЬКО при выполнении ВСЕХ пунктов:

- [ ] `ruff check app/` → **0 errors**
- [ ] `mypy app/ --ignore-missing-imports` → **Success: no issues found**
- [ ] `npm run lint` → **no errors** (vue-tsc)
- [ ] `pytest tests/` → **all green**
- [ ] `alembic check` → **OK** (модели совпадают с миграциями)
- [ ] `alembic heads` → **ровно 1 head**
- [ ] Отчёт агента написан в `.claude/agents/reports/<domain>/<task_id>.md`

---

## 📋 Шаблон отчёта агента

```markdown
## Status: DONE | IN_PROGRESS | BLOCKED
## Completed:
- список выполненного
## Artifacts:
- backend/app/api/v1/products/router.py
## Contracts Verified:
- Pydantic schemas: ✅
- DI via Depends: ✅
- ruff: ✅ | mypy: ✅ | pytest: ✅
## Next:
- передать frontend-agent: API контракт /api/v1/products готов
## Blockers:
- нет
```

Отчёт сохранять в: `.claude/agents/reports/<domain>/<task_id>.md`

---

## 🚫 MUST / MUST NOT

### MUST
- Проходить все 4 фазы в каждой задаче
- Запускать tooling-команды перед каждым коммитом
- Новый endpoint → только в `backend/app/api/v1/<feature>/` со структурой `router/service/repository/schemas`
- Новые зависимости → только с точной версией в `requirements.txt`, проверить `pip install -r requirements.txt`
- Изменения инфраструктуры → в оба файла одновременно: `docker-compose.yml` + `deploy/docker-compose.prod.yml`
- Docker images → только фиксированные версии (например `v1.36.0`)
- Писать отчёт в `.claude/agents/reports/<domain>/<task_id>.md` по шаблону выше
- При добавлении пакетов: `npm install --legacy-peer-deps` (критично для TipTap)
- Для интеграционных тестов: `fakeredis[lua]>=2.20.0`
- В Celery воркерах для async: **только** `asyncio.run()` (не `get_event_loop()`)
- `await session.commit()` в КАЖДОМ методе, изменяющем данные (POST/PUT/PATCH/DELETE)
- Перед Pydantic-валидацией: загружать все relations через `selectinload` или `refresh`

### MUST NOT
- Коммитить `.env` или любые секреты
- Хардкодить цвета/отступы в `.vue` (только CSS-переменные из `tokens.css`)
- Менять `backend/app/core/` без unit-тестов
- Использовать GitHub Actions (только GitLab CI/CD)
- Использовать Docker Hub (только GitLab Container Registry)
- Использовать `:latest` в docker images
- Дублировать типы: `app/models/`, `app/schemas/`, `app/services/` вне `api/v1/<feature>/`
- Вручную добавлять `/api/v1` в пути при использовании `useFetch` с `baseURL: apiBase`
- Использовать имя `Device` (конфликт автоимпортов Nuxt) → использовать `IoTDevice` / `FirmwareDevice`

---

## 📐 Контракты разработки

### 🌐 API Path & BaseURL Policy
1. `apiBase` в `runtimeConfig` **ОБЯЗАН** включать версию (например, `/api/v1`)
2. **ЗАПРЕЩЕНО** вручную добавлять `/api/v1` в относительные пути при использовании `useFetch` или `$fetch` с `baseURL: apiBase`
3. Все пути в композаблах начинаются с `/` относительно `apiBase` (например, `/products`, а не `/api/v1/products`)

### 🔐 Auth & Profile Flow Contract
1. Любой эндпоинт авторизации (`login`, `callback`, `telegram`) **ОБЯЗАН** возвращать полную модель `UserResponse` в поле `user` вместе с токенами
2. В фронтенд-композаблах использовать строго `accessToken` (не `token`, не `jwt`)
3. При обновлении `email` — бэкенд **ОБЯЗАН** пересчитывать `email_hash` (blind index)

### 📱 UI Parity Rule
Любая навигационная ссылка в мобильном меню (Drawer) **ДОЛЖНА** иметь аналог в десктопной версии (Header/Sidebar), если иное не оговорено.

### 🎨 Design Token Contract (Frontend)
```
frontend/assets/css/tokens.css   ← ЕДИНСТВЕННЫЙ источник всех дизайн-токенов
frontend/stores/themeStore.ts    ← ЕДИНСТВЕННЫЙ источник состояния темы
frontend/components/U/UThemeToggle.vue ← глобальная кнопка переключения темы
```
- `themeStore.toggle()` **MUST** обновлять `document.documentElement.dataset.theme`
- Тема **MUST** сохраняться в `localStorage` key `theme`
- SSR: читать тему из cookie `theme` (httpOnly=false) во избежание hydration mismatch
- Тема по умолчанию: `dark` | Контраст текста: ≥ 4.5:1 (WCAG 2.1 AA)

### 📊 IoT / Телеметрия Contract
- Таблица `telemetry` **MUST** быть TimescaleDB hypertable (chunk_time_interval = '1 day')
- WebSocket эндпоинт: `ws://host/ws/iot/{device_id}`
- Данные: Redis Streams → Celery consumer → TimescaleDB
- Дашборд: агрегация через TimescaleDB `time_bucket` (не raw SELECT)
- Retention policy: 90 дней (`TELEMETRY_RETENTION_DAYS` в .env)

### 🏗 Infrastructure Sync Policy
- **Double Edit Rule**: любые изменения инфраструктуры вносить одновременно в `docker-compose.yml` **И** `deploy/docker-compose.prod.yml`
- **ENUM protection**: все новые ENUM-типы в миграциях **MUST** иметь `IF NOT EXISTS` в `pg_type`

---

## 🗂 Feature-First структура backend

Каждая фича в `backend/app/api/v1/{feature}/` **MUST** содержать:
- `router.py` — маршруты FastAPI
- `service.py` — бизнес-логика (DI-ready)
- `repository.py` — CRUD через SQLAlchemy async
- `schemas.py` — Pydantic Request/Response модели

Кросс-доменная логика → `app/core/` или `app/tasks/`. Модели SQLAlchemy **MUST** жить только в `backend/app/db/models/`.

---

## 🌳 Правила Git

1. **Язык**: сообщения коммитов — **русский язык**
2. **Эмодзи**: начинать заголовок с эмодзи (✨ фичи, 🐛 баги, ♻️ рефакторинг, 🚀 CI/CD, 📝 документация, 🔒 безопасность)
3. **Тело коммита**: детальное описание — что сделано, почему, какие компоненты затронуты

**Пример:**
```text
✨ Добавлен функционал корзины с Redis Lua

- Реализовано атомарное резервирование товаров через Lua-скрипт.
- Создан CartService с поддержкой гостевых и авторизованных корзин.
- Обновлен OrderService: валидация стока в Redis перед сохранением в БД.
```

---

## ⚙️ Команды Claude Code (slash commands)

Команды хранятся в `.claude/commands/`. Используй:

```
/agents:plan <описание задачи>   → декомпозиция на подзадачи + JSON-файлы задач
/agents:run <agent> <task_id>    → запуск агента с загрузкой нужного CLAUDE.md
/agents:verify                   → запуск всех DoD проверок + валидация отчётов
/agents:status                   → сводка по активным задачам и отчётам
```

### Формат команды /agents:plan

Вывод плана:
```
## Execution Plan: <задача>

### Фаза N: <название>
- [ ] <task_id> | <agent> | <заголовок> | depends_on: [<ids>]

### Параллельные треки:
- Трек A: <task_ids>
- Трек B: <task_ids>

### Критический путь: <список фаз/задач>
```

Формат файла задачи (`.claude/agents/tasks/<task_id>.json`):
```json
{
  "task_id": "p2_backend_001",
  "phase": 2,
  "agent": "backend-agent",
  "title": "Реализовать эндпоинты каталога товаров",
  "description": "GET /api/v1/products/ с фильтрацией, пагинацией, поиском через Meilisearch",
  "depends_on": ["p1_devops_001"],
  "priority": "high",
  "contracts_required": [".claude/agents/contracts/api_contracts.md"],
  "acceptance_criteria": [
    "GET /api/v1/products/ возвращает 200 с пагинацией",
    "Фильтр по категории работает",
    "Результат индексируется в Meilisearch"
  ]
}
```

---

## 🛡 Gatekeeper Protocol (Pre-Commit Checklist)

НИ ОДИН коммит не может быть предложен без прохождения всех шагов:

1. **Линтинг и типизация** — ruff + mypy (backend), vue-tsc (frontend)
2. **Целостность БД** — `alembic heads` (1 head), `alembic check` (sync OK)
3. **Зависимости** — все новые пакеты в `requirements.txt` с точной версией
4. **Тесты** — pytest для затронутых модулей; обязательно для auth/payments/delivery
5. **Frontend sync** — `frontend/stores/` синхронизированы с изменениями в `backend/app/api/v1/schemas.py`

---

## 🗺 Маппинг Gemini → Claude Code

| Gemini CLI | Claude Code | Примечание |
|---|---|---|
| `.gemini/system.md` + `GEMINI.md` + `AGENTS.md` | `CLAUDE.md` (root) | Этот файл |
| `.gemini/agents/backend-agent.md` | `backend/CLAUDE.md` | Скоупированный контекст |
| `.gemini/agents/frontend-agent.md` | `frontend/CLAUDE.md` | Скоупированный контекст |
| `.gemini/agents/devops-agent.md` | `deploy/CLAUDE.md` | Скоупированный контекст |
| `.gemini/agents/testing-agent.md` | `tests/CLAUDE.md` | Скоупированный контекст |
| `.gemini/agents/tasks/*.json` | `.claude/agents/tasks/*.json` | Идентичный формат |
| `.gemini/agents/reports/*.md` | `.claude/agents/reports/*.md` | Идентичный формат |
| `.gemini/commands/` | `.claude/commands/` | Slash-команды |
| `.gemini/settings.json` | `.claude/settings.json` | Конфиг инструментов |
| `.gemini/agents/contracts/` | `.claude/agents/contracts/` | API-контракты |
