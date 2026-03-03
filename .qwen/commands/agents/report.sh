#!/usr/bin/env bash
# Command: /agents:report <task_id>
# Description: Получить отчёт по выполненной задаче

set -euo pipefail

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Пути
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TASKS_DIR="$PROJECT_ROOT/.qwen/agents/tasks"
REPORTS_DIR="$PROJECT_ROOT/.qwen/agents/reports"

# Проверка аргументов
if [ $# -lt 1 ]; then
    echo -e "${RED}Ошибка: Не указан ID задачи${NC}"
    echo ""
    echo "Использование:"
    echo "  /agents:report <task_id>"
    echo ""
    echo "Пример:"
    echo "  /agents:report p1_backend_001"
    echo ""
    echo "Доступные задачи:"
    if [ -d "$TASKS_DIR" ]; then
        for task_file in "$TASKS_DIR"/*.json; do
            if [ -f "$task_file" ]; then
                task_id=$(basename "$task_file" .json)
                echo "  - $task_id"
            fi
        done
    fi
    exit 1
fi

TASK_ID="$1"
TASK_FILE="$TASKS_DIR/${TASK_ID}.json"

# Проверка существования задачи
if [ ! -f "$TASK_FILE" ]; then
    echo -e "${RED}Ошибка: Задача '$TASK_ID' не найдена${NC}"
    echo ""
    echo "Проверьте доступные задачи:"
    echo "  /agents:status"
    exit 1
fi

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  QWEN Agents: Отчёт по задаче                            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Вывод информации о задаче
echo -e "${CYAN}Задача:${NC} $TASK_ID"
echo "─────────────────────────────────────────────────────────────"

if command -v jq &> /dev/null; then
    # Используем jq если доступен
    description=$(jq -r '.description // "N/A"' "$TASK_FILE")
    status=$(jq -r '.status // "unknown"' "$TASK_FILE")
    agent=$(jq -r '.agent // "N/A"' "$TASK_FILE")
    phase=$(jq -r '.phase // "N/A"' "$TASK_FILE")
    created=$(jq -r '.created_at // "N/A"' "$TASK_FILE")
else
    # Упрощённый парсинг без jq
    description=$(grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' "$TASK_FILE" | cut -d'"' -f4 | head -1)
    status=$(grep -o '"status"[[:space:]]*:[[:space:]]*"[^"]*"' "$TASK_FILE" | cut -d'"' -f4 | head -1)
    agent=$(grep -o '"agent"[[:space:]]*:[[:space:]]*"[^"]*"' "$TASK_FILE" | cut -d'"' -f4 | head -1)
    phase=$(grep -o '"phase"[[:space:]]*:[[:space:]]*"[^"]*"' "$TASK_FILE" | cut -d'"' -f4 | head -1)
    created=$(grep -o '"created_at"[[:space:]]*:[[:space:]]*"[^"]*"' "$TASK_FILE" | cut -d'"' -f4 | head -1)
fi

echo "  Описание:  $description"
echo "  Статус:    $status"
echo "  Агент:     ${agent:-N/A}"
echo "  Фаза:      ${phase:-N/A}"
echo "  Создана:   $created"
echo ""

# Поиск отчёта
echo -e "${CYAN}Отчёты:${NC}"
echo "─────────────────────────────────────────────────────────────"

REPORT_FOUND=false

# Ищем отчёт по ID задачи
for report_file in $(find "$REPORTS_DIR" -name "*${TASK_ID}*.md" -type f 2>/dev/null | sort -r); do
    REPORT_FOUND=true
    echo -e "  ${GREEN}✓ Найден:${NC} $(basename "$report_file")"
    echo ""
    
    # Вывод содержимого отчёта
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"
    cat "$report_file"
    echo ""
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"
done

# Если отчёт не найден
if [ "$REPORT_FOUND" = false ]; then
    if [ "$status" = "DONE" ]; then
        echo -e "${YELLOW}⚠ Отчёт не найден, хотя задача помечена как выполненная${NC}"
        echo ""
        echo "Возможные причины:"
        echo "  - Агент ещё не создал отчёт"
        echo "  - Отчёт находится в другой директории"
    else
        echo -e "${YELLOW}⏳ Задача ещё не выполнена (статус: $status)${NC}"
        echo ""
        echo "Отчёт будет доступен после завершения задачи."
    fi
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Команды:"
echo "  /agents:status    — показать все задачи"
echo "  /agents:validate  — запустить валидацию проекта"
