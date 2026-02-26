Вот исправленный и дополненный документ. Раздел **Деплой** в Этапе 9 полностью переработан под self-hosted GitLab с встроенным Container Registry и деплоем по SSH без использования Docker Hub. [docs.gitlab](https://docs.gitlab.com/user/packages/container_registry/build_and_push_images/)

***

# Техническое задание: Интернет-магазин на FastAPI + Vue

## 1. Архитектурная концепция

Система строится на **модульной Clean Architecture**: каждый домен (товары, заказы, блог, IoT) — изолированный модуль со своими роутерами, схемами, сервисами и репозиториями. Это позволяет масштабировать и тестировать каждый модуль независимо. Асинхронность FastAPI + SQLAlchemy async обеспечивает максимальную производительность на I/O-операциях.

**Технологический стек:**

| Слой | Технология | Обоснование |
|------|-----------|-------------|
| Backend API | FastAPI (Python 3.12+) | Async-first, автодокументация Swagger/ReDoc, type hints |
| ORM | SQLAlchemy 2.x (async) + Alembic | Миграции, type-safe запросы |
| БД основная | PostgreSQL 16 | ACID, JSONB для атрибутов товаров |
| Кэш / Очереди | Redis 7 | Кэш каталога, корзина, инвентарь в реальном времени |
| Фоновые задачи | Celery + Redis broker | Email/SMS, обновление курсов, обработка заказов |
| Frontend | Vue 3 + Pinia + Vite | SPA с SSR (Nuxt 3) для SEO блога |
| Контейнеризация | Docker Compose (dev) / Docker Compose + Nginx (prod) | Self-hosted, без внешних cloud-провайдеров |
| CI/CD | GitLab CE (self-hosted) + GitLab Runner + GitLab Container Registry | Полностью локальный пайплайн без Docker Hub |
| Поиск | Meilisearch | Полнотекстовый поиск товаров, легковесный self-hosted |

***

## 2. Структура проекта

```
project/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── products/    # роутер, схемы, сервис, репозиторий
│   │   │       ├── orders/
│   │   │       ├── cart/
│   │   │       ├── blog/
│   │   │       ├── delivery/    # СДЭК
│   │   │       ├── payments/    # YooMoney
│   │   │       ├── iot/
│   │   │       └── users/
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic Settings
│   │   │   ├── security.py      # JWT, bcrypt
│   │   │   └── dependencies.py
│   │   ├── db/
│   │   │   ├── models/
│   │   │   └── migrations/      # Alembic
│   │   ├── tasks/               # Celery tasks
│   │   └── integrations/
│   │       ├── cdek.py
│   │       ├── yoomoney.py
│   │       └── cbr_rates.py
├── frontend/                    # Vue 3 / Nuxt 3
├── deploy/
│   ├── docker-compose.prod.yml  # продакшн compose с образами из внутреннего реестра
│   └── nginx/
│       └── nginx.conf
└── .gitlab-ci.yml               # единая точка CI/CD
```

***

## 3. Этапы разработки

### Этап 1 — Инфраструктура и ядро (2–3 нед.)

- **Docker Compose**: сервисы `api`, `postgres`, `redis`, `celery_worker`, `celery_beat`, `frontend`, `meilisearch`
- **Конфигурация**: `Pydantic BaseSettings` — все секреты из `.env`, никаких хардкодов
- **БД**: асинхронное подключение через `asyncpg`, сессии через Dependency Injection
- **Аутентификация**: JWT (access + refresh token), хэширование паролей `bcrypt`/`argon2`, ролевая модель (admin, manager, customer)
- **Логирование**: структурированные логи (JSON) через `structlog`, middleware для каждого запроса
- **Базовая обработка ошибок**: глобальные exception handlers, никаких внутренних деталей в ответах

### Этап 2 — Каталог товаров и инвентарь (2–3 нед.)

**Модели БД:**
- `Category` (дерево через LTREE или Adjacency List), `Product`, `ProductVariant`, `ProductImage`, `StockMovement`
- Атрибуты товаров — через JSONB (динамические характеристики без лишних таблиц)

**Инвентарь (остатки) — Redis + PostgreSQL:**
- PostgreSQL — источник правды (source of record) для остатков
- Redis Hash `stock:{product_id}` — быстрое чтение доступного количества
- При добавлении в корзину — **резервирование через Redis lease** с TTL (например, 30 минут); при истечении — автоматический возврат остатка
- Lua-скрипты для атомарного списания (исключает race conditions)

**API эндпоинты:**
- `GET /products` — пагинация (cursor-based), фильтры по категории/цене/атрибутам, сортировка
- `GET /products/{slug}` — карточка с галереей, характеристиками, отзывами
- `GET /categories` — дерево категорий (кэш Redis, TTL 10 мин)

**Поиск:**
- Интеграция Meilisearch: индексация при изменении товара через Celery-таску

### Этап 3 — Корзина, заказы, платежи (2–3 нед.)

**Корзина:**
- Хранение в Redis (для гостей — по session_id, для авторизованных — по user_id)
- Структура: `cart:{user_id}` → Hash `{product_id: quantity}`
- Синхронизация корзины гостя в корзину пользователя при логине

**Оформление заказа (workflow):**
1. Валидация остатков (Redis → резервирование)
2. Расчёт доставки через СДЭК API
3. Создание заказа в БД (статус `PENDING`)
4. Создание платёжной ссылки YooMoney
5. Webhook от YooMoney → подтверждение оплаты → статус `PAID` → списание резерва из Redis и PostgreSQL

**Интеграция YooMoney:**
- Библиотека `aiomoney` (async) или `yoomoney`
- `Quickpay` форма для физлиц, ЮKassa для юрлиц
- Проверка подлинности webhook через HMAC-SHA256 подпись
- Идемпотентные обработчики (защита от дублей)

**Интеграция СДЭК v2 API:**
- OAuth2 авторизация (`client_id` + `client_secret` из ЛК СДЭК)
- `POST /v2/calculator/tariff` — расчёт стоимости и сроков по тарифу
- `GET /v2/deliverypoints` — список ПВЗ с фильтрацией по городу
- `POST /v2/orders` — создание накладной после оплаты
- `GET /v2/orders?cdek_number=...` — отслеживание статуса
- Все запросы к СДЭК — через Celery-таску с retry при ошибках сети

### Этап 4 — Блог и контент (1–2 нед.)

**Модели:** `BlogPost`, `BlogCategory`, `Tag`, `Comment`, `Author`

**Функционал:**
- Rich-text контент через `TipTap` (фронт) + сохранение HTML/Markdown в БД
- SEO-поля: `meta_title`, `meta_description`, `og_image`, `slug` (auto-generate из заголовка)
- Превью (краткое описание), дата публикации, статус (`draft`/`published`/`archived`)
- Комментарии с модерацией (статус `pending`/`approved`)
- Рейтинги (лайки) через Redis для быстрого обновления счётчиков
- RSS-фид для SEO
- Кэширование списка статей в Redis (TTL 5 мин), инвалидация при публикации

### Этап 5 — Административная панель (2 нед.)

Реализовать через **отдельный Vue SPA** (или Nuxt admin-секция), защищённый role-based access:

**Разделы:**
- **Товары**: CRUD продуктов, категорий, управление фото (загрузка в MinIO — self-hosted S3-совместимое хранилище), импорт/экспорт CSV
- **Заказы**: список с фильтрами по статусу, ручная смена статуса, печать накладной СДЭК
- **Клиенты**: список пользователей, история заказов, блокировка
- **Контент**: редактор блога, управление комментариями
- **Интеграции**: настройка ключей API (СДЭК, YooMoney), статус подключений
- **IoT-мониторинг**: статусы устройств, очереди Redis (длина, задержка), логи событий
- **Аналитика**: выручка, топ товаров, конверсия

**Реализация**: FastAPI Admin или кастомный раздел `/admin/*` с отдельным JWT-scope `admin`

### Этап 6 — Уведомления и курсы валют (1 нед.)

**Email** через `fastapi-mail` (SMTP/SendGrid):
- Подтверждение заказа, смена статуса, регистрация

**SMS** через `smsc.ru` или `SMS.ru` API:
- Уведомление о статусе доставки

**Курсы валют ЦБ РФ:**
- Celery Beat задача раз в час: `GET https://www.cbr-xml-daily.ru/daily_json.js`
- Сохранение в PostgreSQL + Redis-кэш
- Применение к ценам в каталоге при необходимости мультивалютности

### Этап 7 — Безопасность (параллельно со всеми этапами)

- **152-ФЗ и GDPR**: шифрование персональных данных (имя, телефон) в БД, политика конфиденциальности, согласие на обработку ПД при регистрации
- **Валидация**: все входные данные через Pydantic-схемы; параметризованные запросы SQLAlchemy (защита от SQL-инъекций)
- **XSS**: санитизация HTML-контента блога через `bleach`
- **Rate Limiting**: `slowapi` (wrapper над limits) на критичных эндпоинтах (login, checkout)
- **HTTPS**: Nginx + Certbot (Let's Encrypt) или самоподписанные сертификаты для внутренней сети
- **Секреты**: только через переменные окружения (не в коде); в CI/CD — через GitLab CI/CD Variables (Settings → CI/CD → Variables), не в репозитории

### Этап 8 — IoT-интеграция (OBD2) (2 нед.)

- Устройства регистрируются в системе и привязываются к аккаунту пользователя (`UserDevice` модель)
- Данные от устройств → `POST /iot/data` → валидация → Redis Stream (`XADD`)
- Celery-воркер читает из Redis Stream (`XREAD`), обрабатывает и сохраняет в PostgreSQL (TimescaleDB или партиционированные таблицы)
- WebSocket-эндпоинт `/ws/iot/{device_id}` для real-time отображения данных в личном кабинете

### Этап 9 — Тестирование и деплой (1–2 нед.)

**Тестирование:**
- Unit-тесты: `pytest` + `pytest-asyncio`, мокирование внешних API (СДЭК, YooMoney) через `respx`/`httpretty`
- Интеграционные тесты: `TestClient` FastAPI + тестовая БД (PostgreSQL в Docker)
- Нагрузочное тестирование: `Locust` или `k6` — сценарии каталога, checkout, Redis-очереди
- Security-тестирование: `OWASP ZAP` для API

***

## Деплой — GitLab CI/CD (Self-Hosted, без Docker Hub)

### Инфраструктурные требования

Все компоненты — исключительно на собственных серверах:

| Компонент | Размещение | Описание |
|---|---|---|
| **GitLab CE** | сервер CI (напр., `ci.internal`) | Хранит код, запускает пайплайны |
| **GitLab Container Registry** | встроен в GitLab CE | Хранит Docker-образы, не требует Docker Hub |
| **GitLab Runner** | тот же или отдельный сервер | Выполняет джобы, executor: `docker` |
| **Продакшн-сервер** | `prod.internal` | Запускает финальные контейнеры через `docker-compose` |

### Схема пайплайна

```
git push → GitLab CE (self-hosted)
              ↓
         GitLab Runner (Docker executor)
              ↓
     build → test → push → deploy
                       ↓         ↓
           GitLab Container   SSH → prod-сервер
              Registry           docker-compose pull + up
           (registry.ci.internal:5005)
```

### Шаг 1 — Включить встроенный Container Registry в GitLab CE

В конфигурации GitLab (`/etc/gitlab/gitlab.rb`): [docs.gitlab](https://docs.gitlab.com/administration/packages/container_registry/)

```ruby
external_url 'https://gitlab.ci.internal'
registry_external_url 'https://registry.ci.internal:5005'

gitlab_rails['registry_enabled'] = true
gitlab_rails['registry_host'] = 'registry.ci.internal'
gitlab_rails['registry_port'] = '5005'

# Если используется самоподписанный сертификат:
# registry['internal_certificate'] = '/etc/gitlab/ssl/registry.crt'
```

После изменения: `gitlab-ctl reconfigure`

### Шаг 2 — Настроить GitLab Runner

Зарегистрировать runner с executor `docker` на CI-сервере: [dev](https://dev.to/ishmam_abir/cicd-on-local-gitlab-server-setup-gitlab-runner-self-hosted-gitlab-37nf)

```bash
docker run --rm -v /srv/gitlab-runner/config:/etc/gitlab-runner \
  gitlab/gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.ci.internal" \
  --registration-token "$RUNNER_TOKEN" \
  --executor "docker" \
  --docker-image "docker:26" \
  --docker-privileged \
  --docker-volumes "/certs/client" \
  --docker-volumes "/var/run/docker.sock:/var/run/docker.sock" \
  --description "self-hosted-runner" \
  --tag-list "docker,deploy"
```

В `/etc/gitlab-runner/config.toml` добавить доступ к внутреннему реестру:

```toml
[[runners]]
  [runners.docker]
    allowed_pull_policies = ["if-not-present"]
    pull_policy = "if-not-present"
    # Разрешить инсекурный реестр, если без TLS:
    # [runners.docker.allowed_services]
```

### Шаг 3 — GitLab CI/CD Variables (секреты)

В GitLab → Project → Settings → CI/CD → Variables добавить: [docs.gitlab](https://docs.gitlab.com/user/packages/container_registry/build_and_push_images/)

| Переменная | Описание |
|---|---|
| `SSH_PRIVATE_KEY` | Приватный SSH-ключ для доступа к prod-серверу (type: File) |
| `PROD_SERVER_IP` | IP или hostname prod-сервера |
| `PROD_SERVER_USER` | Пользователь (напр., `deploy`) |
| `POSTGRES_PASSWORD` | Пароль БД |
| `SECRET_KEY` | FastAPI secret key |
| `YOOMONEY_SECRET` | Ключ YooMoney |
| `CDEK_CLIENT_SECRET` | Ключ СДЭК |
| `CI_REGISTRY` | Автоматически: `registry.ci.internal:5005` |

### Шаг 4 — `.gitlab-ci.yml`

```yaml
# .gitlab-ci.yml
# Полностью self-hosted: образы хранятся в GitLab Container Registry,
# деплой — по SSH через docker-compose, без Docker Hub.

stages:
  - build
  - test
  - push
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  # Образы именуются через внутренний реестр GitLab
  BACKEND_IMAGE: $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHORT_SHA
  FRONTEND_IMAGE: $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHORT_SHA
  BACKEND_IMAGE_LATEST: $CI_REGISTRY_IMAGE/backend:latest
  FRONTEND_IMAGE_LATEST: $CI_REGISTRY_IMAGE/frontend:latest

# ─────────────────────────────────────────────
# STAGE: build
# ─────────────────────────────────────────────
build:backend:
  stage: build
  image: docker:26
  services:
    - docker:26-dind
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
  script:
    - docker build
        --cache-from "$BACKEND_IMAGE_LATEST"
        --build-arg BUILDKIT_INLINE_CACHE=1
        -t "$BACKEND_IMAGE"
        -t "$BACKEND_IMAGE_LATEST"
        -f backend/Dockerfile
        ./backend
    # Образ сохраняется локально в runner до стадии push
  tags:
    - docker

build:frontend:
  stage: build
  image: docker:26
  services:
    - docker:26-dind
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
  script:
    - docker build
        --cache-from "$FRONTEND_IMAGE_LATEST"
        --build-arg BUILDKIT_INLINE_CACHE=1
        -t "$FRONTEND_IMAGE"
        -t "$FRONTEND_IMAGE_LATEST"
        -f frontend/Dockerfile
        ./frontend
  tags:
    - docker

# ─────────────────────────────────────────────
# STAGE: test
# ─────────────────────────────────────────────
test:backend:
  stage: test
  image: $BACKEND_IMAGE
  services:
    - postgres:16-alpine
    - redis:7-alpine
  variables:
    DATABASE_URL: "postgresql+asyncpg://postgres:postgres@postgres/testdb"
    REDIS_URL: "redis://redis:6379/0"
    POSTGRES_DB: testdb
    POSTGRES_PASSWORD: postgres
  script:
    - cd /app
    - pip install pytest pytest-asyncio httpx
    - pytest tests/ -v --tb=short
  tags:
    - docker

# ─────────────────────────────────────────────
# STAGE: push  — только во внутренний реестр GitLab
# ─────────────────────────────────────────────
push:images:
  stage: push
  image: docker:26
  services:
    - docker:26-dind
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
  script:
    - docker push "$BACKEND_IMAGE"
    - docker push "$BACKEND_IMAGE_LATEST"
    - docker push "$FRONTEND_IMAGE"
    - docker push "$FRONTEND_IMAGE_LATEST"
  tags:
    - docker
  only:
    - main
    - master

# ─────────────────────────────────────────────
# STAGE: deploy — SSH на prod-сервер, docker-compose pull + up
# Без Docker Hub: prod тянет образы только из внутреннего реестра
# ─────────────────────────────────────────────
deploy:production:
  stage: deploy
  image: alpine:3.19
  before_script:
    # Установить SSH-клиент и docker-compose
    - apk add --no-cache openssh-client rsync
    # Настроить SSH-ключ (переменная типа File)
    - chmod 600 "$SSH_PRIVATE_KEY"
    - mkdir -p ~/.ssh
    - ssh-keyscan -H "$PROD_SERVER_IP" >> ~/.ssh/known_hosts
  script:
    # Скопировать актуальный docker-compose.prod.yml на сервер
    - rsync -az -e "ssh -i $SSH_PRIVATE_KEY"
        deploy/docker-compose.prod.yml
        $PROD_SERVER_USER@$PROD_SERVER_IP:/opt/app/docker-compose.prod.yml

    # На prod-сервере: авторизоваться в реестре и поднять контейнеры
    - ssh -i "$SSH_PRIVATE_KEY" $PROD_SERVER_USER@$PROD_SERVER_IP "
        docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY &&
        export BACKEND_IMAGE=$BACKEND_IMAGE &&
        export FRONTEND_IMAGE=$FRONTEND_IMAGE &&
        cd /opt/app &&
        docker-compose -f docker-compose.prod.yml pull &&
        docker-compose -f docker-compose.prod.yml up -d --remove-orphans &&
        docker image prune -f
      "
  environment:
    name: production
    url: https://prod.internal
  tags:
    - docker
  only:
    - main
    - master
  when: manual  # Ручной запуск деплоя в прод
```

### Шаг 5 — `deploy/docker-compose.prod.yml`

```yaml
# deploy/docker-compose.prod.yml
# Образы берутся ТОЛЬКО из внутреннего GitLab Container Registry.
# Переменные BACKEND_IMAGE / FRONTEND_IMAGE выставляются CI/CD.

version: "3.9"

services:
  api:
    image: ${BACKEND_IMAGE}
    restart: unless-stopped
    env_file: /opt/app/.env.prod
    depends_on:
      - postgres
      - redis
    networks:
      - backend_net

  celery_worker:
    image: ${BACKEND_IMAGE}
    command: celery -A app.tasks.celery_app worker -l info -c 4
    restart: unless-stopped
    env_file: /opt/app/.env.prod
    depends_on:
      - redis
      - postgres
    networks:
      - backend_net

  celery_beat:
    image: ${BACKEND_IMAGE}
    command: celery -A app.tasks.celery_app beat -l info
    restart: unless-stopped
    env_file: /opt/app/.env.prod
    depends_on:
      - redis
    networks:
      - backend_net

  frontend:
    image: ${FRONTEND_IMAGE}
    restart: unless-stopped
    networks:
      - frontend_net

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    volumes:
      - pg_data:/var/lib/postgresql/data
    env_file: /opt/app/.env.prod
    networks:
      - backend_net

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --save 60 1 --loglevel warning
    volumes:
      - redis_data:/data
    networks:
      - backend_net

  meilisearch:
    image: getmeili/meilisearch:v1.7
    restart: unless-stopped
    volumes:
      - meili_data:/meili_data
    env_file: /opt/app/.env.prod
    networks:
      - backend_net

  minio:
    image: minio/minio:latest
    restart: unless-stopped
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    env_file: /opt/app/.env.prod
    networks:
      - backend_net

  nginx:
    image: nginx:stable-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - api
      - frontend
    networks:
      - frontend_net
      - backend_net

volumes:
  pg_data:
  redis_data:
  meili_data:
  minio_data:

networks:
  backend_net:
  frontend_net:
```

### Шаг 6 — Мониторинг (self-hosted)

- **Prometheus + Grafana**: собирают метрики FastAPI (`prometheus-fastapi-instrumentator`), PostgreSQL (`postgres_exporter`), Redis (`redis_exporter`), Celery — всё в Docker Compose на том же или отдельном сервере [docs.gitlab](https://docs.gitlab.com/administration/packages/container_registry/)
- **Loki + Promtail**: сбор структурированных логов из контейнеров без внешних сервисов
- **Алерты**: Grafana Alerting → уведомления в Telegram/Email при деградации сервисов

***

## 4. Ключевые паттерны (Best Practices)

- **Repository Pattern**: сервисный слой не работает с БД напрямую — только через репозиторий
- **Dependency Injection**: сессии БД, текущий пользователь, настройки — через `Depends()`
- **Idempotency Keys**: для платёжных операций и создания заказов
- **Optimistic Locking**: при списании остатков через `version` поле в PostgreSQL
- **Event-driven**: изменение статуса заказа → Celery-таска → уведомления, не блокируя HTTP-ответ
- **Circuit Breaker**: для внешних API (СДЭК, YooMoney) — через `tenacity` с exponential backoff
- **CI/CD секреты**: никаких ключей в коде или `docker-compose.yml` — только через GitLab CI/CD Variables и `.env.prod` на сервере, недоступный в репозитории [docs.gitlab](https://docs.gitlab.com/user/packages/container_registry/build_and_push_images/)

***

**Ключевые изменения относительно исходного ТЗ:**

- **Docker Hub → GitLab Container Registry**: все образы строятся и хранятся во встроенном реестре self-hosted GitLab CE, переменные `$CI_REGISTRY`, `$CI_REGISTRY_USER`, `$CI_REGISTRY_PASSWORD` выставляются GitLab автоматически [docs.gitlab](https://docs.gitlab.com/administration/packages/container_registry/)
- **GitHub Actions → GitLab CI/CD**: `.gitlab-ci.yml` с явными стадиями `build → test → push → deploy`
- **Kubernetes → Docker Compose (prod)**: соответствует требованию "собственные серверы без cloud"; Kubernetes остаётся опцией для масштабирования в будущем
- **S3 → MinIO**: self-hosted S3-совместимое хранилище для медиафайлов вместо AWS S3
- **Деплой по SSH**: runner копирует `docker-compose.prod.yml` на prod-сервер и выполняет `docker-compose pull && up` — без прямого доступа runner'а к докер-сокету продакшн-хоста [stackoverflow](https://stackoverflow.com/questions/42676369/gitlab-ci-how-to-deploy-an-application-via-ssh)