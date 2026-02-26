# PROJECT: FastAPI E-Commerce + Blog + IoT

## Stack
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.x (async), Alembic
- DB: PostgreSQL 16 + Redis 7
- Frontend: Vue 3 + Pinia + Nuxt 3
- Tasks: Celery + Redis broker
- Integrations: CDEK v2 API, YooMoney/aiomoney, ЦБ РФ

## Coding Contracts (Design-by-Contract)
1. Все эндпоинты MUST иметь Pydantic-схемы (Request + Response)
2. Все сервисы MUST принимать зависимости через DI (Depends)
3. Все внешние API-вызовы MUST иметь retry через tenacity
4. Все репозитории MUST использовать параметризованные запросы (no raw SQL)
5. Все агенты MUST писать отчёт в .gemini/agents/reports/<domain>/<task_id>.md

## Report Contract
Каждый отчёт агента ОБЯЗАН содержать секции:
- ## Status: DONE | IN_PROGRESS | BLOCKED
- ## Completed: (список выполненного)
- ## Artifacts: (список созданных файлов)
- ## Contracts Verified: (какие контракты выполнены)
- ## Next: (что передать следующему агенту)
- ## Blockers: (если есть)

## Agent Invocation
Агенты вызываются: @orchestrator, @backend-agent, @frontend-agent,
@security-agent, @testing-agent, @cdek-agent, @devops-agent
