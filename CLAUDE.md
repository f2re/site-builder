# CLAUDE.md — Точка входа Claude Code агента

> **Читай этот файл ПЕРВЫМ при каждой новой задаче.**
> Здесь — вся концепция проекта, стек, правила, агенты и точки входа.
> **Архитектурные инварианты:** [ARCHITECTURE.md](ARCHITECTURE.md)
> **DevOps детали:** [DEVOPS.md](DEVOPS.md)
> **Детальный план разработки:** [plan.md](plan.md)
> **Активные задачи агентов:** [.claude/agents/tasks/](.claude/agents/tasks/)
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

### 🏗 Infrastructure Sync Policy (Docker)
1. **Double Edit Rule**: два основных конфига:
   - **Dev**: `docker-compose.yml` (корень проекта)
   - **Prod**: `deploy/docker-compose.prod.yml`
2. **Sync Required**: любые изменения инфраструктуры **ОБЯЗАНЫ** вноситься в оба файла одновременно.
3. **Versions**: всегда фиксируй версии образов (например, `v1.36.0`), `:latest` в проде **ЗАПРЕЩЕНО**.

---

## 📁 Канонная структура проекта

Все агенты ОБЯЗАНЫ размещать файлы строго по этой структуре:

```
site-builder/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth/          {router, service, repository, schemas}.py
│   │   │       ├── users/
│   │   │       ├── products/
│   │   │       ├── categories/
│   │   │       ├── cart/
│   │   │       ├── orders/
│   │   │       ├── blog/
│   │   │       ├── delivery/      # СДЭК
│   │   │       ├── payments/      # ЮKassa
│   │   │       ├── iot/           # WebSocket + телеметрия
│   │   │       ├── admin/         # Админ-панель API
│   │   │       └── search/        # Meilisearch прокси
│   │   ├── core/
│   │   │   ├── config.py          # Settings (pydantic-settings)
│   │   │   ├── security.py        # JWT, password hashing
│   │   │   ├── dependencies.py    # FastAPI DI
│   │   │   └── exceptions.py      # HTTPException handlers
│   │   ├── db/
│   │   │   ├── base.py            # DeclarativeBase
│   │   │   ├── session.py         # async_sessionmaker
│   │   │   └── models/            # ЕДИНСТВЕННОЕ место для всех моделей
│   │   │       ├── user.py
│   │   │       ├── product.py
│   │   │       ├── category.py
│   │   │       ├── order.py
│   │   │       ├── cart.py
│   │   │       ├── blog_post.py
│   │   │       └── telemetry.py   # TimescaleDB hypertable
│   │   ├── tasks/
│   │   │   ├── celery_app.py
│   │   │   ├── notifications.py
│   │   │   ├── inventory.py
│   │   │   └── search_index.py
│   │   └── integrations/
│   │       ├── cdek.py
│   │       ├── yoomoney.py
│   │       ├── cbr_rates.py
│   │       └── meilisearch.py
│   ├── migrations/
│   │   └── versions/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── assets/css/tokens.css       # ← ЕДИНСТВЕННЫЙ источник design tokens
│   ├── components/
│   │   ├── U/                      # UI kit: UButton, UCard, UInput, UThemeToggle…
│   │   ├── shop/
│   │   ├── blog/
│   │   ├── iot/
│   │   └── admin/
│   ├── pages/
│   │   ├── index.vue
│   │   ├── shop/
│   │   ├── blog/
│   │   ├── iot/
│   │   ├── account/
│   │   └── admin/
│   ├── stores/
│   │   ├── themeStore.ts
│   │   ├── authStore.ts
│   │   ├── cartStore.ts
│   │   └── productStore.ts
│   ├── composables/
│   ├── nuxt.config.ts
│   └── Dockerfile
│
├── deploy/
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── nginx.dev.conf
│   └── docker-compose.prod.yml
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── load/                       # Locust
│   └── conftest.py
│
├── .claude/                        # ← Claude Code конфигурация
│   ├── agents/
│   │   ├── contracts/              # API-контракты между агентами
│   │   ├── tasks/                  # Активные задачи (.json)
│   │   └── reports/                # Отчёты агентов
│   ├── commands/                   # Slash-команды (/agents:plan и др.)
│   └── settings.json
│
├── docker-compose.yml
├── .gitlab-ci.yml
├── .env.example
├── CLAUDE.md                       # ← ВЫ ЗДЕСЬ
├── GEMINI.md                       # Gemini CLI (legacy)
├── ARCHITECTURE.md
├── DEVOPS.md
└── plan.md
```

---

## 🤖 Мультиагентная система — Claude Code

Ты — **ОРКЕСТРАТОР** мультиагентной системы разработки проекта WifiOBD Site.

### Обязанности оркестратора
1. Читать задачи из `.claude/agents/tasks/*.json`
2. Декомпозировать запрос пользователя на подзадачи для агентов
3. Создавать `.json`-файлы задач в `.claude/agents/tasks/` перед вызовом агента
4. Делегировать задачи агентам (оркестратор сам **НЕ ПИШЕТ** код)
5. Читать и валидировать отчёты из `.claude/agents/reports/`
6. Писать сводку в `.claude/agents/reports/orchestrator_summary.md`
7. Эскалировать блокеры пользователю

### Агенты и зоны ответственности

| Агент | Зона ответственности | Контекст |
|---|---|---|
| `orchestrator` | Координация, декомпозиция, валидация отчётов | CLAUDE.md (этот файл) |
| `devops-agent` | Docker, Nginx, GitLab CI/CD, мониторинг | `deploy/CLAUDE.md` |
| `backend-agent` | FastAPI, SQLAlchemy, Alembic, REST API, WebSocket, IoT | `backend/CLAUDE.md` |
| `cdek-agent` | СДЭК v2, ЮKassa, ЦБ РФ, Celery-задачи интеграций | `backend/CLAUDE.md` |
| `frontend-agent` | Nuxt 3, Vue 3, Pinia, UI kit, темы, PWA, Админ-панель | `frontend/CLAUDE.md` |
| `testing-agent` | pytest, интеграционные тесты, WebSocket, Locust | `tests/CLAUDE.md` |
| `security-agent` | OWASP, 152-ФЗ, аудит (READ-ONLY, код не меняет) | CLAUDE.md (root) |

### Порядок запуска агентов в фазе
```
devops-agent → backend-agent → cdek-agent → frontend-agent → testing-agent → security-agent
```

### Граф зависимостей фаз (9 фаз)

```
Фаза 1: Infrastructure Setup
  Агент: devops-agent
  Задачи: docker-compose.yml, Dockerfiles, .env.example, GitLab CI/CD skeleton
  Depends on: —
  Outputs: работающая dev-среда

Фаза 2: Backend Core
  Агент: backend-agent
  Задачи: FastAPI skeleton, DB models, Alembic init, auth endpoints
  Depends on: Фаза 1
  Outputs: /api/v1/auth/*, /api/v1/users/me

Фаза 3: Product Catalog & Blog
  Агент: backend-agent
  Задачи: products, blog posts, categories, Meilisearch indexing
  Depends on: Фаза 2
  Outputs: /api/v1/products/*, /api/v1/blog/*

Фаза 4: E-Commerce Core
  Агенты: backend-agent, cdek-agent
  Задачи: cart, orders, CDEK delivery, YooMoney payments
  Depends on: Фаза 3
  Outputs: полный checkout flow

Фаза 5: IoT Layer
  Агент: backend-agent
  Задачи: WebSocket /ws/iot/{device_id}, Redis Streams, TimescaleDB
  Depends on: Фаза 2 (auth ready)
  Outputs: IoT device telemetry pipeline

Фаза 6: Currency & Integrations
  Агент: cdek-agent
  Задачи: CBR rates, Celery beat, multi-currency prices
  Depends on: Фаза 4
  Outputs: цены в USD/EUR/CNY через ЦБ РФ

Фаза 7: Frontend
  Агент: frontend-agent
  Задачи: Nuxt 3 app, все страницы, темы, PWA
  Depends on: Фаза 3 + Фаза 4 (API-контракты готовы)
  Outputs: полнофункциональный frontend

Фаза 8: Testing
  Агент: testing-agent
  Задачи: unit tests, integration tests, WebSocket tests, Locust
  Depends on: Фаза 4 + Фаза 5 + Фаза 6
  Outputs: coverage report, Locust HTML report

Фаза 9: Security Audit & Deploy
  Агенты: security-agent, devops-agent
  Задачи: full security audit, production docker-compose, GitLab CI/CD complete
  Depends on: Фаза 8 (все тесты зелёные)
  Outputs: security report, production-ready deployment
```

**Компактный граф:**
```
Фаза1 → Фаза2 → Фаза3 → Фаза4 → Фаза6
                  Фаза3 → Фаза7
         Фаза2 → Фаза5
                  Фаза4+5+6 → Фаза8 → Фаза9
```

---

## 🔄 Рабочий цикл агента (4 фазы — ОБЯЗАТЕЛЬНЫ)

### Фаза 1 — PLAN [режим: максимальный reasoning]
**НЕ ПИШИ КОД.** Только:
- Прочитай задачу и этот файл
- Изучи затронутые файлы
- Сформулируй план в 5–10 шагах
- Опиши стратегию верификации (какие команды докажут готовность)

### Фаза 2 — IMPLEMENT
- Пиши код с учётом тестируемости
- Создавай unit-тесты параллельно с кодом (не в конце)

### Фаза 3 — VERIFY [режим: максимальный reasoning]
- Запусти **ВСЕ** команды из Tooling ниже
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
npm install --quiet
npm run lint

# База данных:
alembic check && alembic heads

# Тесты:
pytest tests/ -x -v
```

---

## ✅ Definition of Done (DoD)

Задача считается выполненной ТОЛЬКО при выполнении всех пунктов:

- [ ] `ruff check app/` → **0 errors**
- [ ] `mypy app/ --ignore-missing-imports` → **Success: no issues found**
- [ ] `npm run lint` → **no errors** (vue-tsc)
- [ ] `pytest tests/` → **all green**
- [ ] `alembic check` → **OK** (модели совпадают с миграциями)
- [ ] `alembic heads` → **ровно 1 head**
- [ ] Отчёт агента написан в `.claude/agents/reports/<domain>/<task_id>.md`

---

## 📐 Контракты разработки

### 🌐 API Path & BaseURL Policy
1. `apiBase` в `runtimeConfig` **ОБЯЗАН** включать версию (например, `/api/v1`).
2. **ЗАПРЕЩЕНО** вручную добавлять `/api/v1` в пути при использовании `useFetch` с `baseURL: apiBase`.
3. Все пути в композаблах начинаются с `/` относительно `apiBase` (например, `/products`).

### 🔐 Auth & Profile Flow Contract
1. Любой эндпоинт авторизации **ОБЯЗАН** возвращать полную `UserResponse` в поле `user` вместе с токенами.
2. В frontend-composables использовать строго `accessToken` (не `token`, не `jwt`).
3. При обновлении `email` бэкенд **ОБЯЗАН** пересчитывать `email_hash` (blind index).

### 📱 UI Parity Rule
Любая навигационная ссылка в мобильном меню **ДОЛЖНА** иметь аналог в десктопной версии.

### 🏷️ Frontend Naming Conventions
- Для IoT/Телеметрии: `IoTDevice` (в `useIoT.ts`)
- Для Магазина/Прошивок: `FirmwareDevice` (в `firmwareStore.ts`)
- Общие типы (User, Order): единственные в `stores/` или `composables/`

### 📊 IoT / Телеметрия Contract
- Таблица `telemetry` **MUST** быть TimescaleDB hypertable (`chunk_time_interval = '1 day'`)
- WebSocket эндпоинт: `ws://host/ws/iot/{device_id}`
- Данные: Redis Streams → Celery consumer → TimescaleDB
- Дашборд агрегирует через `time_bucket` (не raw SELECT)
- Retention policy: 90 дней (`TELEMETRY_RETENTION_DAYS` в .env)

### 🎨 Design Token Contract
```
frontend/assets/css/tokens.css   ← ЕДИНСТВЕННЫЙ источник всех design tokens
frontend/stores/themeStore.ts    ← ЕДИНСТВЕННЫЙ источник состояния темы
```
- `themeStore.toggle()` **MUST** обновлять `document.documentElement.dataset.theme`
- Тема **MUST** сохраняться в `localStorage` key `theme`
- SSR: читать из cookie `theme` (httpOnly=false)
- Тема по умолчанию: `dark`
- Контраст текста: ≥ 4.5:1 (WCAG 2.1 AA) в обеих темах

---

## 🚦 MUST
- Проходить все 4 фазы в каждой задаче
- Запускать tooling-команды перед каждым коммитом
- Новый endpoint → только в `backend/app/api/v1/<feature>/` со структурой `router/service/repository/schemas`
- Новые зависимости → только с точной версией в `requirements.txt`; проверить `pip install -r requirements.txt`
- Изменения инфраструктуры → в оба файла одновременно: `docker-compose.yml` + `deploy/docker-compose.prod.yml`
- Docker images → только фиксированные версии (например, `v1.36.0`)
- Писать отчёт в `.claude/agents/reports/<domain>/<task_id>.md` по шаблону ниже
- Все сервисы, изменяющие данные (POST/PUT/PATCH/DELETE) **ОБЯЗАНЫ** вызывать `await session.commit()`
- Перед валидацией через Pydantic объект **ДОЛЖЕН** быть загружен со всеми связями (`selectinload` или `refresh`)
- В Celery для async: **ТОЛЬКО** `asyncio.run()` (не `get_event_loop()`)
- Для интеграционных тестов бэкенда: `fakeredis[lua]>=2.20.0`
- Frontend пакеты: `npm install --legacy-peer-deps` (критично для TipTap)

## 🚫 MUST NOT
- Коммитить `.env` или любые секреты
- Хардкодить цвета/отступы в `.vue` (только CSS-переменные из `tokens.css`)
- Менять `backend/app/core/` без unit-тестов
- Использовать **GitHub Actions** (только GitLab CI/CD)
- Использовать **Docker Hub** (только GitLab Container Registry)
- Использовать `:latest` в docker images
- Дублировать типы: `app/models/`, `app/schemas/`, `app/services/` вне `api/v1/<feature>/`
- Вручную добавлять `/api/v1` в пути при использовании `useFetch` с `baseURL: apiBase`
- Использовать имя `Device` напрямую (конфликт Nuxt auto-import)
- Запускать фазу до завершения всех её зависимостей

---

## 🛡 Gatekeeper Protocol (Pre-Commit Checklist)

НИ ОДИН коммит не предлагается без прохождения всех пунктов:

1. **Линтинг и типизация**:
   - `ruff check app/ --fix && ruff check app/` → 0 errors
   - `mypy app/ --ignore-missing-imports` → no issues
   - `npm run lint` → SUCCESS
2. **Целостность БД**:
   - `alembic heads` → ровно ONE head
   - `alembic check` → models match migrations
   - ENUM в миграциях: `IF NOT EXISTS` в `pg_type`
3. **Зависимости**:
   - Все новые библиотеки с точной версией в `requirements.txt`
   - `pip install -r requirements.txt --quiet` без конфликтов
4. **Тесты**:
   - `pytest` для затронутого функционала
   - Критические пути (оплата, доставка, auth) — обязательны
5. **Frontend Sync**:
   - `frontend/stores/` актуальны относительно `backend/app/api/v1/schemas.py`

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

---

## 🌳 Git Commit Rules

1. **Язык**: сообщения коммитов на **русском языке**
2. **Эмодзи**: начинать с эмодзи (✨ фичи, 🐛 баги, ♻️ рефакторинг, 🚀 CI/CD, 📝 документация, 🔒 безопасность)
3. **Тело коммита**: детальное описание — что сделано, почему, какие компоненты затронуты

**Пример:**
```
✨ Добавлен функционал корзины с Redis Lua

- Атомарное резервирование товаров через Lua-скрипт (предотвращение race condition)
- CartService с поддержкой гостевых (session_id) и авторизованных (user_id) корзин
- OrderService: валидация стока в Redis перед сохранением в БД
```

---

## ⌨️ Slash-команды Claude Code

```
/agents:plan <описание задачи>   — декомпозировать задачу, создать JSON в .claude/agents/tasks/
/agents:run <agent> <task_id>    — запустить агента с задачей
/agents:verify                   — запустить полный DoD checklist
/agents:status                   — показать статус всех активных задач
```

См. реализацию команд: [.claude/commands/](.claude/commands/)

---

## 📊 Формат файла задачи агента

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

Файлы задач: `.claude/agents/tasks/<phase>_<agent>_<id>.json`
Отчёты агентов: `.claude/agents/reports/<domain>/<task_id>.md`

---

> **Правило оркестратора:** НИКОГДА не писать код самому — только делегировать агентам.
> ВСЕГДА создавать файл задачи перед вызовом агента.
> НИКОГДА не запускать фазу до завершения всех её зависимостей.
