#!/usr/bin/env bash
# Command: /shop:init
# Description: Инициализировать новую фазу разработки магазина

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
echo -e "${BLUE}║  Инициализация фазы: Магазин                             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Создаем директорию задач
mkdir -p "$TASKS_DIR"

# Определяем номер фазы
PHASE_NUM=$(ls "$TASKS_DIR"/p*_shop_*.json 2>/dev/null | wc -l)
PHASE_NUM=$((PHASE_NUM + 1))

echo -e "${CYAN}Фаза:${NC} $PHASE_NUM"
echo -e "${CYAN}Домен:${NC} Магазин (e-commerce)"
echo ""

# Создаем задачи для фазы
TASKS=(
    "catalog:Каталог товаров с категориями и фильтрами"
    "cart:Корзина с резервированием через Redis Lua"
    "checkout:Оформление заказа (checkout flow)"
    "delivery:Интеграция со СДЭК v2 API"
    "payment:Интеграция с ЮKassa"
    "orders:Управление заказами и статусами"
)

echo -e "${YELLOW}Создание задач...${NC}"
echo ""

for i in "${!TASKS[@]}"; do
    IFS=':' read -r task_name task_desc <<< "${TASKS[$i]}"
    TASK_ID="p${PHASE_NUM}_shop_${task_name}"
    TASK_FILE="$TASKS_DIR/${TASK_ID}.json"
    
    # Определяем агента
    case $task_name in
        "delivery"|"payment")
            AGENT="cdek-agent"
            ;;
        *)
            AGENT="backend-agent"
            ;;
    esac
    
    # Создаем JSON задачи
    cat > "$TASK_FILE" << EOF
{
  "task_id": "$TASK_ID",
  "phase": $PHASE_NUM,
  "domain": "shop",
  "agent": "$AGENT",
  "title": "$task_desc",
  "description": "Реализация функционала: $task_desc",
  "depends_on": [],
  "priority": "high",
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
echo "1. Запущен devops-agent для проверки инфраструктуры"
echo "2. backend-agent начнёт реализацию каталога и корзины"
echo "3. cdek-agent подключится для интеграции доставки и оплаты"
echo ""
echo -e "${YELLOW}Для проверки статуса:${NC}"
echo "  /agents:status"
