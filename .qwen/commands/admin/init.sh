#!/usr/bin/env bash
# Command: /admin:init
# Description: Инициализировать новую фазу разработки админ-панели

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
echo -e "${BLUE}║  Инициализация фазы: Админ-панель                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка зависимостей
echo -e "${CYAN}Проверка зависимостей...${NC}"

# Проверяем, что CRUD эндпоинты уже готовы
REQUIRED_DOMAINS=("products" "orders" "users" "blog")
MISSING=()

for domain in "${REQUIRED_DOMAINS[@]}"; do
    if [ ! -d "$PROJECT_ROOT/backend/app/api/v1/$domain" ]; then
        MISSING+=("$domain")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠ Не все зависимости готовы:${NC}"
    for domain in "${MISSING[@]}"; do
        echo "  - $domain API отсутствует"
    done
    echo ""
    echo "Требуется сначала реализовать CRUD эндпоинты."
    echo ""
fi

echo -e "${GREEN}✓ Проверка завершена${NC}"

# Создаем директорию задач
mkdir -p "$TASKS_DIR"

# Определяем номер фазы
PHASE_NUM=$(ls "$TASKS_DIR"/p*_admin_*.json 2>/dev/null | wc -l)
PHASE_NUM=$((PHASE_NUM + 1))

echo ""
echo -e "${CYAN}Фаза:${NC} $PHASE_NUM"
echo -e "${CYAN}Домен:${NC} Админ-панель"
echo ""

# Создаем задачи для фазы
TASKS=(
    "auth:Role-based access control (admin/manager/customer)"
    "products_admin:CRUD товаров и категорий"
    "orders_admin:Управление заказами, CSV экспорт"
    "users_admin:Список пользователей, блок/разблок"
    "blog_admin:Модерация постов и комментариев"
    "iot_admin:Привязка устройств к пользователям"
    "audit:Логирование действий администраторов"
    "frontend:UI админ-панели (таблицы, формы)"
)

echo -e "${YELLOW}Создание задач...${NC}"
echo ""

for i in "${!TASKS[@]}"; do
    IFS=':' read -r task_name task_desc <<< "${TASKS[$i]}"
    TASK_ID="p${PHASE_NUM}_admin_${task_name}"
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
  "domain": "admin",
  "agent": "$AGENT",
  "title": "$task_desc",
  "description": "Реализация функционала: $task_desc",
  "depends_on": [],
  "priority": "high",
  "status": "pending",
  "created_at": "$(date -Iseconds)",
  "requirements": ["role=admin", "audit_log=true"]
}
EOF
    
    echo -e "  ${GREEN}✓${NC} $TASK_ID → $AGENT"
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Требования:"
echo "  - Все CRUD эндпоинты должны быть готовы"
echo "  - Role-based access control реализован"
echo ""
echo "Следующие шаги:"
echo ""
echo "1. backend-agent создаст admin API с проверкой ролей"
echo "2. frontend-agent реализует UI админ-панели"
echo ""
echo -e "${YELLOW}Для проверки статуса:${NC}"
echo "  /agents:status"
