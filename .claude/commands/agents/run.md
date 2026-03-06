# /agents:run

> Запускает агента с указанной задачей (полный 4-фазовый цикл)
> Использование: `/agents:run <agent> <task_id>`
> Пример: `/agents:run backend-agent p2_backend_001`

---

Ты — агент **$ARGUMENTS** (формат: `<agent> <task_id>`).

Действуй строго по 4-фазовому циклу:

---

## ФАЗА 1 — PLAN [максимальный reasoning]

**НЕ ПИШИ КОД.**

1. Прочитай файл задачи `/.claude/agents/tasks/<task_id>.json`
2. Прочитай свой subdirectory CLAUDE.md:
   - `backend-agent` → `backend/CLAUDE.md`
   - `frontend-agent` → `frontend/CLAUDE.md`
   - `testing-agent` → `tests/CLAUDE.md`
   - `devops-agent` → `deploy/CLAUDE.md`
   - `security-agent`, `cdek-agent` → `/CLAUDE.md`
3. Прочитай `/.claude/agents/contracts/api_contracts.md` (если есть)
4. Проверь зависимости: все `depends_on` из JSON-файла должны иметь `Status: DONE` в отчёте
   - Если нет — ОСТАНОВИСЬ и сообщи: «Блокер: задача `<id>` зависит от `<dep_id>`, которая [ещё не выполнена]»
5. Посмотри существующие файлы в зоне ответственности (не переписывай без необходимости)
6. Составь план в 5–10 нумерованных шагов
7. Опиши стратегию верификации

---

## ФАЗА 2 — IMPLEMENT

- Реализуй только то, что в плане из Фазы 1
- Создавай тесты параллельно с кодом, не в конце
- Если файл правился 3+ раза — **СТОП**, пересмотри подход
- Соблюдай coding contracts из своего `CLAUDE.md`

---

## ФАЗА 3 — VERIFY [максимальный reasoning]

Выполни ВСЕ команды, дождись полного вывода каждой:

```bash
# Backend (backend-agent, cdek-agent, security-agent):
cd backend && ruff check app/ --fix && ruff check app/
cd backend && mypy app/ --ignore-missing-imports
cd backend && alembic check && alembic heads
pytest tests/ -x -v

# Frontend (frontend-agent):
cd frontend && npm run lint
cd frontend && npm run type-check

# DevOps (devops-agent):
docker compose -f docker-compose.yml config
docker compose -f deploy/docker-compose.prod.yml config
```

Сверь каждый пункт с `acceptance_criteria` из JSON-задачи.

---

## ФАЗА 4 — FIX

- Исправляй строго по ошибкам из Фазы 3 (не угадывай)
- После каждого исправления → снова Фаза 3
- Повторяй до полного соответствия DoD

---

## После завершения — Напиши отчёт

Save report to `/.claude/agents/reports/<domain>/<task_id>.md` using the template from your `CLAUDE.md`.

Required sections: **Status · Completed · Artifacts · Contracts Verified · Next · Blockers**

```markdown
## Status: DONE
## Completed:
- ...
## Artifacts:
- ...
## Contracts Verified:
- ruff: ✅ | mypy: ✅ | pytest: ✅
## Next:
- ...
## Blockers:
- none
```

> Если `Status: BLOCKED` — обязательно опиши причину и требуемое действие в разделе Blockers.
