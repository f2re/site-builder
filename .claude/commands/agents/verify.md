# /agents:verify

> Запускает полный DoD checklist по всему проекту
> Использование: `/agents:verify`
> Аргументы не требуются.

---

Ты — **системный верификатор** (Gatekeeper). Выполни полный DoD-чеклист:

## Часть 1 — Бэкенд: линтинг и типизация

```bash
cd backend
ruff check app/ --fix && ruff check app/
mypy app/ --ignore-missing-imports
```

Цель: `ruff` → **0 errors**, `mypy` → **Success: no issues found**.

## Часть 2 — БД: целостность миграций

```bash
cd backend
alembic heads         # ожидаем ровно 1 head
alembic check         # модели совпадают с миграциями
```

Цель: одна голова, модели синхронизированы.

## Часть 3 — Интегритет зависимостей

```bash
pip install -r backend/requirements.txt --quiet
```

Цель: нет конфликтов зависимостей.

## Часть 4 — Тесты

```bash
pytest tests/ -x -v --cov=app --cov-report=term-missing
```

Цель: **all green**, coverage `app/services/` > 80%, `app/api/` > 70%.

## Часть 5 — Фронтенд: линт и типы

```bash
cd frontend && npm run lint
cd frontend && npm run type-check
```

Цель: **0 errors**.

## Часть 6 — Инфраструктура: Docker Compose

```bash
docker compose -f docker-compose.yml config
docker compose -f deploy/docker-compose.prod.yml config
```

Цель: оба файла валидны.

## Часть 7 — Безопасность: нет секретов

```bash
# Проверь, что .env.example не содержит реальных секретов:
grep -iE '(password|secret|key)\s*=\s*.{10,}' .env.example | grep -v 'change-me'

# Проверь, что .env не затронут git:
cat .gitignore | grep -c '\.env$'
```

Цель: `.env` в `.gitignore`, нет реальных секретов в `example`.

---

## Вывод результата

Выведи сводную таблицу в формате:

```
────────────────────────────────────────
🔵 /agents:verify — <дата время>
────────────────────────────────────────
☑️ ruff          – 0 errors
☑️ mypy          – 0 issues
☑️ alembic heads – 1 head
☑️ alembic check – OK
☑️ pip install   – no conflicts
☑️ pytest        – X passed, coverage: services=??% api=??%
☑️ npm lint       – 0 errors
☑️ npm type-check – 0 errors
☑️ compose dev   – valid
☑️ compose prod  – valid
☑️ secrets scan  – clean
────────────────────────────────────────
ИТОГ: ✅ DoD пройден | ⚠️ Есть чеки для исправления
```

Если явные ошибки — исправь самостоятельно и повтори чек.
Если требуется вмешательство человека — опиши конкретную проблему.
