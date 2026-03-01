# WifiOBD: Карта проекта

**Статус:** 🟢 Core, Shop, Migration, Dashfirm, SEO — ГОТОВЫ. Вектор: IoT.

---

## 🚀 Реализовано
- **Инфраструктура**: Docker (prod), CI/CD, PG16, Redis, Meilisearch.
- **Безопасность**: JWT, 152-ФЗ (Encryption), Gatekeeper Protocol.
- **Магазин**: ЮKassa, СДЭК v2 (Карта ПВЗ), Резервирование остатков.
- **Миграция**: Авто-импорт из OpenCart (Users, Catalog, Orders).
- **Dashfirm**: Прошивки, токены, CLI компилятор.
- **SEO & Content**: Sitemap, JSON-LD, Редиректы, Reading Time.

---

## 🎯 Бэклог (В работе)

### 1. IoT & Телеметрия
- WebSocket поток данных (`/ws/iot/`).
- TimescaleDB hypertable для `telemetry`.
- Real-time графики в кабинете пользователя.

### 2. Поиск & UX
- Синхронизация Meilisearch (товары/статьи).
- Живые фильтры в каталоге.
- Древовидные комментарии в блоге.

### 3. Аналитика
- Дашборд продаж в админке.
- Логирование действий администраторов.

---

## 📍 Ресурсы
- **API Swagger**: `https://m.wifiobd.ru/docs`
- **Admin**: `/admin/`
- **Software**: `/software/`
