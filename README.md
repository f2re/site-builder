# 🏎️ WifiOBD Site Builder — E-Commerce Platform

> Современный интернет-магазин (E-Commerce + Blog + IoT) на базе **FastAPI + Vue 3 + Nuxt 3**.
> Разрабатывается мультиагентной системой ИИ на базе **Gemini CLI** с архитектурой Clean Architecture.

---

## 📐 Архитектура и стек технологий

| Слой | Технологии |
|------|-----------|
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy 2.x (async), Alembic, PostgreSQL 16 |
| **Frontend** | Vue 3, Nuxt 3, Pinia, TypeScript (strict), vee-validate + zod |
| **Кэш / Очереди** | Redis 7, Celery + Redis broker |
| **Интеграции** | CDEK v2 API, YooMoney (HMAC-SHA256 webhook) |
| **Инфраструктура** | Docker Compose, Nginx, Prometheus, Grafana |
| **ИИ-система** | Gemini CLI (`gemini-3.1-pro-preview`), 6 специализированных агентов |

**Принципы UI/UX (frontend):** Mobile-First · Race-Style Design · WCAG 2.1 AA · Core Web Vitals (LCP < 2.5s)

---

## 🤖 Мультиагентная система (Gemini CLI)

Проект управляется системой специализированных ИИ-агентов. Каждый агент имеет строгую зону ответственности и набор coding contracts.

### Агенты

| Агент | Зона ответственности | Режим |
|-------|---------------------|-------|
| `orchestrator` | Делегирует задачи, проверяет отчёты агентов | read/write |
| `backend-agent` | FastAPI, SQLAlchemy, Pydantic, REST API | read/write |
| `frontend-agent` | Vue 3, Nuxt 3, Pinia, TypeScript, UI/UX | read/write |
| `security-agent` | OWASP аудит, 152-ФЗ, GDPR | **только чтение** |
| `testing-agent` | pytest, respx, Locust | read/write |
| `cdek-agent` | CDEK v2 API, YooMoney интеграция | read/write |
| `devops-agent` | Docker, Nginx, CI/CD, Prometheus | read/write |

Определения агентов: [`.gemini/agents/`](.gemini/agents/)
Конфигурация Gemini CLI: [`.gemini/settings.json`](.gemini/settings.json) (`experimental.enableAgents: true`, модель `gemini-3.1-pro-preview`)

---

## 🚀 Быстрый старт разработки

### 1. Требования

- [Gemini CLI](https://github.com/google-gemini/gemini-cli) установлен глобально
- Docker + Docker Compose
- Node.js 20+ (для frontend-разработки)
- Python 3.12+ (для backend-разработки)

### 2. Клонирование и запуск

```bash
git clone https://github.com/f2re/site-builder.git
cd site-builder

# Запуск всей инфраструктуры
docker-compose up --build

# Или только отдельные сервисы
docker-compose up postgres redis        # только БД и кэш
docker-compose up backend               # FastAPI сервер
docker-compose up frontend              # Nuxt 3 dev сервер
```

### 3. Первый запуск Gemini CLI в проекте

```bash
# В корне репозитория — Gemini подхватит .gemini/settings.json автоматически
gemini

# Убедиться, что агенты активны (в чате Gemini CLI):
/agents:status
```

---

## 🛠️ Работа с агентами

### Способ 1 — Прямой вызов агента в чате

Откройте Gemini CLI в корне проекта и обращайтесь к агенту через `@`:

```
@orchestrator создай план реализации страницы корзины
@frontend-agent добавь компонент карточки товара с анимацией
@backend-agent реализуй эндпоинт GET /api/v1/products с пагинацией
@security-agent проведи аудит модуля аутентификации
```

> **Важно:** `orchestrator` НИКОГДА не пишет код сам — он делегирует задачи другим агентам и проверяет отчёты.

### Способ 2 — Система задач (слэш-команды)

Команды доступны в Gemini CLI через `/`:

```bash
# Поставить задачу в очередь
/agents:start frontend-agent добавить мобильную навигацию
/agents:start backend-agent реализовать фильтрацию товаров по цене

# Запустить первую pending-задачу из очереди
/agents:run

# Запустить конкретную задачу по ID
/agents:run 20260226_143000_frontend

# Посмотреть статус всех задач и агентов
/agents:status
```

#### Формат task_id
```
YYYYMMDD_HHMMSS_<agent-short-name>
Пример: 20260226_143000_frontend
```

#### Жизненный цикл задачи
```
pending → running → done
                 ↘ blocked  (требует эскалации к разработчику)
```

Файлы задач хранятся в `.gemini/agents/tasks/*.json`, отчёты агентов — в `.gemini/agents/reports/<domain>/<task_id>.md`.

### Способ 3 — Domain-команды (быстрый доступ)

```bash
/shop:frontend добавить страницу избранного
/shop:backend реализовать поиск по каталогу
/shop:review проверить последние изменения в PR
```

---

## 📋 Структура задачи (`.gemini/agents/tasks/<task_id>.json`)

```json
{
  "task_id": "20260226_143000_frontend",
  "agent": "frontend-agent",
  "status": "pending",
  "priority": "normal",
  "description": "Добавить мобильную навигацию (bottom nav bar)",
  "created_at": "2026-02-26T14:30:00Z",
  "dependencies": [],
  "report_path": ".gemini/agents/reports/frontend/20260226_143000_frontend.md"
}
```

---

## 📝 Структура отчёта агента

Каждый агент **обязан** включить все секции в свой отчёт, иначе orchestrator отклонит задачу:

```markdown
## Status        — DONE / BLOCKED
## Completed     — список реализованных файлов
## Artifacts     — созданные/изменённые маршруты, компоненты, сторы
## Contracts Verified — какие coding + API контракты проверены
## Accessibility — результат axe-core (только frontend-agent)
## Performance   — Lighthouse scores mobile (только frontend-agent)
## Next          — задачи-продолжения
## Blockers      — проблемы для эскалации оркестратору
```

---

## 🔗 Ключевые файлы проекта

| Файл / Директория | Назначение |
|-------------------|-----------|
| [`plan.md`](plan.md) | Техническое задание и план разработки |
| [`.gemini/agents/`](.gemini/agents/) | Определения всех агентов (контракты, workflow) |
| [`.gemini/agents/contracts/api_contracts.md`](.gemini/agents/contracts/api_contracts.md) | Спецификации API (читать ПЕРВЫМ перед любой задачей) |
| [`.gemini/commands/agents/`](.gemini/commands/agents/) | Слэш-команды: `start`, `run`, `status` |
| [`.gemini/commands/shop/`](.gemini/commands/shop/) | Domain-команды: `frontend`, `backend`, `review` |
| [`.gemini/settings.json`](.gemini/settings.json) | Конфигурация Gemini CLI (модель, агенты, политики) |
| [`.gemini/system.md`](.gemini/system.md) | Системный промпт оркестратора |
| [`.gemini/policies/`](.gemini/policies/) | Политики безопасности и ограничения агентов |

---

## ⚡ Полезные команды для разработки

```bash
# Frontend (Nuxt 3)
npm run dev           # dev-сервер с HMR
npm run build         # production build
npm run lint          # ESLint + Vue rules
npm run type-check    # vue-tsc --noEmit
npx nuxt analyze      # анализ бандла

# Backend (FastAPI)
uvicorn app.main:app --reload   # dev-сервер
ruff check .                    # линтер
mypy .                          # type-check

# Тесты
pytest -v                       # все тесты
pytest tests/unit/              # только unit
pytest tests/integration/       # только integration

# Инфраструктура
docker-compose ps               # статус контейнеров
docker-compose logs -f backend  # логи конкретного сервиса
docker-compose down -v          # остановить + удалить volumes
```

---

## 🏗️ Принципы кодовой базы

- **Backend:** Repository pattern, Dependency Injection (`Depends()`), async SQLAlchemy, типизированные Pydantic схемы, `tenacity` retry для внешних API
- **Frontend:** Composables для всех API-вызовов, Pinia stores для состояния, zod-валидация форм, NO hardcoded URLs (`useRuntimeConfig()`)
- **Безопасность:** без захардкоженных секретов, JWT с refresh rotation, HMAC-SHA256 для YooMoney webhooks, шифрование персональных данных (152-ФЗ)
- **UI/UX:** Mobile-First, CSS custom properties (design tokens), micro-interactions на каждом элементе, skeleton loaders, toast-уведомления, WCAG 2.1 AA
