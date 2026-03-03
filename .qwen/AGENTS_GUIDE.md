# Настройка Qwen Agents для WifiOBD Site

## 📋 Обзор

Система мульти-агентной разработки автоматически регистрируется при старте Qwen CLI. Агенты и slash-команды подтягиваются из директории `.qwen/`.

---

## 🚀 Быстрый старт

### 1. Автоматическая загрузка (рекомендуется)

Агенты загружаются автоматически при каждом запуске Qwen CLI благодаря конфигурации в:
- `.qwen/settings.json`
- `.qwen/agents.yaml`

Ничего делать не нужно — просто начните использовать команды!

### 2. Ручная загрузка (опционально)

```bash
# Загрузить агенты в текущую сессию
source .qwen/scripts/load-agents.sh

# Или зарегистрировать команды
.qwen/scripts/load-agents.sh --register
```

---

## 📁 Структура файлов

```
.qwen/
├── settings.json           # Настройки Qwen CLI + агенты
├── agents.yaml             # Конфигурация агентов (авто-загрузка)
├── agents/                 # Файлы агентов (.md)
│   ├── orchestrator.md
│   ├── backend-agent.md
│   ├── frontend-agent.md
│   ├── devops-agent.md
│   ├── cdek-agent.md
│   ├── testing-agent.md
│   └── security-agent.md
├── commands/               # Slash-команды (.sh)
│   ├── agents/
│   │   ├── plan.sh
│   │   ├── status.sh
│   │   ├── report.sh
│   │   ├── validate.sh
│   │   └── contract.sh
│   ├── shop/
│   │   └── init.sh
│   ├── blog/
│   │   └── init.sh
│   ├── iot/
│   │   └── init.sh
│   └── admin/
│       └── init.sh
├── scripts/
│   └── load-agents.sh      # Скрипт авто-загрузки
└── policies/
    └── agents.toml         # Политики доступа агентов
```

---

## 🔧 Доступные команды

### Управление задачами

| Команда | Описание |
|---------|----------|
| `/agents:plan <задача>` | Декомпозиция задачи на подзадачи для агентов |
| `/agents:status` | Показать статус текущих задач и агентов |
| `/agents:report <task_id>` | Получить отчёт по выполненной задаче |
| `/agents:validate` | Запустить финальную валидацию проекта (Gatekeeper) |
| `/agents:contract <domain>` | Показать контракты для домена |

### Инициализация фаз

| Команда | Описание |
|---------|----------|
| `/shop:init` | Инициализировать новую фазу разработки магазина |
| `/blog:init` | Инициализировать новую фазу разработки блога |
| `/iot:init` | Инициализировать новую фазу разработки IoT-дашборда |
| `/admin:init` | Инициализировать новую фазу разработки админ-панели |

---

## 🤖 Агенты

| Агент | Зона ответственности |
|-------|----------------------|
| `orchestrator` | Координация, декомпозиция задач, валидация отчётов |
| `devops-agent` | Docker, Nginx, GitLab CI/CD, мониторинг |
| `backend-agent` | FastAPI, SQLAlchemy, Alembic, REST API, WebSocket, IoT |
| `cdek-agent` | СДЭК v2, ЮKassa, ЦБ РФ, Celery-задачи интеграций |
| `frontend-agent` | Nuxt 3, Vue 3, Pinia, UI kit, темы, PWA |
| `testing-agent` | pytest, интеграционные тесты, WebSocket, Locust |
| `security-agent` | OWASP, 152-ФЗ, аудит (READ-ONLY) |

---

## 📝 Примеры использования

### 1. Создание новой задачи

```bash
/agents:plan Добавить функционал корзины с резервированием через Redis Lua
```

**Что происходит:**
1. Оркестратор анализирует задачу
2. Создаёт JSON-файлы подзадач в `.qwen/agents/tasks/`
3. Назначает агентов (backend-agent, cdek-agent, frontend-agent)
4. Выводит план выполнения

### 2. Инициализация фазы

```bash
/shop:init
```

**Что происходит:**
1. Создаются задачи для фазы "Магазин"
2. Определяются зависимости между задачами
3. Запускается devops-agent для проверки инфраструктуры
4. backend-agent начинает реализацию

### 3. Проверка статуса

```bash
/agents:status
```

**Вывод:**
- Статус агентов (idle/in_progress/done)
- Активные задачи
- Последние отчёты

### 4. Валидация перед коммитом

```bash
/agents:validate
```

**Проверяется:**
- `alembic heads` — один head
- `alembic check` — синхронизация моделей
- `ruff check` / `mypy` — линтинг backend
- `npm run lint` — линтинг frontend
- `pip install -r requirements.txt` — зависимости
- `pytest` — тесты

---

## ⚙️ Конфигурация

### agents.yaml

```yaml
version: "1.0"
project: "WifiOBD Site"

defaults:
  approval_mode: "auto_edit"
  output_language: "ru"

agents:
  - id: "orchestrator"
    name: "Оркестратор"
    file: ".qwen/agents/orchestrator.md"
    commands:
      - "/agents:plan"
      - "/agents:status"
    active: true

auto_load:
  enabled: true
  directory: ".qwen/agents"
  pattern: "*.md"
```

### settings.json

```json
{
  "agents": {
    "enabled": true,
    "configFile": ".qwen/agents.yaml",
    "autoLoad": true
  },
  "slashCommands": {
    "enabled": true,
    "autoRegister": true
  }
}
```

---

## 🔍 Диагностика

### Проверка конфигурации

```bash
.qwen/scripts/load-agents.sh --validate
```

### Список агентов и команд

```bash
.qwen/scripts/load-agents.sh --list
```

### Помощь

```bash
.qwen/scripts/load-agents.sh --help
```

---

## 🛠 Добавление нового агента

1. Создайте файл `.qwen/agents/<name>-agent.md`:

```markdown
---
name: <name>-agent
description: Описание агента
kind: local
tools: [read_file, write_file, run_shell_command]
---

# AGENT: <name>-agent

Зона ответственности агента...
```

2. Добавьте запись в `.qwen/agents.yaml`:

```yaml
agents:
  - id: "<name>-agent"
    name: "<Name> Агент"
    file: ".qwen/agents/<name>-agent.md"
    commands:
      - "/<name>:action"
    active: true
```

3. Создайте команду `.qwen/commands/<name>/action.sh`:

```bash
#!/usr/bin/env bash
# Command: /<name>:action
# Description: Описание команды

echo "Выполнение команды..."
```

4. Сделайте скрипт исполняемым:

```bash
chmod +x .qwen/commands/<name>/action.sh
```

---

## 📊 Отчёты агентов

Отчёты сохраняются в `.qwen/agents/reports/<agent>/<task_id>.md`

**Обязательные секции:**
```markdown
## Status: DONE

## Completed:
- список выполненного

## Artifacts:
- путь/к/файлу.py

## Contracts Verified:
- Pydantic schemas: ✅

## Next:
- что передать следующему агенту

## Blockers:
- нет
```

---

## 🔐 Политики безопасности

Политики определяются в `.qwen/policies/agents.toml`:

- **read_file, list_directory, glob, grep** — разрешены без подтверждения
- **write_file, replace** — авто-разрешены в режиме `auto_edit`
- **run_shell_command** — зависит от команды (lint/test — разрешены, rm/deploy — спрашивать)

---

## 📚 Дополнительные ресурсы

- [QWEN.md](../QWEN.md) — главный документ проекта
- [plan.md](../plan.md) — детальный план разработки
- [DEVOPS.md](../DEVOPS.md) — инфраструктура и деплой
