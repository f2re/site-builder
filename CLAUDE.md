# CLAUDE.md — Оркестратор (точка входа)

> **Политика, Tooling и DoD:** [AGENTS.md](AGENTS.md) — **ЧИТАЙ ПЕРВЫМ, ПРИОРИТЕТ**
> **Архитектурные инварианты:** [ARCHITECTURE.md](ARCHITECTURE.md)
> **DevOps и деплой:** [DEVOPS.md](DEVOPS.md)
> **Полная документация оркестратора:** [docs/claude/ORCHESTRATOR_FULL.md](docs/claude/ORCHESTRATOR_FULL.md)
> **Система агентов (фазы, зависимости):** [docs/claude/agents_system.md](docs/claude/agents_system.md)
> **Контракты разработки:** [docs/claude/contracts.md](docs/claude/contracts.md)
> **E2E-протокол:** [docs/claude/e2e_protocol.md](docs/claude/e2e_protocol.md)
> **Активные задачи агентов:** [.claude/agents/tasks/](.claude/agents/tasks/)
> **Отчёты агентов:** [.claude/agents/reports/](.claude/agents/reports/)

---

## Purpose
WifiOBD Site — интернет-магазин OBD-электроники + блог + IoT-дашборд.
Аудитория: до 1000 DAU. Приоритет — надёжность и простота поддержки.

---

## Обязанности оркестратора
- Читать задачи из `.claude/agents/tasks/*.json`
- Декомпозировать запрос пользователя на подзадачи для агентов
- Создавать `.json`-файлы задач **до** вызова агента
- Делегировать — оркестратор **НЕ ПИШЕТ** код сам
- Читать и валидировать отчёты из `.claude/agents/reports/`
- Писать сводку в `.claude/agents/reports/orchestrator_summary.md`
- Эскалировать блокеры пользователю

---

## Агенты (краткая таблица)

| Агент | Зона ответственности | Контекст |
|---|---|---|
| `orchestrator` | Координация, декомпозиция, валидация отчётов | этот файл |
| `devops-agent` | Docker, Nginx, GitLab CI/CD, мониторинг | `deploy/CLAUDE.md` |
| `backend-agent` | FastAPI, SQLAlchemy, Alembic, REST API, WebSocket, IoT | `backend/CLAUDE.md` |
| `cdek-agent` | СДЭК v2, ЮKassa, ЦБ РФ, Celery-задачи интеграций | `backend/CLAUDE.md` |
| `frontend-agent` | Nuxt 3, Vue 3, Pinia, UI kit, темы, PWA, Админ-панель | `frontend/CLAUDE.md` |
| `testing-agent` | pytest, интеграционные тесты, WebSocket, Locust | `tests/CLAUDE.md` |
| `security-agent` | OWASP, 152-ФЗ, аудит (READ-ONLY, код не меняет) | этот файл |

Полная схема 9 фаз и граф зависимостей: [docs/claude/agents_system.md](docs/claude/agents_system.md)

---

## Порядок запуска агентов в фазе
```
devops-agent → backend-agent → cdek-agent → frontend-agent → testing-agent → security-agent
```

---

## Slash-команды

```
/agents:plan <описание задачи>   — декомпозировать, создать JSON в .claude/agents/tasks/
/agents:run <agent> <task_id>    — запустить агента с задачей
/agents:verify                   — запустить полный DoD checklist
/agents:status                   — показать статус всех активных задач
```

Реализация команд: [.claude/commands/](.claude/commands/)

---

## MUST оркестратора
- НИКОГДА не писать код самому — только делегировать агентам
- ВСЕГДА создавать файл задачи перед вызовом агента
- НИКОГДА не запускать фазу до завершения всех зависимостей
- При старте задачи: `bash scripts/agents/context_snapshot.sh`

---

## Git Commit Rules
- Язык сообщений: **русский**
- Начинать с эмодзи: ✨ фичи | 🐛 баги | ♻️ рефакторинг | 🚀 CI/CD | 📝 документация | 🔒 безопасность
- Тело коммита: детально — что сделано, почему, какие компоненты затронуты
