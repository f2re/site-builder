# agents_system.md — Система агентов, фазы и зависимости

> Часть документации оркестратора. Точка входа: [CLAUDE.md](../../CLAUDE.md)

---

## Агенты и зоны ответственности

| Агент | Зона ответственности | Контекст |
|---|---|---|
| `orchestrator` | Координация, декомпозиция, валидация отчётов | CLAUDE.md |
| `devops-agent` | Docker, Nginx, GitLab CI/CD, мониторинг | `deploy/CLAUDE.md` |
| `backend-agent` | FastAPI, SQLAlchemy, Alembic, REST API, WebSocket, IoT | `backend/CLAUDE.md` |
| `cdek-agent` | СДЭК v2, ЮKassa, ЦБ РФ, Celery-задачи интеграций | `backend/CLAUDE.md` |
| `frontend-agent` | Nuxt 3, Vue 3, Pinia, UI kit, темы, PWA, Админ-панель | `frontend/CLAUDE.md` |
| `testing-agent` | pytest, интеграционные тесты, WebSocket, Locust | `tests/CLAUDE.md` |
| `security-agent` | OWASP, 152-ФЗ, аудит (READ-ONLY, код не меняет) | CLAUDE.md |

---

## Порядок запуска агентов в фазе
```
devops-agent → backend-agent → cdek-agent → frontend-agent → testing-agent → security-agent
```

---

## Граф зависимостей фаз (9 фаз)

### Фаза 1: Infrastructure Setup
- **Агент:** devops-agent
- **Задачи:** docker-compose.yml, Dockerfiles, .env.example, GitLab CI/CD skeleton
- **Depends on:** —
- **Outputs:** работающая dev-среда

### Фаза 2: Backend Core
- **Агент:** backend-agent
- **Задачи:** FastAPI skeleton, DB models, Alembic init, auth endpoints
- **Depends on:** Фаза 1
- **Outputs:** /api/v1/auth/*, /api/v1/users/me

### Фаза 3: Product Catalog & Blog
- **Агент:** backend-agent
- **Задачи:** products, blog posts, categories, Meilisearch indexing
- **Depends on:** Фаза 2
- **Outputs:** /api/v1/products/*, /api/v1/blog/*

### Фаза 4: E-Commerce Core
- **Агенты:** backend-agent, cdek-agent
- **Задачи:** cart, orders, CDEK delivery, YooMoney payments
- **Depends on:** Фаза 3
- **Outputs:** полный checkout flow

### Фаза 5: IoT Layer
- **Агент:** backend-agent
- **Задачи:** WebSocket /ws/iot/{device_id}, Redis Streams, TimescaleDB
- **Depends on:** Фаза 2 (auth ready)
- **Outputs:** IoT device telemetry pipeline

### Фаза 6: Currency & Integrations
- **Агент:** cdek-agent
- **Задачи:** CBR rates, Celery beat, multi-currency prices
- **Depends on:** Фаза 4
- **Outputs:** цены в USD/EUR/CNY через ЦБ РФ

### Фаза 7: Frontend
- **Агент:** frontend-agent
- **Задачи:** Nuxt 3 app, все страницы, темы, PWA
- **Depends on:** Фаза 3 + Фаза 4 (API-контракты готовы)
- **Outputs:** полнофункциональный frontend

### Фаза 8: Testing
- **Агент:** testing-agent
- **Задачи:** unit tests, integration tests, WebSocket tests, Locust
- **Depends on:** Фаза 4 + Фаза 5 + Фаза 6
- **Outputs:** coverage report, Locust HTML report

### Фаза 9: Security Audit & Deploy
- **Агенты:** security-agent, devops-agent
- **Задачи:** full security audit, production docker-compose, GitLab CI/CD complete
- **Depends on:** Фаза 8 (все тесты зелёные)
- **Outputs:** security report, production-ready deployment

---

## Компактный граф

```
Фаза1 → Фаза2 → Фаза3 → Фаза4 → Фаза6
                  Фаза3 → Фаза7
         Фаза2 → Фаза5
                  Фаза4+5+6 → Фаза8 → Фаза9
```

---

## Формат файла задачи агента

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
