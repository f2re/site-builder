# GEMINI.md — Точка входа ИИ-агента

> **Читай этот файл ПЕРВЫМ.** Здесь — вся концепция проекта, стек, правила и точки входа для работы.
> Детальный план разработки: [plan.md](plan.md)
> Текущий спринт / активные задачи: [.gemini/agents/tasks/](.gemini/agents/tasks/)

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
- **MinIO** — хранилище медиафайлов (S3-совместимое, self-hosted)

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
- **Monitoring**: Prometheus + Grafana + Loki + Promtail (prod-профиль)
- Секреты: `.env` (в git не коммитить), шаблон: `.env.example`

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
│   │       ├── meilisearch.py
│   │       └── minio.py
│   ├── migrations/
│   │   └── versions/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── assets/css/tokens.css       # ← ЕДИНСТВЕННЫЙ источник design tokens
│   ├── components/
│   │   ├── U/                      # UI kit: UButton, UCard, UInput, UThemeToggle…
│   │   ├── shop/                   # ProductCard, CartItem, OrderStatus…
│   │   ├── blog/                   # PostCard, PostContent…
│   │   ├── iot/                    # TelemetryChart, DeviceStatus…
│   │   └── admin/                  # AdminTable, AdminForm…
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
│   │   ├── nginx.conf              # prod
│   │   └── nginx.dev.conf          # dev
│   ├── docker-compose.prod.yml
│   └── monitoring/
│       ├── prometheus.yml
│       ├── loki.yml
│       └── promtail.yml
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── load/                       # Locust
│   └── conftest.py
│
├── .gemini/
│   ├── agents/
│   │   ├── orchestrator.md         # Агент-координатор
│   │   ├── backend-agent.md
│   │   ├── frontend-agent.md
│   │   ├── devops-agent.md
│   │   ├── testing-agent.md
│   │   ├── security-agent.md
│   │   ├── cdek-agent.md
│   │   ├── contracts/              # API-контракты между агентами
│   │   ├── tasks/                  # Активные задачи (.json)
│   │   └── reports/                # Отчёты агентов
│   ├── commands/                   # Slash-команды (/agents:plan и др.)
│   ├── policies/                   # TOML-политики агентов
│   ├── settings.json
│   └── system.md                   # Системный промпт оркестратора
│
├── docker-compose.yml              # Dev: все сервисы
├── .gitlab-ci.yml
├── .env.example
├── GEMINI.md                       # ← ВЫ ЗДЕСЬ
├── DEVOPS.md
├── CHANGELOG.md
└── plan.md                         # Детальный план по фазам
```

---

## 📐 Контракты разработки (обязательны для всех агентов)

### Общие правила
1. Все эндпоинты **MUST** иметь Pydantic-схемы (отдельные Request + Response)
2. Все сервисы **MUST** принимать зависимости через `Depends` (DI)
3. Все внешние API-вызовы **MUST** иметь retry через `tenacity` (3 попытки, exponential backoff)
4. Все репозитории **MUST** использовать параметризованные запросы (no raw SQL)
5. Каждый агент **MUST** писать отчёт в `.gemini/agents/reports/<domain>/<task_id>.md`
6. **ЗАПРЕЩЕНО**: использовать GitHub Actions — только GitLab CI/CD
7. **ЗАПРЕЩЕНО**: использовать Docker Hub — только GitLab Container Registry
8. **ЗАПРЕЩЕНО**: хардкодить цвета в `.vue`-компонентах — только CSS-переменные из `tokens.css`
9. Модели SQLAlchemy **MUST** жить только в `backend/app/db/models/`
10. Нет дублирования: **ЗАПРЕЩЕНЫ** top-level `app/models/`, `app/schemas/`, `app/services/`

### Feature-First структура backend
Каждая фича в `backend/app/api/v1/{feature}/` **MUST** содержать:
- `router.py` — маршруты FastAPI
- `service.py` — бизнес-логика (DI-ready)
- `repository.py` — CRUD через SQLAlchemy async
- `schemas.py` — Pydantic Request/Response модели

Кросс-доменная логика → `app/core/` или `app/tasks/`.

---

## 🎨 Design Token Contract (Frontend)

```
frontend/assets/css/tokens.css   ← ЕДИНСТВЕННЫЙ источник всех дизайн-токенов
frontend/stores/themeStore.ts    ← ЕДИНСТВЕННЫЙ источник состояния темы
frontend/components/U/UThemeToggle.vue ← глобальная кнопка переключения темы
```

- `themeStore.toggle()` **MUST** обновлять `document.documentElement.dataset.theme`
- Тема **MUST** сохраняться в `localStorage` key `theme`
- SSR: читать тему из cookie `theme` (httpOnly=false) во избежание hydration mismatch
- Тема по умолчанию: `dark`
- Контраст текста: ≥ 4.5:1 (WCAG 2.1 AA) в обеих темах

---

## 📊 IoT / Телеметрия Contract

- Таблица `telemetry` **MUST** быть TimescaleDB hypertable (chunk_time_interval = '1 day')
- WebSocket эндпоинт: `ws://host/ws/iot/{device_id}`
- Данные пишутся через Redis Streams → Celery consumer → TimescaleDB
- Дашборд агрегирует данные через TimescaleDB time_bucket (не raw SELECT)
- Retention policy: 90 дней (настраивается через `TELEMETRY_RETENTION_DAYS` в .env)

---

## 🧹 Проверка кода (Linting & Type Checking)

**ОБЯЗАТЕЛЬНОЕ ТРЕБОВАНИЕ:** Все ИИ-агенты **ОБЯЗАНЫ** успешно выполнить локальную проверку линтерами перед каждым коммитом. Коммит с ошибками линтинга считается бракованным.

**Backend (Python):**
```bash
# Выполнять из папки /backend
ruff check app/ --fix
ruff check app/
mypy app/ --ignore-missing-imports
```
*(Успех: вывод "All checks passed!" и "Success: no issues found")*

**Frontend (Vue/Nuxt 3):**
```bash
# Выполнять из папки /frontend
npm install --quiet
npm run lint # или ./node_modules/.bin/vue-tsc --noEmit
```
*(Успех: пустой вывод или SUCCESS от vue-tsc)*

---

## 🌳 Правила работы с Git (Git Commits)

При создании коммитов и работе с репозиторием обязательно соблюдайте следующие правила:
1. **Язык**: Сообщения коммитов **MUST** быть на **русском языке**.
2. **Эмодзи**: Начинайте заголовок коммита с подходящего эмодзи (например: ✨ для новых фич, 🐛 для багов, ♻️ для рефакторинга, 🚀 для CI/CD и деплоя, 📝 для документации, 🔒 для безопасности).
3. **Развернутый комментарий**: В теле коммита (после пустой строки от заголовка) **MUST** содержаться детальное и понятное для разработчиков описание внесенных изменений (что именно было сделано, почему выбрано такое техническое решение, какие компоненты/модули затронуты).

**Пример правильного коммита:**
```text
✨ Добавлен функционал корзины с Redis Lua

- Реализовано атомарное резервирование товаров через Lua-скрипт для предотвращения race condition.
- Создан CartService с поддержкой гостевых (session_id) и авторизованных (user_id) корзин.
- Обновлен OrderService: перед сохранением в БД происходит валидация стока в Redis.
```

---

## 🤖 Агенты — вызов и порядок

### Доступные агенты
| Агент | Зона ответственности |
|---|---|
| `@orchestrator` | Координация, декомпозиция задач, валидация отчётов |
| `@backend-agent` | FastAPI, SQLAlchemy, Alembic, REST API, WebSocket |
| `@cdek-agent` | СДЭК, ЮKassa, ЦБ РФ, Celery-задачи интеграций |
| `@frontend-agent` | Nuxt 3, Vue 3, Pinia, UI kit, темы, PWA |
| `@devops-agent` | Docker, Nginx, GitLab CI/CD, мониторинг |
| `@testing-agent` | pytest, интеграционные тесты, Locust |
| `@security-agent` | OWASP, 152-ФЗ, audit (READ-ONLY) |

### Порядок запуска в фазе
```
devops-agent → backend-agent → cdek-agent → frontend-agent → testing-agent → security-agent
```

Полный граф зависимостей фаз: см. [orchestrator.md](.gemini/agents/orchestrator.md)

### Точка входа для новой задачи
```
/agents:plan <описание задачи>
```
Оркестратор декомпозирует задачу, создаёт `.json`-файлы в `.gemini/agents/tasks/` и строит план выполнения.

---

## 📋 Формат отчёта агента

Каждый отчёт **ОБЯЗАН** содержать все секции:

```markdown
## Status: DONE | IN_PROGRESS | BLOCKED
## Completed:
- список выполненного
## Artifacts:
- backend/app/api/v1/products/router.py
## Contracts Verified:
- Pydantic schemas: ✅
- DI via Depends: ✅
## Next:
- передать frontend-agent: API контракт /api/v1/products готов
## Blockers:
- нет
```
