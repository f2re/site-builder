# ORCHESTRATOR.md — Полный контекст оркестратора

> Этот файл читается ПОСЛЕ CLAUDE.md когда нужны детали.
> Основной policy-шлюз: [AGENTS.md](../AGENTS.md)
> Точка входа: [CLAUDE.md](../CLAUDE.md)

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
1. **Double Edit Rule**: `docker-compose.yml` (dev) + `deploy/docker-compose.prod.yml` (prod)
2. Любые изменения инфраструктуры **ОБЯЗАНЫ** вноситься в оба файла одновременно
3. Всегда фиксируй версии образов (например, `v1.36.0`), `:latest` в проде **ЗАПРЕЩЕНО**

---

## 📁 Канонная структура проекта

Все агенты ОБЯЗАНЫ размещать файлы строго по этой структуре:

```
site-builder/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── auth/          {router, service, repository, schemas}.py
│   │   │   ├── users/
│   │   │   ├── products/
│   │   │   ├── categories/
│   │   │   ├── cart/
│   │   │   ├── orders/
│   │   │   ├── blog/
│   │   │   ├── delivery/      # СДЭК
│   │   │   ├── payments/      # ЮKassa
│   │   │   ├── iot/           # WebSocket + телеметрия
│   │   │   ├── admin/
│   │   │   └── search/        # Meilisearch прокси
│   │   ├── core/
│   │   │   ├── config.py      # Settings (pydantic-settings)
│   │   │   ├── security.py    # JWT, password hashing
│   │   │   ├── dependencies.py
│   │   │   └── exceptions.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── models/        # ЕДИНСТВЕННОЕ место для всех моделей
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
│   ├── migrations/versions/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── assets/css/tokens.css   # ← ЕДИНСТВЕННЫЙ источник design tokens
│   ├── components/
│   │   ├── U/                  # UI kit: UButton, UCard, UInput...
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
├── .claude/
│   ├── agents/
│   │   ├── contracts/          # API-контракты между агентами
│   │   ├── tasks/              # Активные задачи (.json)
│   │   └── reports/            # Отчёты агентов
│   ├── commands/               # Slash-команды
│   ├── hooks/                  # Middleware: pre_completion, loop_detector, local_context
│   ├── logs/                   # Логи сессий и loop-state
│   ├── ORCHESTRATOR.md         # ← ВЫ ЗДЕСЬ
│   └── settings.json
```

---

## 📊 Граф зависимостей фаз (9 фаз)

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

## 📋 Формат файла задачи агента

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

Файлы: `.claude/agents/tasks/<phase>_<agent>_<id>.json`
Отчёты: `.claude/agents/reports/<domain>/<task_id>.md`

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
- **ЗАПРЕЩЕНО** имя `Device` напрямую (конфликт Nuxt auto-import)

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

## E2E Автоматизация — Протокол агентов

### Задачи фазы E2E (Phase 8, подфаза e2e)

| task_id | Агент | Зависит от | Описание |
|---|---|---|---|
| `p8_e2e_backend_001` | backend-agent | p2, p3, p4 | Создать `backend/scripts/seed_e2e.py` |
| `p8_e2e_frontend_001` | frontend-agent | p7 | Расставить все `data-testid` по контракту |
| `p8_e2e_testing_001` | testing-agent | p8_e2e_backend_001 + p8_e2e_frontend_001 | Запустить E2E, зафиксировать результат |

### Порядок запуска
```
backend-agent p8_e2e_backend_001   (параллельно с frontend)
frontend-agent p8_e2e_frontend_001 (параллельно с backend)
          ↓ оба завершены
testing-agent p8_e2e_testing_001   (запускает тесты, пишет отчёт)
```

### Что делает testing-agent (p8_e2e_testing_001)
1. Проверяет доступность всех сервисов (порты 3000, 8000, 7700)
2. Запускает `python -m scripts.seed_e2e` для засева данных
3. Устанавливает зависимости: `pip install pytest playwright` + `playwright install chromium`
4. Прогоняет `pytest tests/e2e/ -v --headed -s` с логом в `.claude/logs/e2e.log`
5. Анализирует каждое падение: тест-код / отсутствующий testid / API / seed-данные
6. Исправляет проблемы в тест-коде (conftest, fixture)
7. Эскалирует блокеры через отчёт

### Контракт data-testid
Полный реестр: `.claude/agents/contracts/e2e_testid_contract.md`

### Итоговый отчёт
`testing-agent` пишет отчёт в: `.claude/agents/reports/testing/p8_e2e_testing_001.md`
Формат — таблица PASS/FAIL по каждому test_0*.py + список блокеров с ответственным агентом.

---

## 🌳 Git Commit Rules

1. **Язык**: сообщения коммитов на **русском языке**
2. **Эмодзи**: начинать с эмодзи (✨ фичи, 🐛 баги, ♻️ рефакторинг, 🚀 CI/CD, 📝 документация, 🔒 безопасность)
3. **Тело коммита**: детальное описание — что сделано, почему, какие компоненты затронуты

**Пример:**
```
✨ Добавлен функционал корзины с Redis Lua

- Атомарное резервирование товаров через Lua-скрипт (race condition prevention)
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

Реализация команд: [.claude/commands/](.claude/commands/)

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
6. **Middleware**:
   - `python .claude/hooks/pre_completion.py <task_id>` → DoD пройден

---

## 🔒 Специальные правила

- Все сервисы POST/PUT/PATCH/DELETE **ОБЯЗАНЫ** вызывать `await session.commit()`
- Перед валидацией Pydantic объект **ДОЛЖЕН** быть загружен со всеми связями (`selectinload` или `refresh`)
- В Celery для async: **ТОЛЬКО** `asyncio.run()` (не `get_event_loop()`)
- Для интеграционных тестов бэкенда: `fakeredis[lua]>=2.20.0`
- Frontend пакеты: `npm install --legacy-peer-deps` (критично для TipTap)
