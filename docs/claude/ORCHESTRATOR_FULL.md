# ORCHESTRATOR_FULL.md — Полная документация оркестратора (legacy)

> Этот файл — архивная копия полного CLAUDE.md до декомпозиции (2026-03-06).
> Актуальные правки вносить в: CLAUDE.md (карта) + docs/claude/agents_system.md + docs/claude/contracts.md + docs/claude/e2e_protocol.md

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
│   │   │   ├── delivery/
│   │   │   ├── payments/
│   │   │   ├── iot/
│   │   │   ├── admin/
│   │   │   └── search/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── dependencies.py
│   │   │   └── exceptions.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── models/
│   │   ├── tasks/
│   │   └── integrations/
│   ├── migrations/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── assets/css/tokens.css
│   ├── components/U/
│   ├── pages/
│   ├── stores/
│   ├── composables/
│   ├── nuxt.config.ts
│   └── Dockerfile
├── deploy/
│   ├── nginx/
│   └── docker-compose.prod.yml
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── load/
│   └── conftest.py
├── .claude/
│   ├── agents/
│   │   ├── contracts/
│   │   ├── tasks/
│   │   └── reports/
│   ├── commands/
│   └── settings.json
├── scripts/agents/
│   ├── verify_dod.sh
│   └── context_snapshot.sh
├── docs/claude/
│   ├── agents_system.md
│   ├── contracts.md
│   ├── e2e_protocol.md
│   └── ORCHESTRATOR_FULL.md
└── docs/examples/
```

---

> Для актуальной оркестрации смотри: CLAUDE.md + docs/claude/agents_system.md
