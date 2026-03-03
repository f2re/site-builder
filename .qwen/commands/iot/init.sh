#!/usr/bin/env bash
# Command: /iot:init
# Description: Инициализировать новую фазу разработки IoT-дашборда

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
echo -e "${BLUE}║  Инициализация фазы: IoT-дашборд                         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка зависимостей
echo -e "${CYAN}Проверка зависимостей...${NC}"

if [ ! -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    echo -e "${RED}✗ docker-compose.yml не найден${NC}"
    echo "Требуется готовая инфраструктура (TimescaleDB, Redis Streams)"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose конфигурация найдена${NC}"

# Создаем директорию задач
mkdir -p "$TASKS_DIR"

# Определяем номер фазы
PHASE_NUM=$(ls "$TASKS_DIR"/p*_iot_*.json 2>/dev/null | wc -l)
PHASE_NUM=$((PHASE_NUM + 1))

echo ""
echo -e "${CYAN}Фаза:${NC} $PHASE_NUM"
echo -e "${CYAN}Домен:${NC} IoT (телеметрия, WebSocket)"
echo ""

# Создаем задачи для фазы
TASKS=(
    "models:Модель telemetry для TimescaleDB hypertable"
    "websocket:WebSocket эндпоинт для real-time данных"
    "redis_streams:Redis Streams consumer для телеметрии"
    "celery:Celery consumer для пакетной записи в БД"
    "dashboard:Дашборд с агрегацией через time_bucket"
    "devices:CRUD устройств и привязка к пользователям"
)

echo -e "${YELLOW}Создание задач...${NC}"
echo ""

for i in "${!TASKS[@]}"; do
    IFS=':' read -r task_name task_desc <<< "${TASKS[$i]}"
    TASK_ID="p${PHASE_NUM}_iot_${task_name}"
    TASK_FILE="$TASKS_DIR/${TASK_ID}.json"
    
    # Определяем агента
    case $task_name in
        "dashboard")
            AGENT="frontend-agent"
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
  "domain": "iot",
  "agent": "$AGENT",
  "title": "$task_desc",
  "description": "Реализация функционала: $task_desc",
  "depends_on": [],
  "priority": "high",
  "status": "pending",
  "created_at": "$(date -Iseconds)",
  "contracts_required": [".qwen/agents/contracts/iot_contracts.md"]
}
EOF
    
    echo -e "  ${GREEN}✓${NC} $TASK_ID → $AGENT"
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Требования к инфраструктуре:"
echo "  - PostgreSQL 16 + TimescaleDB"
echo "  - Redis 7 (Streams)"
echo "  - Celery + Beat"
echo ""
echo "Следующие шаги:"
echo ""
echo "1. devops-agent проверит конфигурацию TimescaleDB"
echo "2. backend-agent создаст модель telemetry и WebSocket"
echo "3. frontend-agent реализует дашборд"
echo ""
echo -e "${YELLOW}Для проверки статуса:${NC}"
echo "  /agents:status"
