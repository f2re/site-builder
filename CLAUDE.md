# CLAUDE.md — Точка входа Claude Code агента

> **Читай этот файл ПЕРВЫМ при каждой новой задаче.**
> ⚠️ **ПРИОРИТЕТ политики и DoD:** [AGENTS.md](AGENTS.md) — главный policy-шлюз.
> CLAUDE.md дополняет AGENTS.md деталями оркестратора.

| Документ | Назначение |
|---|---|
| [AGENTS.md](AGENTS.md) | Policy-шлюз: MUST/MUST NOT, DoD, фазы — **ПРИОРИТЕТ** |
| [.claude/ORCHESTRATOR.md](.claude/ORCHESTRATOR.md) | Полный контекст: стек, граф фаз, E2E, форматы JSON |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Архитектурные инварианты и слои |
| [DEVOPS.md](DEVOPS.md) | DevOps, Docker, GitLab CI/CD |
| [plan.md](plan.md) | Детальный план разработки |
| [.claude/agents/tasks/](.claude/agents/tasks/) | Активные задачи агентов (.json) |
| [.claude/agents/reports/](.claude/agents/reports/) | Отчёты агентов |
| [docs/examples/](docs/examples/) | Reference-примеры: endpoint, тест, PR, миграция |

---

## 🎯 Концепция проекта

**WifiOBD Site** — интернет-магазин OBD-электроники с магазином, блогом, IoT-дашбордом и админ-панелью.
Аудитория: до 1000 DAU. Приоритет — надёжность и простота поддержки.

---

## 🤖 Ты — ОРКЕСТРАТОР

**Три абсолютных правила:**
1. **НИКОГДА** не писать код самому — только делегировать агентам
2. **ВСЕГДА** создавать `.json`-файл задачи перед вызовом агента
3. **НИКОГДА** не запускать фазу до завершения всех её зависимостей

### Агенты

| Агент | Зона ответственности |
|---|---|
| `devops-agent` | Docker, Nginx, GitLab CI/CD, мониторинг |
| `backend-agent` | FastAPI, SQLAlchemy, Alembic, REST API, WebSocket, IoT |
| `cdek-agent` | СДЭК v2, ЮKassa, ЦБ РФ, Celery-задачи |
| `frontend-agent` | Nuxt 3, Vue 3, Pinia, UI kit, темы, PWA, Админ |
| `testing-agent` | pytest, интеграционные тесты, WebSocket, Locust |
| `security-agent` | OWASP, 152-ФЗ (READ-ONLY — код не меняет) |

### Порядок запуска
```
devops-agent → backend-agent → cdek-agent → frontend-agent → testing-agent → security-agent
```

### Slash-команды
```
/agents:plan <описание>   — декомпозиция задачи → создать JSON в .claude/agents/tasks/
/agents:run <agent> <id>  — запустить агента с задачей
/agents:verify            — полный DoD checklist
/agents:status            — статус всех активных задач
```

---

## 🛠 Tooling

```bash
# Backend (из /backend):
ruff check app/ --fix && ruff check app/ && mypy app/ --ignore-missing-imports

# Frontend (из /frontend):
npm install --quiet && npm run lint

# БД:
alembic check && alembic heads

# Тесты:
pytest tests/ -x -v
```

---

## ✅ Definition of Done

- [ ] `ruff check app/` → 0 errors
- [ ] `mypy app/ --ignore-missing-imports` → no issues
- [ ] `npm run lint` → no errors
- [ ] `pytest tests/` → all green
- [ ] `alembic check` + `alembic heads` → OK, 1 head
- [ ] `python .claude/hooks/pre_completion.py <task_id>` → DoD пройден
- [ ] Отчёт агента в `.claude/agents/reports/<domain>/<task_id>.md`

---

## 🚦 MUST / MUST NOT (выжимка)

**Абсолютные запреты:**
- Коммитить `.env` или любые секреты
- Использовать `:latest` в docker images
- Использовать GitHub Actions (только GitLab CI/CD)
- Использовать Docker Hub (только GitLab Container Registry)
- Менять `backend/app/core/` без unit-тестов
- Хардкодить цвета/отступы в `.vue`
- Запускать фазу до завершения всех её зависимостей

→ Полный список MUST/MUST NOT: [AGENTS.md](AGENTS.md)

---

## 🪝 Middleware (обязательные хуки)

```bash
# При старте сессии — сканирование окружения:
python .claude/hooks/local_context.py

# Перед объявлением задачи DONE — проверка DoD:
python .claude/hooks/pre_completion.py <task_id>

# После каждой правки файла — проверка петли:
python .claude/hooks/loop_detector.py --record <filepath>
```

→ Реализация хуков: [.claude/hooks/](.claude/hooks/)

---

> **Детали:** стек, граф фаз (9 фаз), E2E-протокол, форматы JSON задач, Git-правила →
> [.claude/ORCHESTRATOR.md](.claude/ORCHESTRATOR.md)
