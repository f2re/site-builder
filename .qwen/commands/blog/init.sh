#!/usr/bin/env bash
# Command: /blog:init
# Description: Инициализировать новую фазу разработки блога

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

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Инициализация фазы: Блог                                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Создаем директорию задач
mkdir -p "$TASKS_DIR"

# Определяем номер фазы
PHASE_NUM=$(ls "$TASKS_DIR"/p*_blog_*.json 2>/dev/null | wc -l)
PHASE_NUM=$((PHASE_NUM + 1))

echo -e "${CYAN}Фаза:${NC} $PHASE_NUM"
echo -e "${CYAN}Домен:${NC} Блог (статьи, документация)"
echo ""

# Создаем задачи для фазы
TASKS=(
    "models:Модели Post, Tag, Comment"
    "api:CRUD эндпоинты для статей"
    "admin:Админ-панель для управления контентом"
    "comments:Система комментариев с модерацией"
    "search:Поиск по статьям через Meilisearch"
    "frontend:Страницы блога и документация"
)

echo -e "${YELLOW}Создание задач...${NC}"
echo ""

for i in "${!TASKS[@]}"; do
    IFS=':' read -r task_name task_desc <<< "${TASKS[$i]}"
    TASK_ID="p${PHASE_NUM}_blog_${task_name}"
    TASK_FILE="$TASKS_DIR/${TASK_ID}.json"
    
    # Определяем агента
    case $task_name in
        "frontend")
            AGENT="frontend-agent"
            ;;
        *)
            AGENT="backend-agent"
            ;;
    esac
    
    cat > "$TASK_FILE" << EOF
{
  "task_id": "$TASK_ID",
  "phase": $PHASE_NUM,
  "domain": "blog",
  "agent": "$AGENT",
  "title": "$task_desc",
  "description": "Реализация функционала: $task_desc",
  "depends_on": [],
  "priority": "medium",
  "status": "pending",
  "created_at": "$(date -Iseconds)"
}
EOF
    
    echo -e "  ${GREEN}✓${NC} $TASK_ID → $AGENT"
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Следующие шаги:"
echo ""
echo "1. backend-agent создаст модели и API"
echo "2. frontend-agent реализует страницы блога"
echo ""
echo -e "${YELLOW}Для проверки статуса:${NC}"
echo "  /agents:status"
