#!/usr/bin/env bash
# Command: /agents:status
# Description: Показать статус текущих задач и агентов

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
AGENTS_CONFIG="$PROJECT_ROOT/.qwen/agents.yaml"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  QWEN Agents: Статус                                     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка наличия задач
if [ ! -d "$TASKS_DIR" ] || [ -z "$(ls -A "$TASKS_DIR"/*.json 2>/dev/null)" ]; then
    echo -e "${YELLOW}Нет активных задач${NC}"
    echo ""
    echo "Создайте новую задачу:"
    echo "  /agents:plan <описание задачи>"
    exit 0
fi

# Статус агентов
echo -e "${CYAN}Агенты:${NC}"
echo "─────────────────────────────────────────────────────────────"

declare -A AGENT_STATUS
declare -A AGENT_TASKS

# Считаем задачи по агентам
for task_file in "$TASKS_DIR"/*.json; do
    if [ -f "$task_file" ]; then
        # Извлекаем статус и агента из JSON (упрощённо)
        status=$(grep -o '"status"[[:space:]]*:[[:space:]]*"[^"]*"' "$task_file" | head -1 | cut -d'"' -f4 || echo "unknown")
        agent=$(grep -o '"agent"[[:space:]]*:[[:space:]]*"[^"]*"' "$task_file" | cut -d'"' -f4 || echo "unknown")
        task_id=$(basename "$task_file" .json)
        
        if [ -n "$agent" ]; then
            AGENT_TASKS[$agent]=$((${AGENT_TASKS[$agent]:-0} + 1))
            if [ "$status" = "DONE" ]; then
                AGENT_STATUS[$agent]="done"
            elif [ "$status" = "IN_PROGRESS" ]; then
                AGENT_STATUS[$agent]="in_progress"
            fi
        fi
    fi
done

# Список агентов
AGENTS=("orchestrator" "devops-agent" "backend-agent" "cdek-agent" "frontend-agent" "testing-agent" "security-agent")

for agent in "${AGENTS[@]}"; do
    tasks_count=${AGENT_TASKS[$agent]:-0}
    status=${AGENT_STATUS[$agent]:-idle}
    
    case $status in
        "done")
            icon="✅"
            status_text="Готов"
            ;;
        "in_progress")
            icon="🔄"
            status_text="В работе"
            ;;
        *)
            icon="⏸"
            status_text="Ожидание"
            ;;
    esac
    
    printf "  %-20s %s %-10s задач: %d\n" "$agent" "$icon" "[$status_text]" "$tasks_count"
done

echo ""

# Активные задачи
echo -e "${CYAN}Активные задачи:${NC}"
echo "─────────────────────────────────────────────────────────────"

active_count=0
for task_file in "$TASKS_DIR"/*.json; do
    if [ -f "$task_file" ]; then
        status=$(grep -o '"status"[[:space:]]*:[[:space:]]*"[^"]*"' "$task_file" | head -1 | cut -d'"' -f4 || echo "")
        if [ "$status" != "DONE" ] && [ "$status" != "cancelled" ]; then
            task_id=$(basename "$task_file" .json)
            description=$(grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' "$task_file" | cut -d'"' -f4 | head -c 50)
            created=$(grep -o '"created_at"[[:space:]]*:[[:space:]]*"[^"]*"' "$task_file" | cut -d'"' -f4)
            
            echo -e "  ${YELLOW}●${NC} $task_id"
            echo "    Описание: $description..."
            echo "    Создана: $created"
            echo ""
            active_count=$((active_count + 1))
        fi
    fi
done

if [ $active_count -eq 0 ]; then
    echo -e "  ${GREEN}Все задачи выполнены!${NC}"
fi

echo ""

# Последние отчёты
echo -e "${CYAN}Последние отчёты:${NC}"
echo "─────────────────────────────────────────────────────────────"

if [ -d "$REPORTS_DIR" ]; then
    report_count=0
    for report_file in $(find "$REPORTS_DIR" -name "*.md" -type f -mmin -60 | sort -r | head -5); do
        report_name=$(basename "$report_file")
        report_time=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$report_file" 2>/dev/null || stat -c "%y" "$report_file" | cut -d'.' -f1)
        echo -e "  ${GREEN}✓${NC} $report_name ($report_time)"
        report_count=$((report_count + 1))
    done
    
    if [ $report_count -eq 0 ]; then
        echo -e "  ${YELLOW}Нет недавних отчётов${NC}"
    fi
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Команды:"
echo "  /agents:plan <задача>  — создать новую задачу"
echo "  /agents:report <id>    — получить отчёт по задаче"
echo "  /agents:validate       — запустить валидацию проекта"
