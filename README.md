# 🚗 WifiOBD Site — E-Commerce & IoT Ecosystem

[![Backend: FastAPI 0.130+](https://img.shields.io/badge/Backend-FastAPI_0.130+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Frontend: Nuxt 3](https://img.shields.io/badge/Frontend-Nuxt_3-00DC82?style=flat-square&logo=nuxt.js)](https://nuxt.com/)
[![DB: PostgreSQL 16](https://img.shields.io/badge/DB-PostgreSQL_16-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![IoT: TimescaleDB](https://img.shields.io/badge/IoT-TimescaleDB-F37021?style=flat-square&logo=timescaledb)](https://www.timescale.com/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red?style=flat-square)](LICENSE)

**WifiOBD Site** — это высокопроизводительная экосистема для автомобильной электроники, объединяющая современный интернет-магазин, интеллектуальную платформу управления прошивками (**Dashfirm**) и IoT-дашборд для мониторинга телеметрии в реальном времени.

---

## 🏗 Ключевые Возможности и Модули

### 🛒 E-Commerce & Каталог
*   **Умный каталог**: Поддержка иерархических категорий, тегов и динамических атрибутов товаров.
*   **Карточки товаров**: Многовариантные товары с выбором опций (цвет, тип адаптера, комплектность), галереи изображений и видео.
*   **Meilisearch Integration**: Мгновенный полнотекстовый поиск с поддержкой опечаток и фильтрацией по атрибутам.
*   **Оформление заказа**: Гибкая корзина, расчет стоимости доставки в реальном времени и интеграция с **ЮKassa**.

### 📦 Логистика и Доставка (CDEK, Ozon, WB, Почта)
*   **СДЭК v2**: Полная интеграция с расчетом тарифов, выбором ПВЗ на карте и созданием накладных.
*   **Ozon Delivery & Wildberries (WB)**: Поддержка популярных маркетплейс-доставщиков.
*   **Почта России**: Автоматический расчет стоимости по API.

### 📝 Блог и CMS на базе TipTap
*   **TipTap Editor**: Продвинутый визуальный редактор с поддержкой JSON/HTML формата, вставкой медиа-файлов и блоков кода.
*   **SEO & Analytics**: Автоматическая генерация мета-тегов, расчет времени чтения, система категорий и тегов.
*   **Интерактив**: Встроенная система комментариев с древовидной структурой.

### ⚙️ Dashfirm Engine (Firmware Management)
*   **Управление девайсами**: Учет серийных номеров, привязка токенов доступа и управление парком OBD-адаптеров.
*   **OTA Обновления**: Хранилище прошивок с версионированием, историей изменений и безопасной раздачей по токенам.

### 📊 IoT Dashboard & Telemetry
*   **Real-time Stream**: Обработка потока данных телеметрии через **Redis Streams**.
*   **TimescaleDB**: Эффективное хранение временных рядов (метрики авто, GPS, ошибки OBD).
*   **WebSockets**: Мгновенное обновление графиков и показателей в личном кабинете пользователя.

### 🚀 Migration Engine (OpenCart Legacy Support)
*   **Seamless Migration**: Мощный инструмент для переноса данных из OpenCart (Товары, Категории, Клиенты, Заказы, Статьи).
*   **SEO Preservation**: Автоматическая система 301-редиректов для сохранения позиций в поисковой выдаче после миграции.

---

## 🛡 Security & Privacy (152-ФЗ)

Проект спроектирован с учетом строгих требований безопасности:
*   **PII Encryption**: Шифрование персональных данных (имена, телефоны, адреса) на уровне БД с использованием AES-256 (Fernet).
*   **RBAC**: Гибкая система ролей (Admin, Manager, User, IoT-Device).
*   **JWT Security**: Ротация Refresh-токенов и защита от CSRF/XSS.

---

## 🛠 Технологический стек

### Backend (FastAPI)
- **Core**: Python 3.12, FastAPI, Pydantic v2
- **Database**: PostgreSQL 16 + **TimescaleDB**
- **Search**: Meilisearch (Instant Search)
- **Messaging**: Redis Streams & Pub/Sub
- **Background**: Celery + Redis

### Frontend (Nuxt 3)
- **Framework**: Vue 3 (Composition API), Nuxt 3 (SSR Mode)
- **State**: Pinia
- **Editor**: TipTap Rich Text Editor
- **UI**: Custom **Race-Style UI** (Mobile-First, Optimized for Performance)

---

## 📁 Структура проекта

```bash
site-builder/
├── backend/                # 🐍 FastAPI Application
│   ├── app/
│   │   ├── api/v1/         # Feature routers (shop, blog, iot, firmware, migration)
│   │   ├── db/             # Models, Migrations (Alembic), OpenCart adapters
│   │   ├── integrations/   # CDEK, Ozon, WB, Pochta, YooMoney, Meilisearch
│   │   └── tasks/          # Background processing (Celery & Streams)
├── frontend/               # ⚡ Nuxt 3 Application
│   ├── components/         # Atomic UI & Domain blocks (Blog, Shop, IoT)
│   ├── pages/              # SSR-enabled routing
│   └── stores/             # Pinia state (Cart, Auth, User)
├── deploy/                 # 🚀 Docker & Nginx configurations
└── .gemini/                # 🤖 AI-Agent Orchestration (Gemini CLI)
```

---

## 🚀 Быстрый старт

### macOS / Linux (Local)

```bash
cp .env.example .env
./scripts/dev_macos.sh
```

**После запуска:**
*   **Frontend**: [http://localhost:3000](http://localhost:3000)
*   **API Docs**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

## 🧪 Качество и Тестирование

*   **E2E**: Playwright (Full checkout & IoT flows).
*   **Linters**: `ruff` и `mypy` для чистоты кода.
*   **Security**: Регулярные аудиты через `security-agent`.

---

## 🤖 Команда разработки (AI-Driven)

Проект разрабатывается с использованием **Gemini CLI** — мультиагентной системы, где специализированные агенты (Backend, Frontend, DevOps) работают в тесной связке под контролем **Orchestrator**.

---
© 2026 WifiOBD Team. Все права защищены.
