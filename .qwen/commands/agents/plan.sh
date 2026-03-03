#!/usr/bin/env bash
# Command: /agents:plan
# Description: Декомпозиция задачи на подзадачи для агентов
# Usage: /agents:plan <описание задачи>

set -euo pipefail

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Пути
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TASKS_DIR="$PROJECT_ROOT/.qwen/agents/tasks"
REPORTS_DIR="$PROJECT_ROOT/.qwen/agents/reports"

# Проверка аргументов
if [ $# -lt 1 ]; then
    echo -e "${RED}Ошибка: Не указано описание задачи${NC}"
    echo ""
    echo "Использование:"
    echo "  /agents:plan <описание задачи>"
    echo ""
    echo "Примеры:"
    echo "  /agents:plan Добавить функционал корзины с Redis"
    echo "  /agents:plan Реализовать WebSocket для IoT телеметрии"
    echo "  /agents:plan Настроить CI/CD пайплайн для production"
    exit 1
fi

# Объединяем все аргументы в одно описание
TASK_DESCRIPTION="$*"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  QWEN Agents: Планирование задачи                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Задача:${NC} $TASK_DESCRIPTION"
echo ""

# Создаем дирекории если не существуют
mkdir -p "$TASKS_DIR"
mkdir -p "$REPORTS_DIR"
mkdir -p "$REPORTS_DIR/orchestrator"
mkdir -p "$REPORTS_DIR/backend"
mkdir -p "$REPORTS_DIR/frontend"
mkdir -p "$REPORTS_DIR/devops"
mkdir -p "$REPORTS_DIR/testing"
mkdir -p "$REPORTS_DIR/security"
mkdir -p "$REPORTS_DIR/cdek"

# Генерируем ID задачи
TASK_ID="task_$(date +%Y%m%d_%H%M%S)"
TASK_FILE="$TASKS_DIR/${TASK_ID}.json"

# Создаем JSON задачи
cat > "$TASK_FILE" << EOF
{
  "task_id": "$TASK_ID",
  "created_at": "$(date -Iseconds)",
  "status": "pending",
  "description": "$TASK_DESCRIPTION",
  "decomposed_by": "orchestrator",
  "subtasks": [],
  "phase": null,
  "agents_assigned": []
}
EOF

echo -e "${GREEN}✓ Создан файл задачи:${NC} $TASK_FILE"
echo ""
echo -e "${YELLOW}Запуск оркестратора для декомпозиции...${NC}"
echo ""

# Выводим инструкцию для пользователя
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Следующие шаги:"
echo ""
echo "1. Оркестратор проанализирует задачу и создаст подзадачи для агентов"
echo "2. Файлы подзадач будут созданы в: $TASKS_DIR/"
echo "3. Отчёты агентов будут сохранены в: $REPORTS_DIR/"
echo ""
echo -e "${YELLOW}Для проверки статуса выполните:${NC}"
echo "  /agents:status"
echo ""
echo -e "${YELLOW}Для получения отчёта по задаче:${NC}"
echo "  /agents:report $TASK_ID"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
