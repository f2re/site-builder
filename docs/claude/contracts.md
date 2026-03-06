# contracts.md — Контракты разработки

> Часть документации оркестратора. Точка входа: [CLAUDE.md](../../CLAUDE.md)

---

## 🌐 API Path & BaseURL Policy
1. `apiBase` в `runtimeConfig` **ОБЯЗАН** включать версию (например, `/api/v1`).
2. **ЗАПРЕЩЕНО** вручную добавлять `/api/v1` в пути при использовании `useFetch` с `baseURL: apiBase`.
3. Все пути в композаблах начинаются с `/` относительно `apiBase` (например, `/products`).

---

## 🔐 Auth & Profile Flow Contract
1. Любой эндпоинт авторизации **ОБЯЗАН** возвращать полную `UserResponse` в поле `user` вместе с токенами.
2. В frontend-composables использовать строго `accessToken` (не `token`, не `jwt`).
3. При обновлении `email` бэкенд **ОБЯЗАН** пересчитывать `email_hash` (blind index).

---

## 📱 UI Parity Rule
Любая навигационная ссылка в мобильном меню **ДОЛЖНА** иметь аналог в десктопной версии.

---

## 🏷️ Frontend Naming Conventions
- Для IoT/Телеметрии: `IoTDevice` (в `useIoT.ts`)
- Для Магазина/Прошивок: `FirmwareDevice` (в `firmwareStore.ts`)
- Общие типы (User, Order): единственные в `stores/` или `composables/`
- **ЗАПРЕЩЕНО** имя `Device` напрямую (конфликт Nuxt auto-import)

---

## 📊 IoT / Телеметрия Contract
- Таблица `telemetry` **MUST** быть TimescaleDB hypertable (`chunk_time_interval = '1 day'`)
- WebSocket эндпоинт: `ws://host/ws/iot/{device_id}`
- Данные: Redis Streams → Celery consumer → TimescaleDB
- Дашборд агрегирует через `time_bucket` (не raw SELECT)
- Retention policy: 90 дней (`TELEMETRY_RETENTION_DAYS` в .env)

---

## 🎨 Design Token Contract

```
frontend/assets/css/tokens.css   ← ЕДИНСТВЕННЫЙ источник всех design tokens
frontend/stores/themeStore.ts    ← ЕДИНСТВЕННЫЙ источник состояния темы
```

- `themeStore.toggle()` **MUST** обновлять `document.documentElement.dataset.theme`
- Тема **MUST** сохраняться в `localStorage` key `theme`
- SSR: читать из cookie `theme` (httpOnly=false)
- Тема по умолчанию: `dark`
- Контраст текста: ≥ 4.5:1 (WCAG 2.1 AA) в обеих темах

---

## 🏗 Infrastructure Sync Policy (Docker)
1. **Double Edit Rule**: любые изменения инфраструктуры вносятся в оба файла одновременно:
   - Dev: `docker-compose.yml`
   - Prod: `deploy/docker-compose.prod.yml`
2. `:latest` в prod-образах — **ЗАПРЕЩЕНО**, всегда фиксированные версии.

---

## 🛢 Backend Data Contracts
- Все сервисы POST/PUT/PATCH/DELETE **ОБЯЗАНЫ** вызывать `await session.commit()`
- Перед валидацией Pydantic объект **ДОЛЖЕН** быть загружен со всеми связями (`selectinload` или `refresh`)
- В Celery для async: **ТОЛЬКО** `asyncio.run()` (не `get_event_loop()`)
- Для интеграционных тестов бэкенда: `fakeredis[lua]>=2.20.0`
- Frontend пакеты: `npm install --legacy-peer-deps` (критично для TipTap)
