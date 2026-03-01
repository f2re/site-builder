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
| 5 | **IoT Layer** | WebSocket поток, TimescaleDB, Real-time графики | 🔄 В работе |
| 6 | **SEO & Content** | Dynamic Sitemap, JSON-LD, SSR Meta, Блог | 🔄 В работе |
| 7 | **QA & Search** | Meilisearch синхронизация, Нагрузочные тесты | ⏳ Ожидает |

---

## 🛠 Технологический стек

### Backend (FastAPI)
- **Ядро**: Python 3.12, FastAPI (Async)
- **БД**: PostgreSQL 16 + **TimescaleDB** (для телеметрии)
- **ORM**: SQLAlchemy 2.0 (Mapped types) + Alembic
- **Кэш & Очереди**: Redis 7, Celery + Celery Beat
- **Поиск**: Meilisearch (полнотекстовый поиск)
- **Безопасность**: Fernet (шифрование 152-ФЗ), JWT (Refresh Rotation)

### Frontend (Nuxt 3)
- **Framework**: Vue 3 (Composition API), Nuxt 3 (SSR)
- **State**: Pinia
- **UI System**: **Race-Style Design** (Custom UI Kit + Design Tokens)
- **Иконки**: Phosphor Icons (Local bundling через `@nuxt/icon`)
- **Карты**: Yandex Maps API integration

---

## 📁 Структура проекта

```bash
site-builder/
├── backend/                # 🐍 FastAPI Backend
│   ├── app/
│   │   ├── api/v1/         # Feature-First модули (auth, shop, iot, firmware...)
│   │   ├── core/           # Глобальные настройки и безопасность
│   │   ├── db/             # Модели SQLAlchemy и миграции Alembic
│   │   ├── integrations/   # СДЭК, ЮKassa, Meilisearch, CRM
│   │   └── tasks/          # Фоновые задачи Celery
│   └── tests/              # Pytest (Unit & Integration)
├── frontend/               # ⚡ Nuxt 3 Frontend
│   ├── components/         # UI Kit (U/) и доменные компоненты
│   ├── pages/              # Роутинг и логика страниц
│   ├── stores/             # Состояние Pinia
│   └── assets/css/         # Design Tokens (tokens.css)
├── deploy/                 # 🚀 Конфиги Nginx, Monitoring (Prometheus/Loki)
└── .gemini/                # 🤖 Инструкции и задачи для ИИ-агентов
```

---

## 🤖 Мультиагентная разработка (Gemini CLI)

Проект разрабатывается командой ИИ-агентов. Все изменения проходят через **Gatekeeper Protocol**:
- 🧼 **Linting**: Обязательный `ruff` и `mypy` перед каждым коммитом.
- 🧪 **Testing**: Автоматический запуск `pytest` для верификации критических узлов.
- 🛡 **Security**: Шифрование PII и защита миграций от дублирования ENUM.

---

## 🚀 Быстрый старт

### 1. Окружение
Скопируйте шаблон переменных и заполните их:
```bash
cp .env.example .env
```

### 2. Запуск в Docker (Recommended)
```bash
# Сборка и запуск всех сервисов
docker compose up --build -d

# Применение миграций БД
docker compose exec backend alembic upgrade head

# Создание первого администратора
docker compose run --rm backend python -m app.db.create_admin
```

### 3. Локальная разработка
**Backend**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

---

## ⚡ Полезные команды

- `alembic revision --autogenerate -m "msg"` — создать миграцию.
- `ruff check app/ --fix` — исправить ошибки линтинга.
- `npm run lint` — проверить типы и стиль фронтенда.
- `pytest --cov=app` — запустить тесты с отчетом о покрытии.

---

## 📐 Принципы кодовой базы
- **152-ФЗ Compliance**: Имена, телефоны и email шифруются в БД (AES-256).
- **Idempotency**: Все платежные и доставочные операции защищены от повторов.
- **Race-Style UI**: Интерфейс ориентирован на скорость, адаптивность и спортивную эстетику.
