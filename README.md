# 🏐 WifiOBD Site Builder — E-Commerce Platform

> Современный интернет-магазин (**E-Commerce + Blog + IoT**) на базе **FastAPI + Nuxt 3**.
> SEO-оптимизирован, self-hosted, CI/CD через GitLab, управляется мультиагентной системой **Gemini CLI**.

---

## 📈 Статус разработки

| Этап | Название | Статус |
|--------|---------|--------|
| 1 | Инфраструктура и ядро (Docker, JWT, логи, БД) | ✅ Готов |
| 2 | Каталог товаров + инвентарь (Redis + PG) | 🔄 В работе |
| 3 | Корзина, заказы, YooMoney, СДЭК | ⏳ Ожидает |
| 4 | **Блог + медиа (TipTap + MinIO + SEO)** | ⏳ Ожидает |
| 5 | Админпанель | ⏳ Ожидает |
| 6 | Уведомления, курсы валют | ⏳ Ожидает |
| 7 | Безопасность (152-ФЗ, bleach, HMAC) | ✅ Параллельно |
| 8 | IoT / OBD2 интеграция | ⏳ Ожидает |
| 9 | **SEO: sitemap, Schema.org, canonical, CWV** | ⏳ Ожидает |
| 10 | Тесты + Lighthouse CI + деплой | ⏳ Ожидает |

Полный план с техническими деталями: [→ `plan.md`](plan.md)

---

## 📐 Архитектура и стек технологий

| Слой | Технологии | Назначение |
|------|-----------|-----------|
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy 2.x async, Alembic, PostgreSQL 16 | REST API, асинхронное ядро |
| **Frontend** | Nuxt 3, Vue 3, Pinia, TypeScript, vee-validate + zod | SSR для SEO блога и каталога |
| **Кэш / Очереди** | Redis 7, Celery + Redis broker | Кэш каталога/блога, резерв остатков, обработка медиа |
| **Хранилище медиа** | MinIO (self-hosted S3) | Фото/видео товаров и блога, presigned URL, WebP |
| **Поиск** | Meilisearch | Полнотекстовый поиск товаров, self-hosted |
| **Интеграции** | CDEK v2 API, YooMoney | Доставка, HMAC-SHA256 webhook |
| **SEO** | Nuxt `useSeoMeta`, Schema.org JSON-LD, sitemap, RSS | Индексация блога/каталога |
| **Инфраструктура** | Docker Compose, Nginx, Prometheus, Grafana, Loki | Self-hosted, без cloud |
| **CI/CD** | GitLab CE + GitLab Runner + GitLab Container Registry | Без Docker Hub |
| **ИИ-система** | Gemini CLI, 7 агентов | Мультиагентная разработка |

**Принципы UI/UX:** Mobile-First · Race-Style Design · WCAG 2.1 AA · LCP < 2.5s · CLS < 0.1

---

## 📂 Структура проекта

```
project/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── products/    # каталог, варианты, Schema.org Product
│   │   │   ├── blog/        # посты, категории, теги, комментарии
│   │   │   ├── media/       # presigned URL MinIO, WebP Celery-таска
│   │   │   ├── orders/      # заказы, статусы
│   │   │   ├── cart/        # Redis Hash, гости/авторизованные
│   │   │   ├── payments/    # YooMoney HMAC webhook
│   │   │   ├── delivery/    # СДЭК v2
│   │   │   ├── users/
│   │   │   ├── auth/
│   │   │   ├── admin/
│   │   │   └── iot/         # OBD2, Redis Stream, WebSocket
│   │   ├── core/            # config, security, dependencies
│   │   ├── db/models/       # SQLAlchemy ORM модели
│   │   ├── tasks/           # Celery: media, search, email, blog
│   │   └── integrations/    # minio.py, cdek.py, yoomoney.py, cbr_rates.py
│   └── requirements.txt
├── frontend/
│   ├── pages/
│   │   ├── blog/[slug].vue  # Schema.org BlogPosting, useSeoMeta
│   │   └── products/[slug].vue  # Schema.org Product
│   ├── composables/
│   │   ├── useSeo.ts        # useSeoMeta + canonical
│   │   └── useSchemaOrg.ts  # JSON-LD: Article, Product, Breadcrumb
│   ├── server/routes/
│   │   ├── sitemap.xml.ts   # динамический sitemap
│   │   ├── robots.txt.ts    # robots с Sitemap:
│   │   └── rss.xml.ts       # RSS-фид блога
│   ├── components/
│   │   └── AppBreadcrumbs.vue  # BreadcrumbList Schema.org
│   └── error.vue            # 404 с noindex
├── deploy/
│   ├── docker-compose.prod.yml
│   └── nginx/nginx.conf     # MinIO proxy, CSP, sitemap
├── .gemini/                 # агенты, политики, команды
├── .gitlab-ci.yml           # build → test → push → deploy
└── plan.md                  # полное ТЗ с техническими деталями
```

---

## 📝 Блог — архитектура

Блог является **основным источником SEO-трафика** для OBD2-тематики. Рендерится через Nuxt SSR.

### Контент и редактор

- **TipTap** (`@tiptap/vue-3`) — rich-text редактор в админпанели
- Контент хранится в двух форматах: `content_json` (TipTap JSON, для редактора) + `content_html` (pre-rendered, для SSR)
- `bleach.clean()` санитизирует HTML перед сохранением (XSS)
- Видео: embed YouTube/RuTube через TipTap YouTube extension или загрузка MP4 в MinIO

### Загрузка медиа (MinIO)

```
1. Frontend → POST /api/v1/media/upload-url  → presigned PUT URL
2. Frontend → PUT <presigned URL> (MinIO)     → загрузка без прокси через FastAPI
3. Frontend → POST /api/v1/media/confirm     → запись в БД + Celery-таска
4. Celery    → Pillow: WebP + 3 размера (480/800/1200px) → MinIO
```

> См. технические детали: [plan.md § Этап 4](plan.md)

---

## 🔍 SEO архитектура

Все публичные страницы обязаны содержать:

| Компонент | Реализация | Страницы |
|-----------|------------|----------|
| `useSeoMeta` | title, description, OG, Twitter Cards | все |
| Schema.org `BlogPosting` | JSON-LD с автором, датами, `wordCount` | `/blog/[slug]` |
| Schema.org `Product` | цена, наличие, SKU | `/products/[slug]` |
| Schema.org `BreadcrumbList` | microdata + JSON-LD | товары, статьи |
| `rel=canonical` | URL без sort/page, но с category | /products |
| `sitemap.xml` | динамический: все товары + статьи + статика | `/sitemap.xml` |
| `robots.txt` | Disallow /admin, /cart, ?* | `/robots.txt` |
| RSS-фид | последние 20 статей | `/rss.xml` |
| 301/302 редиректы | таблица `Redirect` в PG + Redis кэш | server middleware |
| Core Web Vitals | `alt`+`width`+`height` для всех `<img>`, WebP, `lazy` | все |

**Целевые метрики:** Lighthouse SEO = 100 · Performance ≥ 90 · CLS < 0.1 · LCP < 2.5s

---

## 🤖 Мультиагентная система (Gemini CLI)

Проект управляется системой специализированных ИИ-агентов. Каждый агент имеет строгую зону ответственности.

### Агенты

| Агент | Зона ответственности | Режим |
|-------|---------------------|-------|
| `orchestrator` | Делегирует задачи, проверяет отчёты | read/write |
| `backend-agent` | FastAPI, SQLAlchemy, Pydantic, REST API, Celery | read/write |
| `frontend-agent` | Nuxt 3, Vue 3, Pinia, TypeScript, SEO composables | read/write |
| `security-agent` | OWASP, 152-ФЗ, bleach, HMAC, XSS-аудит | **только чтение** |
| `testing-agent` | pytest, respx, Locust, Lighthouse CI | read/write |
| `cdek-agent` | CDEK v2 API, YooMoney интеграция | read/write |
| `devops-agent` | Docker, Nginx, GitLab CI/CD, Prometheus, MinIO | read/write |

Определения агентов: [`.gemini/agents/`](.gemini/agents/)

### Работа с агентами

**Способ 1 — Прямой вызов в чате Gemini CLI:**

```
@orchestrator создай план реализации блог-модуля
@backend-agent реализуй модели BlogPost, BlogCategory, BlogPostMedia
@frontend-agent добавь страницу /blog/[slug].vue с useSeoMeta и useSchemaOrg
@frontend-agent реализуй sitemap.xml server route
@security-agent проведи аудит bleach.clean() в blog/service.py
@devops-agent настрой Nginx proxy для MinIO /media/
```

> `orchestrator` **некогда не пишет код** — только делегирует и проверяет отчёты.

**Способ 2 — Система задач (слэш-команды):**

```bash
/agents:start backend-agent реализовать модуль media/ presigned URL + Celery process_image
/agents:start frontend-agent добавить AppBreadcrumbs.vue с Schema.org BreadcrumbList
/agents:run
/agents:status
```

**Способ 3 — Domain-команды:**

```bash
/shop:frontend добавить TipTap-редактор в /admin/blog
/shop:backend реализовать RSS-фид блога
/shop:review проверить последние изменения в PR
```

---

## 🚀 Быстрый старт разработки

### 1. Требования

- [Gemini CLI](https://github.com/google-gemini/gemini-cli) установлен глобально
- Docker + Docker Compose
- Node.js 20+
- Python 3.12+

### 2. Клонирование и запуск

```bash
git clone https://github.com/f2re/site-builder.git
cd site-builder

# Копировать и заполнить переменные
cp .env.example .env
# Отредактировать .env: SECRET_KEY, POSTGRES_PASSWORD, MINIO_ROOT_PASSWORD, NUXT_PUBLIC_SITE_URL

# Запустить всю инфраструктуру
docker-compose up --build

# Или только нужные сервисы
docker-compose up postgres redis minio     # БД, кэш, хранилище
docker-compose up backend                  # FastAPI сервер
docker-compose up frontend                 # Nuxt 3 dev-сервер
```

### 3. Первый запуск Gemini CLI

```bash
# Gemini CLI подхватит .gemini/settings.json автоматически
gemini

# Убедиться, что агенты активны:
/agents:status
```

---

## ⚡ Полезные команды

```bash
# ── Frontend (Nuxt 3)
npm run dev           # dev-сервер с HMR
npm run build         # production build
npm run lint          # ESLint
npm run type-check    # vue-tsc --noEmit
npx nuxt analyze      # анализ бандла

# ── Backend (FastAPI)
cd backend
uvicorn app.main:app --reload   # dev-сервер
ruff check .                    # линтер
mypy .                          # type-check
alembic upgrade head            # применить миграции
alembic revision --autogenerate -m "add blog tables"  # создать миграцию

# ── Тесты
pytest -v                       # все тесты
pytest tests/unit/              # unit
pytest tests/integration/       # integration
npm run test:lighthouse         # Lighthouse CI

# ── SEO-проверка
curl https://wifiobd.shop/sitemap.xml  # должен вернуть XML
curl https://wifiobd.shop/robots.txt   # должен содержать Sitemap:
curl -I https://wifiobd.shop/blog/test-post  # проверить canonical в headers

# ── Инфраструктура
docker-compose ps               # статус контейнеров
docker-compose logs -f backend  # логи сервиса
docker-compose down -v          # остановить + удалить volumes

# ── Целостность MinIO
curl http://localhost:9001      # MinIO Console
```

---

## 📊 CI/CD: GitLab → GitLab Registry → prod

```
git push main
    ↓
build: backend + frontend Docker-образы
    ↓
test: pytest + Lighthouse CI
    ↓
push: GitLab Container Registry (registry.ci.internal:5005)
    ↓
deploy: SSH → prod → docker-compose pull + up  [ручной запуск]
```

Secrets — только через GitLab CI/CD Variables, не в репозитории.

---

## 📄 Структура задачи агента

```json
{
  "task_id": "20260226_143000_frontend",
  "agent": "frontend-agent",
  "status": "pending",
  "priority": "normal",
  "description": "Реализовать sitemap.xml server route",
  "created_at": "2026-02-26T14:30:00Z",
  "dependencies": [],
  "report_path": ".gemini/agents/reports/frontend/20260226_143000_frontend.md"
}
```

Жизненный цикл: `pending → running → done` (или `blocked` → эскалация)

---

## 📋 Структура отчёта агента

Каждый агент **обязан** включить все секции — orchestrator отклонит неполный отчёт:

```markdown
## Status        — DONE / BLOCKED
## Completed     — список реализованных файлов
## Artifacts     — роуты, компоненты, схемы API
## Contracts Verified — какие coding-контракты проверены
## SEO Verified  — useSeoMeta + canonical + Schema.org (только frontend)
## Accessibility — axe-core, alt/width/height (только frontend)
## Performance   — Lighthouse mobile scores (только frontend)
## Next          — задачи-продолжения
## Blockers      — проблемы для эскалации
```

> **Новое по сравнению с предыдущей версией:** добавлена секция `## SEO Verified` — frontend-agent обязан проверять наличие `useSeoMeta`, Schema.org и `rel=canonical` на каждой реализованной странице.

---

## 🔗 Ключевые файлы проекта

| Файл / Директория | Назначение |
|-------------------|-----------|
| [`plan.md`](plan.md) | **Полное ТЗ** со 10 этапами, моделями БД, кодом SEO-компонентов, чек-листом |
| [`.gemini/agents/`](.gemini/agents/) | Определения агентов (контракты, workflow) |
| [`.gemini/agents/contracts/api_contracts.md`](.gemini/agents/contracts/api_contracts.md) | **Читать ПЕРВЫМ** перед любой задачей |
| [`.gemini/commands/agents/`](.gemini/commands/agents/) | Слэш-команды: `start`, `run`, `status` |
| [`.gemini/commands/shop/`](.gemini/commands/shop/) | Domain-команды: `frontend`, `backend`, `review` |
| [`.gemini/settings.json`](.gemini/settings.json) | Конфигурация Gemini CLI |
| [`.gemini/system.md`](.gemini/system.md) | Системный промпт оркестратора |
| [`.env.example`](.env.example) | Шаблон всех переменных среды |
| [`backend/requirements.txt`](backend/requirements.txt) | Python-зависимости (полный список в `plan.md`) |
| [`deploy/docker-compose.prod.yml`](deploy/docker-compose.prod.yml) | Продакшн-композ |
| [`deploy/nginx/nginx.conf`](deploy/nginx/nginx.conf) | Nginx: proxy MinIO, CSP, sitemap, фонты |
| [`.gitlab-ci.yml`](.gitlab-ci.yml) | CI/CD пайплайн: build → test → push → deploy |
| [`CHANGELOG.md`](CHANGELOG.md) | История изменений |

---

## 🏗️ Принципы кодовой базы

**Backend:**
- Repository Pattern: сервисный слой работает только через репозиторий
- Dependency Injection: сессии БД, пользователь, настройки через `Depends()`
- Sanitize always: `bleach.clean()` для любого HTML из пользовательского ввода
- Circuit Breaker: `tenacity` с exponential backoff для CDEK/YooMoney

**Frontend:**
- Composables для всех API-вызовов, Pinia stores для состояния
- `useSeoMeta` + `useSchemaOrg` + `rel=canonical` — на каждой публичной странице
- NO hardcoded URLs: только `useRuntimeConfig()`
- Фото: `alt`+`width`+`height`+`loading="lazy"` обязательные атрибуты

**Безопасность:**
- JWT + refresh rotation, HMAC-SHA256 webhook YooMoney
- Шифрование персональных данных Fernet (152-ФЗ)
- Rate limiting: `slowapi` на `/auth/*`, `/checkout`, `/media/upload-url`
- Secrets: только GitLab CI/CD Variables + `.env.prod` на сервере
