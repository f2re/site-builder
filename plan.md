# Техническое задание: Интернет-магазин на FastAPI + Vue

## 1. Архитектурная концепция

Система строится на **модульной Clean Architecture**: каждый домен (товары, заказы, блог, IoT) — изолированный модуль со своими роутерами, схемами, сервисами и репозиториями. Это позволяет масштабировать и тестировать каждый модуль независимо. Асинхронность FastAPI + SQLAlchemy async обеспечивает максимальную производительность на I/O-операциях. [dev](https://dev.to/sanoy24/building-a-robust-e-commerce-api-with-fastapi-a-deep-dive-f5e)

**Технологический стек:**

| Слой | Технология | Обоснование |
|------|-----------|-------------|
| Backend API | FastAPI (Python 3.12+) | Async-first, автодокументация Swagger/ReDoc, type hints  [dev](https://dev.to/wallaceespindola/fastapi-your-fast-and-modern-framework-for-apis-3mmo) |
| ORM | SQLAlchemy 2.x (async) + Alembic | Миграции, type-safe запросы |
| БД основная | PostgreSQL 16 | ACID, JSONB для атрибутов товаров |
| Кэш / Очереди | Redis 7 | Кэш каталога, корзина, инвентарь в реальном времени  [linkedin](https://www.linkedin.com/posts/gabrielcerioni_github-gacerionigabs-redis-online-inventory-guarantee-demo-activity-7373470690210996224-3iI1) |
| Фоновые задачи | Celery + Redis broker | Email/SMS, обновление курсов, обработка заказов  [youtube](https://www.youtube.com/watch?v=23JqBCNn31g) |
| Frontend | Vue 3 + Pinia + Vite | SPA с SSR (Nuxt 3) для SEO блога |
| Контейнеризация | Docker Compose (dev) / Kubernetes (prod) |  [github](https://github.com/FastAPI-MEA/fastapi-template) |
| Поиск | Elasticsearch / Meilisearch | Полнотекстовый поиск товаров |

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
└── docker-compose.yml
```

***

## 3. Этапы разработки

### Этап 1 — Инфраструктура и ядро (2–3 нед.)

- **Docker Compose**: сервисы `api`, `postgres`, `redis`, `celery_worker`, `celery_beat`, `frontend`
- **Конфигурация**: `Pydantic BaseSettings` — все секреты из `.env`, никаких хардкодов [github](https://github.com/zhanymkanov/fastapi-best-practices)
- **БД**: асинхронное подключение через `asyncpg`, сессии через Dependency Injection
- **Аутентификация**: JWT (access + refresh token), хэширование паролей `bcrypt`/`argon2`, ролевая модель (admin, manager, customer) [linkedin](https://www.linkedin.com/posts/manab-pokhrel_building-a-modular-fastapi-backend-with-postgresql-activity-7404617364249464833-oKzI)
- **Логирование**: структурированные логи (JSON) через `structlog`, middleware для каждого запроса
- **Базовая обработка ошибок**: глобальные exception handlers, никаких внутренних деталей в ответах [dev](https://dev.to/sanoy24/building-a-robust-e-commerce-api-with-fastapi-a-deep-dive-f5e)

### Этап 2 — Каталог товаров и инвентарь (2–3 нед.)

**Модели БД:**
- `Category` (дерево через LTREE или Adjacency List), `Product`, `ProductVariant`, `ProductImage`, `StockMovement`
- Атрибуты товаров — через JSONB (динамические характеристики без лишних таблиц)

**Инвентарь (остатки) — Redis + PostgreSQL:**
- PostgreSQL — источник правды (source of record) для остатков
- Redis Hash `stock:{product_id}` — быстрое чтение доступного количества
- При добавлении в корзину — **резервирование через Redis lease** с TTL (например, 30 минут); при истечении — автоматический возврат остатка [linkedin](https://www.linkedin.com/posts/gabrielcerioni_github-gacerionigabs-redis-online-inventory-guarantee-demo-activity-7373470690210996224-3iI1)
- Lua-скрипты для атомарного списания (исключает race conditions)

**API эндпоинты:**
- `GET /products` — пагинация (cursor-based), фильтры по категории/цене/атрибутам, сортировка
- `GET /products/{slug}` — карточка с галереей, характеристиками, отзывами
- `GET /categories` — дерево категорий (кэш Redis, TTL 10 мин)

**Поиск:**
- Интеграция Meilisearch/Elasticsearch: индексация при изменении товара через Celery-таску

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
- Библиотека `aiomoney` (async)  или `yoomoney` [github](https://github.com/AlekseyKorshuk/yoomoney-api)
- `Quickpay` форма для физлиц, ЮKassa для юрлиц
- Проверка подлинности webhook через HMAC-SHA256 подпись
- Идемпотентные обработчики (защита от дублей)

**Интеграция СДЭК v2 API**: [cdek](https://www.cdek.ru/ru/integration/api/)
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
- **Товары**: CRUD продуктов, категорий, управление фото (загрузка в S3/MinIO), импорт/экспорт CSV
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

- **152-ФЗ и GDPR**: шифрование персональных данных (имя, телефон) в БД, политика конфиденциальности, согласие на обработку ПД при регистрации [auth0](https://auth0.com/blog/fastapi-best-practices/)
- **Валидация**: все входные данные через Pydantic-схемы; параметризованные запросы SQLAlchemy (защита от SQL-инъекций)
- **XSS**: санитизация HTML-контента блога через `bleach`
- **Rate Limiting**: `slowapi` (wrapper над limits) на критичных эндпоинтах (login, checkout)
- **HTTPS**: Nginx + Let's Encrypt в продакшене
- **Секреты**: только через переменные окружения (не в коде), rotation через Vault или `.env` + CI/CD secrets

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

**Деплой:**
- CI/CD: GitHub Actions → build Docker image → push to registry → deploy
- Продакшн: Nginx (reverse proxy, SSL termination) → Gunicorn + Uvicorn workers
- Мониторинг: Prometheus + Grafana (метрики FastAPI, PostgreSQL, Redis, Celery)
- Логи: Loki или ELK stack

***

## 4. Ключевые паттерны (Best Practices)

- **Repository Pattern**: сервисный слой не работает с БД напрямую — только через репозиторий [habr](https://habr.com/ru/companies/exness/articles/494370/)
- **Dependency Injection**: сессии БД, текущий пользователь, настройки — через `Depends()` [github](https://github.com/zhanymkanov/fastapi-best-practices)
- **Idempotency Keys**: для платёжных операций и создания заказов
- **Optimistic Locking**: при списании остатков через `version` поле в PostgreSQL
- **Event-driven**: изменение статуса заказа → Celery-таска → уведомления, не блокируя HTTP-ответ [youtube](https://www.youtube.com/watch?v=23JqBCNn31g)
- **Circuit Breaker**: для внешних API (СДЭК, YooMoney) — через `tenacity` с exponential backoff