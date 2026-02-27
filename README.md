# 🚗 WifiOBD Site — Интернет-магазин + IoT-дашборд

> Современный интернет-магазин автомобильной электроники (OBD-адаптеры, телематика)
> с **IoT-дашбордом онлайн-телеметрии**, блогом и полноценной админ-панелью.
> Стек: **FastAPI + Nuxt 3**, self-hosted, CI/CD через GitLab, разработка управляется мультиагентной системой **Gemini CLI**.

---

## 📊 Статус разработки

| Этап | Название | Статус |
|--------|---------|--------|
| 1 | Инфраструктура (Docker, JWT, логи, БД, Redis) | ✅ Готов |
| 2 | Каталог товаров + инвентарь (products, categories, variants) | ✅ Готов |
| 3 | Корзина, заказы, YooMoney, СДЭК | ✅ Готов |
| 4 | Блог + медиа (TipTap + SEO) | ✅ Готов |
| 5 | Админ-панель (CRUD товары/заказы/блог/пользователи) | ✅ Готов |
| 6 | Личный кабинет (профиль, заказы, устройства, WebSocket) | ✅ Готов |
| 7 | Безопасность (152-ФЗ, bleach, HMAC, rate limiting) | ✅ Готов |
| 8 | IoT / OBD2 (телеметрия Redis Stream, WebSocket, TimescaleDB) | ✅ Готов |
| 9 | CI/CD (GitLab Runner, Docker Registry, SSH-деплой) | ✅ Готов |
| 10 | SEO: sitemap, Schema.org, canonical, CWV | 🔄 В работе |
| 11 | Meilisearch — подключение к backend + индексация | 🔄 В работе |
| 12 | Тесты (pytest, Locust) + Lighthouse CI | ⏳ Ожидает |

Полный план с техническими деталями: [→ `plan.md`](plan.md)

---

## 📦 Стек технологий

| Слой | Технологии | Назначение |
|------|-----------|-----------|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.x async, Alembic | REST API, асинхронное ядро |
| **БД** | PostgreSQL 16 + **TimescaleDB** | Основная БД + IoT hypertable для телеметрии |
| **Кэш / Очереди** | Redis 7, Celery (worker+beat) | Кэш, резерв остатков, IoT Streams, фоновые задачи |
| **Frontend** | Nuxt 3, Vue 3 Composition API, TypeScript, Pinia | SSR, PWA, i18n (ru/en) |
| **Медиа** | Локальное хранилище `/media` через Nginx + Celery WebP | Фото/видео товаров и блога |
| **Поиск** | Meilisearch | Полнотекстовый поиск товаров и статей, self-hosted |
| **Интеграции** | СДЭК v2, YooMoney/aiomoney, ЦБ РФ | Доставка, оплата, курсы валют |
| **SEO** | `useSeoMeta`, Schema.org JSON-LD, sitemap, RSS | Индексация блога/каталога |
| **Инфра** | Docker Compose (6 сервисов), Nginx | Self-hosted, без cloud |
| **CI/CD** | GitLab CE (gitlab.wifiobd.ru) + Runner 18.9 + Container Registry | Не Docker Hub, не GitHub Actions |
| **Мониторинг** | Prometheus + Grafana + Loki + Promtail | Prod-профиль |
| **ИИ-система** | Gemini CLI, 7 агентов | Мультиагентная разработка |

**Принципы UI/UX:** Mobile-First · Race-Style Design · Dark theme by default · WCAG 2.1 AA · LCP < 2.5s

---

## 📁 Структура проекта

```
site-builder/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── auth/         # JWT, refresh rotation
│   │   │   ├── users/        # профиль, заказы, OBD2-устройства
│   │   │   ├── products/     # каталог, категории, варианты
│   │   │   ├── cart/         # Redis Hash, резервирование Lua
│   │   │   ├── orders/       # заказы, статусы, атомарное списание
│   │   │   ├── delivery/     # СДЭК v2 API
│   │   │   ├── payments/     # YooMoney, HMAC-SHA256 webhook
│   │   │   ├── blog/         # посты, теги, комментарии, SEO
│   │   │   ├── media/        # локальное хранилище, Celery WebP
│   │   │   ├── admin/        # CRUD + IoT-мониторинг (только role=admin)
│   │   │   ├── iot/          # WebSocket, Redis Streams → TimescaleDB
│   │   │   └── search/       # Meilisearch прокси
│   │   ├── core/           # config, security, dependencies, exceptions, logging
│   │   ├── db/
│   │   │   ├── models/       # все SQLAlchemy-модели здесь
│   │   │   └── migrations/   # Alembic versions
│   │   ├── tasks/          # Celery: media WebP, search, notifications, inventory
│   │   └── integrations/   # cdek, yoomoney, cbr_rates, meilisearch
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── assets/css/tokens.css   # ← единственный источник design tokens
│   ├── components/
│   │   ├── U/              # UI-кит: UButton, UCard, UThemeToggle…
│   │   ├── shop/           # ProductCard, CartItem, OrderStatus…
│   │   ├── blog/           # PostCard, PostContent…
│   │   ├── iot/            # TelemetryChart, DeviceStatus…
│   │   └── admin/          # AdminTable, AdminForm…
│   ├── pages/
│   ├── stores/             # themeStore, authStore, cartStore, productStore
│   ├── composables/
│   └── nuxt.config.ts
├── deploy/
│   ├── docker-compose.prod.yml
│   ├── nginx/nginx.conf
│   ├── monitoring/             # prometheus.yml, loki.yml, promtail.yml
│   └── scripts/
│       ├── setup_server.sh
│       ├── setup_runner.sh
│       └── deploy.sh
├── .gemini/
│   ├── agents/             # промпты агентов
│   ├── commands/           # slash-команды
│   ├── policies/           # TOML-политики
│   └── system.md           # системный промпт оркестратора
├── docker-compose.yml       # dev: api, frontend, postgres, redis, celery, meilisearch, nginx
├── .gitlab-ci.yml
├── .env.example
├── GEMINI.md                # ← точка входа для ИИ-агента
├── DEVOPS.md
├── CHANGELOG.md
└── plan.md
```

---

## 🚀 Быстрый старт

### Требования

- [Gemini CLI](https://github.com/google-gemini/gemini-cli) — установлен глобально
- Docker + Docker Compose
- Node.js 20+
- Python 3.12+

### Запуск

```bash
git clone https://github.com/f2re/site-builder.git
cd site-builder

cp .env.example .env
# Обязательно заполнить: SECRET_KEY, POSTGRES_PASSWORD, MEILI_MASTER_KEY, FERNET_KEY

docker compose up --build -d

# Применить миграции
docker compose exec api alembic upgrade head
```

### Отдельные сервисы

```bash
docker compose up postgres redis meilisearch -d   # БД, кэш, поиск
docker compose up api -d                          # FastAPI
docker compose up frontend -d                     # Nuxt 3 dev
```

---

## ⚡ Полезные команды

```bash
# ── Backend
cd backend
uvicorn app.main:app --reload
ruff check backend/app/ --fix
mypy backend/app/ --strict
alembic upgrade head
alembic revision --autogenerate -m "<domain>: <description>"
pytest -v --cov=app

# ── Frontend
cd frontend
npm run dev
npm run build
npm run lint

# ── Docker
docker compose ps
docker compose logs -f api
docker compose down -v

# ── Проверка сервисов
curl -s http://localhost:8000/health   # API
curl -s http://localhost:7700/health   # Meilisearch
```

---

## 📦 CI/CD: GitLab → Registry → prod

```
git tag v1.1.0 && git push origin v1.1.0
         ↓
  lint (ruff + mypy + vue-tsc)
         ↓
  test (pytest + services)
         ↓
  build: Docker-образы backend + frontend
         ↓
  push: GitLab Container Registry (gitlab.wifiobd.ru)
         ↓
  deploy_staging (авто, пуш в main)
         ↓
  deploy_prod (SSH → Машина B → docker compose pull + up)
```

Secrets — только через GitLab CI/CD Variables (`SSH_PRIVATE_KEY`, `PROD_HOST`, `DEPLOY_USER`).
Подробнее: [DEVOPS.md](DEVOPS.md)

---

## 🤖 Мультиагентная система (Gemini CLI)

Проект управляется системой специализированных агентов Gemini CLI.

> Начальная точка для агента: [`GEMINI.md`](GEMINI.md) — читать первым.

| Агент | Зона ответственности | Режим |
|-------|---------------------|-------|
| `@orchestrator` | Делегирует задачи, проверяет отчёты | read/write |
| `@backend-agent` | FastAPI, SQLAlchemy, Alembic, REST API, IoT | read/write |
| `@frontend-agent` | Nuxt 3, Vue 3, Pinia, UI-кит, SEO, admin-страницы | read/write |
| `@cdek-agent` | СДЭК v2, YooMoney, ЦБ РФ, Celery-интеграции | read/write |
| `@devops-agent` | Docker, Nginx, GitLab CI/CD, мониторинг | read/write |
| `@testing-agent` | pytest, WebSocket-тесты, Locust | read/write |
| `@security-agent` | OWASP, 152-ФЗ, audit | **только чтение** |

```bash
# Запуск новой задачи через оркестратор:
/agents:plan реализовать подключение Meilisearch к backend

# Прямой вызов агента:
@backend-agent создай db/models/telemetry.py с TimescaleDB hypertable
@frontend-agent добавь страницу /iot/[device_id].vue с TelemetryChart
@security-agent проведи аудит bleach.clean() в blog/service.py
```

---

## 📐 Принципы кодовой базы

**Backend:**
- Feature-First структура: `api/v1/{feature}/{router,service,repository,schemas}.py`
- Repository Pattern: сервисный слой никогда не импортирует из `db/` напрямую
- Dependency Injection: сессии, пользователь, настройки — через `Depends()`
- Circuit Breaker: `tenacity` + exponential backoff для СДЭК/YooMoney
- sanitize always: `bleach.clean()` для HTML из пользовательского ввода
- IoT: `time_bucket()` TimescaleDB для агрегации, не raw SELECT

**Frontend:**
- Composables для API-вызовов, Pinia stores для состояния
- `tokens.css` — единственный источник цветов, NO hardcoded colors
- `useSeoMeta` + Schema.org JSON-LD + `rel=canonical` — на каждой публичной странице
- NO hardcoded URL: только `useRuntimeConfig()`

**Безопасность:**
- JWT + refresh rotation, HMAC-SHA256 вебхук YooMoney
- Шифрование персданных Fernet (152-ФЗ)
- Rate limiting: `slowapi` на `/auth/*`, `/checkout`, `/payments/*`
- Secrets: только GitLab CI/CD Variables + `.env` на сервере, никогда в git

---

## 🔗 Ключевые файлы

| Файл | Назначение |
|-------------------|-----------|
| [`GEMINI.md`](GEMINI.md) | **Точка входа для ИИ-агента** — читать первым |
| [`plan.md`](plan.md) | Полное ТЗ с техническими деталями |
| [`DEVOPS.md`](DEVOPS.md) | CI/CD, SSH, Runner, деплой |
| [`CHANGELOG.md`](CHANGELOG.md) | История изменений |
| [`.env.example`](.env.example) | Шаблон всех переменных среды |
| [`docker-compose.yml`](docker-compose.yml) | Dev-среда (api, postgres, redis, celery, meilisearch, nginx) |
| [`deploy/docker-compose.prod.yml`](deploy/docker-compose.prod.yml) | Продакшн-композ |
| [`.gitlab-ci.yml`](.gitlab-ci.yml) | CI/CD пайплайн |
| [`.gemini/agents/`](.gemini/agents/) | Определения агентов |
| [`backend/requirements.txt`](backend/requirements.txt) | Python-зависимости |
