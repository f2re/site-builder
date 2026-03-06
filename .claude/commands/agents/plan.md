# /agents:plan

> Создаёт JSON-файлы задач для агентов в `.claude/agents/tasks/`
> Использование: `/agents:plan <описание задачи>`

---

Ты — **ОРКЕСТРАТОР**. Тебе поступила задача: **$ARGUMENTS**

Выполни следующее, без написания кода:

## ШАГ 1 — Прочитай контекст

1. Прочитай `/CLAUDE.md` — граф фаз, агенты, DoD, MUST/MUST NOT
2. Прочитай `/.claude/agents/contracts/api_contracts.md` (если существует)
3. Просмотри существующие задачи в `/.claude/agents/tasks/` — избегай дублирования
4. Просмотри последние отчёты в `/.claude/agents/reports/` — узнай, что уже готово

## ШАГ 2 — Декомпозиция

Декомпозируй задачу `$ARGUMENTS` на подзадачи для конкретных агентов:

| Агент | Зона ответственности |
|---|---|
| `devops-agent` | Docker, Nginx, GitLab CI/CD, мониторинг |
| `backend-agent` | FastAPI, SQLAlchemy, Alembic, REST API, IoT |
| `cdek-agent` | СДЭК, ЮКасса, ЦБ РФ, Celery |
| `frontend-agent` | Nuxt 3, Vue 3, Pinia, UI kit, темы |
| `testing-agent` | pytest, e2e, WebSocket, Locust |
| `security-agent` | OWASP-аудит (READ-ONLY) |

Порядок запуска в фазе: `devops → backend → cdek → frontend → testing → security`

## ШАГ 3 — Создай JSON-файлы задач

Для каждой подзадачи создай файл `/.claude/agents/tasks/<phase>_<agent>_<id>.json`:

```json
{
  "task_id": "p<N>_<agent>_<NNN>",
  "phase": <N>,
  "agent": "<agent-name>",
  "title": "Краткое название задачи",
  "description": "Подробное описание: что нужно сделать, в каких файлах",
  "depends_on": ["<task_id_предшествующей>"],
  "priority": "high | medium | low",
  "contracts_required": [".claude/agents/contracts/api_contracts.md"],
  "acceptance_criteria": [
    "Пункт DoD 1",
    "Пункт DoD 2"
  ]
}
```

**Правила нумерации:**
- `task_id` — `p<номер_фазы>_<агент>_<001..999>`
- Номер фазы — по графу из CLAUDE.md (Фаза 1 = инфра, 2 = backend core, ..., 9 = security)
- `phase` — целое число
- `depends_on` — `[]` если зависимостей нет

## ШАГ 4 — Выведи план

После создания всех файлов выведи сводную таблицу:

```
✔️ План декомпозиции: "<описание>"

Созданы задачи:
  1. <task_id> [агент>] — <название>
  2. <task_id> [агент>] — <название> (зависит от: <id>)
  ...

Для запуска первой задачи:
  /agents:run <agent> <task_id>
```

> ОРКЕСТРАТОР НИКОГДА НЕ ПИШЕТ КОД САМ.
> НИКОГДА не запускай фазу до завершения всех зависимостей.
