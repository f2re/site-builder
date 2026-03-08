# 🚗 WifiOBD Site — Интернет-магазин + IoT-дашборд

> **WifiOBD Site** — это современная e-commerce платформа для продажи автомобильной электроники (OBD-адаптеры, телематика) с интегрированной системой управления прошивками (**Dashfirm**), блогом и **IoT-дашбордом** для мониторинга телеметрии в реальном времени.

---

## 📊 Дорожная карта (Roadmap)

| Этап | Модуль | Описание | Статус |
|:---:|:---|:---|:---:|
| 1 | **Core & Infra** | Docker, JWT Auth, RBAC, CI/CD Pipeline | ✅ Готов |
| 2 | **E-Commerce** | Каталог, Корзина, ЮKassa, СДЭК v2 (ПВЗ на карте) | ✅ Готов |
| 3 | **Dashfirm** | Управление прошивками, серийниками и токенами | ✅ Готов |
| 4 | **Migration** | Автоматический импорт данных из OpenCart | ✅ Готов |
| 5 | **SEO & Content** | Sitemap, Schema.org, SSR Meta, Редиректы | ✅ Готов |
| 6 | **IoT Layer** | WebSocket поток, TimescaleDB, Real-time графики | 🔄 В работе |
| 7 | **Search & UX** | Meilisearch синхронизация, Нагрузочные тесты | ⏳ Ожидает |

---

## 🛠 Технологический стек

### Backend (FastAPI)
- **Ядро**: Python 3.12, FastAPI (Async)
- **БД**: PostgreSQL 16 + **TimescaleDB** (для телеметрии)
- **ORM**: SQLAlchemy 2.0 (Mapped types) + Alembic
- **Кэш & Очереди**: Redis 7, Celery + Celery Beat
- **Поиск**: Meilisearch (полнотекстовый поиск)
- **Безопасность**: Fernet (шифрование PII 152-ФЗ), JWT (Refresh Rotation)

### Frontend (Nuxt 3)
- **Framework**: Vue 3 (Composition API), Nuxt 3 (SSR)
- **State**: Pinia
- **UI System**: **Race-Style Design** (Custom UI Kit + Design Tokens)
- **Иконки**: Phosphor Icons (Local bundling через `@nuxt/icon`)
- **SEO**: SSR Meta, JSON-LD Structured Data, Dynamic Sitemap

---

## 📁 Структура проекта

```bash
site-builder/
├── backend/                # 🐍 FastAPI Backend
│   ├── app/
│   │   ├── api/v1/         # Feature-First модули (auth, shop, iot, firmware...)
│   │   ├── core/           # Глобальные настройки и безопасность (Gatekeeper)
│   │   ├── db/             # Модели SQLAlchemy и миграции Alembic
│   │   ├── integrations/   # СДЭК, ЮKassa, Meilisearch
│   │   └── tasks/          # Фоновые задачи Celery (Delivery, SEO, Cleanup)
│   └── tests/              # Pytest (Unit & Integration)
├── frontend/               # ⚡ Nuxt 3 Frontend
│   ├── components/         # UI Kit (U/) и доменные компоненты
│   ├── pages/              # Роутинг и логика страниц
│   ├── stores/             # Состояние Pinia
│   └── assets/css/         # Design Tokens (tokens.css)
├── deploy/                 # 🚀 Конфиги Nginx/Apache, Monitoring
└── .gemini/                # 🤖 Инструкции и задачи для ИИ-агентов
```

---

## 🤖 Мультиагентная разработка (Gemini CLI)

Проект разрабатывается командой ИИ-агентов. Все изменения проходят через **Gatekeeper Protocol**:
- 🧼 **Linting**: Обязательный `ruff` и `mypy` перед каждым коммитом.
- 🧪 **Testing**: Автоматический запуск `pytest` для верификации критических узлов.
- 🛡 **Security**: Шифрование PII и защита миграций от дублирования ENUM.
- 📦 **Dependencies**: Строгий контроль версий в `requirements.txt`.

---

## Быстрый старт

### Вариант A: Docker (рекомендуется для продакшена)

```bash
# Скопировать переменные окружения
cp .env.example .env

# Собрать и запустить все сервисы
docker compose up --build -d

# Применить миграции БД
docker compose exec backend alembic upgrade head

# Создать первого администратора
docker compose run --rm backend python -m app.db.create_admin
```

После старта перейдите на `/admin` (используйте email и пароль из `.env`).

---

### Вариант B: macOS без Docker (для локальной разработки)

**Требования:** macOS 12+, [Homebrew](https://brew.sh), Python 3.12, Node.js 20+, PostgreSQL, Redis.

```bash
# Установить зависимости (один раз)
brew install python@3.12 node postgresql@16 redis

# Запустить PostgreSQL (должен быть доступен на порту 5432)
brew services start postgresql@16

# Первый запуск: создаст .env, установит зависимости, поднимет все сервисы
./scripts/dev_macos.sh
```

Скрипт автоматически:
1. Создаёт `.env` из `.env.example` с localhost-адресами и случайными секретными ключами
2. Создаёт БД `site_builder` и пользователя `sb_user`
3. Применяет Alembic-миграции
4. Устанавливает Python venv и npm-зависимости
5. Запускает в фоне: Meilisearch, Backend (uvicorn --reload), Celery worker, Frontend (Nuxt)

После старта доступно:

| Сервис      | URL                        |
|-------------|----------------------------|
| Frontend    | http://localhost:3000      |
| Backend API | http://localhost:8000      |
| API Docs    | http://localhost:8000/docs |
| Meilisearch | http://localhost:7700      |

Логи сервисов пишутся в `.logs/` (backend.log, frontend.log, celery.log, meilisearch.log).

```bash
# Остановить все сервисы
./scripts/dev_macos.sh stop
```

---

## E2E-тестирование

E2E-тесты используют **Playwright + pytest** и проверяют полный пользовательский сценарий через браузер Chromium.

### Тестовые аккаунты

Создаются скриптом seed автоматически:

| Роль          | Email                      | Пароль       |
|---------------|----------------------------|--------------|
| Администратор | admin@wifiobd-test.ru      | Admin123!    |
| Покупатель    | customer@wifiobd-test.ru   | Customer123! |

### Автоматический запуск (рекомендуется)

Скрипт сам проверит, запущено ли окружение, засеет данные и запустит тесты:

```bash
./scripts/dev_macos.sh e2e
```

### Ручной запуск (если окружение уже запущено)

```bash
# 1. Активировать виртуальное окружение
source backend/.venv/bin/activate

# 2. Установить тестовые зависимости (один раз)
pip install pytest playwright requests
playwright install chromium

# 3. Засеять тестовые данные
cd backend && python -m scripts.seed_e2e && cd ..

# 4. Запустить все тесты с визуальным браузером
pytest tests/e2e/ -v --headed -s -p no:warnings
```

### Запуск отдельных тест-файлов

```bash
# Авторизация
pytest tests/e2e/test_01_auth.py -v --headed -s

# Блог
pytest tests/e2e/test_02_blog.py -v --headed -s

# Управление товарами (нужен admin_page)
pytest tests/e2e/test_03_admin_products.py -v --headed -s

# Каталог магазина
pytest tests/e2e/test_04_shop.py -v --headed -s

# Корзина
pytest tests/e2e/test_05_cart.py -v --headed -s

# Оформление заказа
pytest tests/e2e/test_06_checkout.py -v --headed -s

# История заказов
pytest tests/e2e/test_07_orders.py -v --headed -s

# Один конкретный тест
pytest tests/e2e/test_01_auth.py::test_login_admin_success -v --headed -s
```

### Headless-режим (без GUI, для CI)

```bash
CI=true pytest tests/e2e/ -v -s -p no:warnings
```

### Переменные окружения для тестов

| Переменная      | По умолчанию            | Описание              |
|-----------------|-------------------------|-----------------------|
| `E2E_BASE_URL`  | http://localhost:3000   | URL Nuxt frontend     |
| `E2E_API_URL`   | http://localhost:8000   | URL FastAPI backend   |
| `CI`            | false                   | headless если `true`  |

Пример запуска против другого стенда:

```bash
E2E_BASE_URL=http://staging.example.com \
E2E_API_URL=http://api.staging.example.com \
CI=true pytest tests/e2e/ -v
```

### Структура E2E-тестов

```
tests/e2e/
  conftest.py               — фикстуры: browser, page, admin_page, customer_page
  test_01_auth.py           — вход, регистрация, выход
  test_02_blog.py           — чтение статей
  test_03_admin_products.py — управление товарами через админ-панель
  test_04_shop.py           — каталог, фильтры
  test_05_cart.py           — корзина
  test_06_checkout.py       — оформление заказа (с моком CDEK API)
  test_07_orders.py         — история заказов
  screenshots/              — скриншоты (создаются автоматически при падении теста)
```

### Засев данных без тестов

```bash
./scripts/dev_macos.sh seed
```

### Просмотр логов E2E

```bash
tail -f .logs/e2e.log
```

---

### Вход в Админ-панель

---

## 🚚 Интеграции с провайдерами доставки

Для работы с API служб доставки необходимо получить токены и заполнить переменные окружения в `.env`.

### СДЭК (CDEK)

1. Зарегистрируйтесь в [личном кабинете СДЭК](https://www.cdek.ru/ru/integration)
2. Перейдите в раздел "Интеграция" → "API"
3. Создайте тестовый или боевой аккаунт
4. Скопируйте `Account` и `Secure Password`

```bash
CDEK_ACCOUNT=your_account
CDEK_PASSWORD=your_password
CDEK_API_URL=https://api.cdek.ru/v2  # prod: https://api.cdek.ru/v2, test: https://api.edu.cdek.ru/v2
```

### Почта России

1. Зарегистрируйтесь на [портале разработчиков Почты России](https://otpravka.pochta.ru)
2. Получите доступ к API "Отправка" (требуется договор с Почтой России)
3. В личном кабинете создайте токен доступа и ключ авторизации

```bash
POCHTA_TOKEN=your_token
POCHTA_KEY=your_key
POCHTA_API_URL=https://otpravka-api.pochta.ru
```

### Ozon и Wildberries (C2C доставка)

Ozon и Wildberries используются для C2C доставки через пункты выдачи. API не требуется — пользователь выбирает ПВЗ на карте при оформлении заказа.

**Токены не нужны.** Список ПВЗ хранится в статических данных приложения.

---

## 📐 Принципы кодовой базы
- **152-ФЗ Compliance**: Имена, телефоны и email шифруются в БД (AES-256).
- **Idempotency**: Все платежные и доставочные операции защищены от повторов.
- **Race-Style UI**: Интерфейс ориентирован на скорость, адаптивность (Mobile-First) и спортивную эстетику.
- **SEO Ready**: Автоматическая генерация Sitemap, RSS и JSON-LD разметки.
