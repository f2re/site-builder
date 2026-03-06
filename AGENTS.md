# AGENTS.md — Policy Gateway

> Читается ПЕРВЫМ перед любым действием.
> Детали стека и инварианты: [ARCHITECTURE.md](ARCHITECTURE.md)
> DevOps детали: [DEVOPS.md](DEVOPS.md)
> Полный контекст оркестратора: [.claude/ORCHESTRATOR.md](.claude/ORCHESTRATOR.md)
> Reference-примеры: [docs/examples/](docs/examples/)

---

## Purpose
WifiOBD Site — интернет-магазин OBD-электроники (до 1000 DAU).
Backend: FastAPI + PostgreSQL/TimescaleDB + Redis + Meilisearch.
Frontend: Nuxt 3 SSR + Vue 3 + Pinia.

---

## Иерархия истины (приоритет: сверху → вниз)
1. **Enforcement** — CI/CD, ruff, mypy, vue-tsc, pytest (нарушение = сборка падает)
2. **Policy** — этот файл (AGENTS.md)
3. **Architecture** — ARCHITECTURE.md (слои, инварианты)
4. **Operations** — DEVOPS.md / docs/runbook.md (dev/deploy/debug)
5. **Examples** — docs/examples/ (эталонные endpoint, тест, PR, миграция)

---

## Tooling — обязательные команды

```bash
# Backend (из директории /backend):
ruff check app/ --fix && ruff check app/ && mypy app/ --ignore-missing-imports

# Frontend (из директории /frontend):
npm run lint

# База данных:
alembic check && alembic heads

# Тесты:
pytest tests/ -x -v
```

---

## Рабочий цикл агента (4 фазы — ОБЯЗАТЕЛЬНЫ)

### Фаза 1 — PLAN [режим: xhigh reasoning]
**НЕ ПИШИ КОД.** Только:
- Прочитай задачу и этот файл
- Изучи затронутые файлы (`grep_search`, `glob`, `read_file`)
- Сформулируй план в 5–10 шагах
- Опиши стратегию верификации (какие команды докажут готовность)

### Фаза 2 — IMPLEMENT [режим: high reasoning]
- Пиши код с учётом тестируемости
- Создавай unit-тесты параллельно с кодом (не в конце)

### Фаза 3 — VERIFY [режим: xhigh reasoning]
- Запусти ВСЕ команды из Tooling выше
- Проверь полный вывод — не «пробегай глазами»
- Сверь результат с Definition of Done ниже

### Фаза 4 — FIX
- Исправляй по конкретным ошибкам из Фазы 3
- Повторяй с Фазы 3 до полного соответствия DoD

> ⚠️ Если один файл правился 3+ раза — рассмотри другой подход целиком.

---

## MUST
- Проходить все 4 фазы в каждой задаче
- Запускать tooling-команды перед каждым коммитом
- Новый endpoint → только в `backend/app/api/v1/<feature>/` со структурой router/service/repository/schemas
- Новые зависимости → только с точной версией в `requirements.txt`, проверить `pip install -r requirements.txt`
- Изменения инфраструктуры → в оба файла одновременно: `docker-compose.yml` + `deploy/docker-compose.prod.yml`
- Docker images → только фиксированные версии (например `v1.36.0`)
- Писать отчёт в `.claude/agents/reports/<domain>/<task_id>.md` по шаблону ниже
- При старте сессии: `python .claude/hooks/local_context.py`
- Перед DONE: `python .claude/hooks/pre_completion.py <task_id>`
- После правки файла: `python .claude/hooks/loop_detector.py --record <filepath>`

## MUST NOT
- Коммитить `.env` или любые секреты
- Хардкодить цвета/отступы в `.vue` (только CSS-переменные из `tokens.css`)
- Менять `backend/app/core/` без unit-тестов
- Использовать GitHub Actions (только GitLab CI/CD)
- Использовать Docker Hub (только GitLab Container Registry)
- Использовать `:latest` в docker images
- Дублировать типы вне `api/v1/<feature>/`
- Вручную добавлять `/api/v1` в пути при использовании `useFetch` с `baseURL: apiBase`
- Запускать фазу до завершения всех её зависимостей

---

## Definition of Done (DoD)

Задача считается выполненной ТОЛЬКО при выполнении всех пунктов:

- [ ] `ruff check app/` → **0 errors**
- [ ] `mypy app/ --ignore-missing-imports` → **Success: no issues found**
- [ ] `npm run lint` → **no errors** (vue-tsc)
- [ ] `pytest tests/` → **all green**
- [ ] `alembic check` → **OK** (модели совпадают с миграциями)
- [ ] `alembic heads` → **ровно 1 head**
- [ ] `python .claude/hooks/pre_completion.py <task_id>` → **DoD пройден**
- [ ] Отчёт агента написан в `.claude/agents/reports/<domain>/<task_id>.md`

---

## Observability — цикл стабилизации

- Каждая агентская сессия логируется в `.claude/logs/<task_id>.log`
- При повторяющейся ошибке: формулируй правило MUST/MUST NOT → добавляй в этот файл → закрепляй в CI
- Ошибка агента — сигнал о недостатке в harness, а не о глупости модели
- Запускай `python .claude/hooks/local_context.py` для диагностики окружения

---

## Шаблон отчёта агента

```markdown
## Status: DONE | IN_PROGRESS | BLOCKED
## Completed:
- список выполненного
## Artifacts:
- backend/app/api/v1/products/router.py
## Contracts Verified:
- Pydantic schemas: ✅
- DI via Depends: ✅
- ruff: ✅ | mypy: ✅ | pytest: ✅
## Next:
- передать frontend-agent: API контракт /api/v1/products готов
## Blockers:
- нет
```
