# ARCHITECTURE.md — Архитектурные инварианты

> Это канон архитектуры. Нарушение любого инварианта = блокировка PR.

## Слои (зависимости только «вперёд»)

```
Types → Config → Repository → Service → Router → UI
```

- **Types** (`schemas.py`) — Pydantic-модели, нет зависимостей
- **Config** (`core/config.py`) — pydantic-settings, только Types
- **Repository** (`repository.py`) — SQLAlchemy async CRUD, только Types + Config
- **Service** (`service.py`) — бизнес-логика, использует Repository через DI
- **Router** (`router.py`) — FastAPI endpoints, использует Service через Depends
- **UI** (frontend) — потребляет Router через REST/WS

## Cross-cutting (единственный способ)
Авторизация, телеметрия, feature flags → только через `app/core/dependencies.py` (Providers)

## Инварианты модулей

| Слой | Расположение | Запрещено |
|---|---|---|
| Модели SQLAlchemy | `backend/app/db/models/` | Дублировать в других папках |
| Pydantic-схемы | `backend/app/api/v1/<feature>/schemas.py` | `app/schemas/` в корне |
| Бизнес-логика | `backend/app/api/v1/<feature>/service.py` | `app/services/` в корне |
| Кросс-доменная | `backend/app/core/` или `app/tasks/` | В feature-папках |
| Design tokens | `frontend/assets/css/tokens.css` | Инлайн в `.vue` |
| Состояние темы | `frontend/stores/themeStore.ts` | В компонентах |

## Обязательная структура каждой feature

```
backend/app/api/v1/<feature>/
├── router.py      # FastAPI routes ( @router.get/post/...)
├── service.py     # Бизнес-логика, принимает зависимости через DI
├── repository.py  # CRUD через SQLAlchemy async, параметризованные запросы
└── schemas.py     # Отдельные Request + Response Pydantic-модели
```

## Проверяемые линтером правила
- Файлы >500 строк → линтер предупреждает, нужно разбить
- `import` из `app/models/` (не `app/db/models/`) → ошибка
- `raw SQL` в `repository.py` → ошибка
- Цвета в `.vue` вне `var(--*)` → ошибка