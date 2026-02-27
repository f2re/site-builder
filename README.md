# 🏐 WifiOBD Site Builder — E-Commerce Platform

> Современный интернет-магазин (**E-Commerce + Blog + IoT**) на базе **FastAPI + Nuxt 3**.
> SEO-оптимизирован, self-hosted, CI/CD через GitLab, управляется мультиагентной системой **Gemini CLI**.

---

## 📈 Статус разработки

| Этап | Название | Статус |
|--------|---------|--------|
| 1 | Инфраструктура и ядро (Docker, JWT, логи, БД, Redis) | ✅ Готов |
| 2 | Каталог товаров + инвентарь (products, categories, variants) | ✅ Готов |
| 3 | Корзина, заказы, YooMoney, СДЭК | ✅ Готов |
| 4 | Блог + медиа (TipTap + SEO) | ✅ Готов |
| 5 | Админпанель (CRUD товары/заказы/блог/пользователи) | ✅ Готов |
| 6 | Пользовательский кабинет (профиль, заказы, устройства, WS) | ✅ Готов |
| 7 | Безопасность (152-ФЗ, bleach, HMAC, rate limiting) | ✅ Готов |
| 8 | IoT / OBD2 интеграция (Redis Stream, WebSocket) | ✅ Готов |
| 9 | **CI/CD (GitLab Runner, Docker Registry, SSH-деплой)** | ✅ Готов |
| 10 | **SEO: sitemap, Schema.org, canonical, CWV** | 🔄 В работе |
| 11 | Meilisearch интеграция в backend | 🔄 В работе |
| 12 | Тесты + Lighthouse CI | ⏳ Ожидает |

Полный план с техническими деталями: [→ `plan.md`](plan.md)

---

## 📅 Что реализовано (v1.0.3)

### Backend (`backend/app/api/v1/`)

| Модуль | Описание |
|-------|------------|
| `auth/` | JWT аутентификация, refresh rotation, выход |
| `users/` | Профиль, заказы, устройства, WebSocket OBD2 |
| `products/` | Каталог, категории, варианты, cursor-пагинация |
| `cart/` | Redis Hash, гостевой/авторизованный режим |
| `orders/` | Создание, статусы, атомарное списание со склада |
| `delivery/` | СДЭК v2 API, расчёт тарифов |
| `blog/` | Посты, категории, теги, комментарии, SEO-слаги |
| `media/` | Локальное хранилище, Celery WebP-преобразование |
| `admin/` | CRUD товары/заказы/блог/пользователи, IoT-мониторинг |
| `iot/` | OBD2 устройства, Redis Stream телеметрия |

### Инфраструктура

- ✅ GitLab Runner 18.9 (`site-builder-runner`) зарегистрирован на [gitlab.wifiobd.ru](https://gitlab.wifiobd.ru)
- ✅ CI/CD пайплайн: `lint → test → build → deploy_staging → deploy_prod`
- ✅ Деплой по тегу (`git push origin vX.Y.Z`) — SSH на Машину B
- ✅ `deploy/scripts/setup_server.sh` — инициализация прод-сервера
- ✅ `deploy/scripts/setup_runner.sh` — установка Runner (glrt-токен, GitLab 16+)

### Что в работе

- 🔄 Подключение Meilisearch-клиента к backend (client, config, индекс `products`)
- 🔄 Frontend SEO: sitemap.xml, Schema.org, canonical
- 🔄 `package-lock.json` — обновить после добавления `@nuxt/image`, `nuxt-icon`

---

## 📀 Архитектура и стек технологий

| Слой | Технологии | Назначение |
|------|-----------|-----------|
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy 2.x async, Alembic, PostgreSQL 16 + TimescaleDB | REST API, асинхронное ядро |
| **Frontend** | Nuxt 3 (v4.x), Vue 3, Pinia, TypeScript, `@nuxt/image`, `nuxt-icon` | SSR для SEO блога и каталога |
| **Кэш / Очереди** | Redis 7, Celery (worker+beat) | Кэш каталога/блога, резерв остатков, обработка медиа |
| **Хранилище медиа** | Локальная папка `/media` за Nginx | Фото/видео товаров и блога, WebP |
| **Поиск** | Meilisearch | Полнотекстовый поиск товаров, self-hosted |
| **Интеграции** | CDEK v2 API, YooMoney | Доставка, HMAC-SHA256 webhook |
| **SEO** | Nuxt `useSeoMeta`, Schema.org JSON-LD, sitemap, RSS | Индексация блога/каталога |
| **Инфраструктура** | Docker Compose (7 сервисов), Nginx | Self-hosted, без cloud |
| **CI/CD** | GitLab CE (gitlab.wifiobd.ru) + GitLab Runner 18.9 + GitLab Container Registry | Без Docker Hub |
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
│   │   │   ├── media/       # загрузка файлов, WebP Celery-таска
│   │   │   ├── orders/      # заказы, статусы
│   │   │   ├── cart/        # Redis Hash, гости/авторизованные
│   │   │   ├── delivery/    # СДЭК v2
│   │   │   ├── users/       # профиль, заказы, OBD2 устройства, WebSocket
│   │   │   ├── auth/        # JWT, refresh rotation
│   │   │   ├── admin/       # полный CRUD + IoT-мониторинг
│   │   │   └── iot/         # OBD2, Redis Stream, WebSocket
│   │   ├── core/            # config, security, dependencies
│   │   ├── db/models/       # SQLAlchemy ORM модели
│   │   ├── tasks/           # Celery: media, search, email, blog
│   │   └── integrations/    # cdek.py, yoomoney.py
│   └── requirements.txt
├── frontend/
│   ├── pages/
│   ├── components/
│   ├── composables/
│   ├── stores/              # Pinia
│   ├── layouts/
│   ├── assets/
│   ├── nuxt.config.ts
│   └── package.json
├── deploy/
│   ├── docker-compose.prod.yml
│   ├── nginx/nginx.conf
│   └── scripts/
│       ├── setup_server.sh  # инициализация Машины B
│       ├── setup_runner.sh  # установка GitLab Runner (glrt-)
│       └── deploy.sh        # запуск на Машине B через SSH
├── .gemini/                 # агенты, политики, команды
├── .gitlab-ci.yml           # lint → test → build → deploy
├── DEVOPS.md                # инструкция по CI/CD и деплою
└── plan.md                  # полное ТЗ с техническими деталями
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
# Отредактировать .env: SECRET_KEY, POSTGRES_PASSWORD, MEILI_MASTER_KEY

# Запустить всю инфраструктуру
docker-compose up --build

# Или только нужные сервисы
docker-compose up postgres redis meilisearch  # БД, кэш, поиск
docker-compose up api                         # FastAPI сервер
docker-compose up frontend                    # Nuxt 3 dev-сервер
```

### 3. Применить миграции БД

```bash
cd backend
alembic upgrade head
```

---

## ⚡ Полезные команды

```bash
# ── Frontend (Nuxt 3)
cd frontend
npm install
npm run dev           # dev-сервер с HMR
npm run build         # production build
npm run lint          # vue-tsc --noEmit
npm run typecheck     # vue-tsc --noEmit

# ── Backend (FastAPI)
cd backend
uvicorn app.main:app --reload   # dev-сервер
ruff check backend/app/ --fix   # линтер + autofix
mypy backend/app/ --ignore-missing-imports  # type-check
alembic upgrade head            # применить миграции
alembic revision --autogenerate -m "add table"  # создать миграцию

# ── Тесты
pytest -v
pytest tests/unit/
pytest tests/integration/

# ── Инфраструктура
docker-compose ps
docker-compose logs -f api
docker-compose down -v

# ── Meilisearch
curl -s http://localhost:7700/health
```

---

## 📦 CI/CD: GitLab → Registry → prod

```
git tag v1.0.4 && git push origin v1.0.4
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

Secrets — только через GitLab CI/CD Variables (`SSH_PRIVATE_KEY` тип File, `PROD_HOST`, `DEPLOY_USER`). Подробнее: [DEVOPS.md](DEVOPS.md)

---

## 🤖 Мультиагентная система (Gemini CLI)

Проект управляется системой специализированных ИИ-агентов. Каждый агент имеет строгую зону ответственности.

| Агент | Зона ответственности | Режим |
|-------|---------------------|-------|
| `orchestrator` | Делегирует задачи, проверяет отчёты | read/write |
| `backend-agent` | FastAPI, SQLAlchemy, Pydantic, REST API, Celery | read/write |
| `frontend-agent` | Nuxt 3, Vue 3, Pinia, TypeScript, SEO composables | read/write |
| `security-agent` | OWASP, 152-ФЗ, bleach, HMAC, XSS-аудит | **только чтение** |
| `testing-agent` | pytest, respx, Locust, Lighthouse CI | read/write |
| `cdek-agent` | CDEK v2 API, YooMoney интеграция | read/write |
| `devops-agent` | Docker, Nginx, GitLab CI/CD | read/write |

Определения агентов: [`.gemini/agents/`](.gemini/agents/)

```bash
# Примеры вызовов:
@backend-agent реализуй клиент Meilisearch в app/db/meilisearch.py
@frontend-agent добавь страницу /blog/[slug].vue с useSeoMeta и Schema.org
@devops-agent настрой Nginx для раздачи /media/
@security-agent проведи аудит bleach.clean() в blog/service.py
```

---

## 🔗 Ключевые файлы проекта

| Файл / Директория | Назначение |
|-------------------|-----------|
| [`plan.md`](plan.md) | **Полное ТЗ** со 12 этапами, моделями БД, кодом SEO-компонентов |
| [`DEVOPS.md`](DEVOPS.md) | Полная инструкция по CI/CD, SSH, Runner, деплою |
| [`CHANGELOG.md`](CHANGELOG.md) | История изменений |
| [`.env.example`](.env.example) | Шаблон всех переменных среды |
| [`backend/requirements.txt`](backend/requirements.txt) | Python-зависимости |
| [`deploy/docker-compose.prod.yml`](deploy/docker-compose.prod.yml) | Продакшн-композ (7 сервисов) |
| [`deploy/scripts/setup_runner.sh`](deploy/scripts/setup_runner.sh) | Установка Runner (GitLab 16+, glrt-токен) |
| [`deploy/scripts/setup_server.sh`](deploy/scripts/setup_server.sh) | Инициализация прод-сервера |
| [`.gitlab-ci.yml`](.gitlab-ci.yml) | CI/CD пайплайн |
| [`.gemini/agents/`](.gemini/agents/) | Определения агентов |

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
