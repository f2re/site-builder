#!/usr/bin/env bash
# Qwen Agents Auto-Loader
# Автоматическая регистрация агентов и slash-команд при старте Qwen CLI
# 
# Использование:
#   source .qwen/scripts/load-agents.sh
#   или
#   .qwen/scripts/load-agents.sh --register

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
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
QWEN_DIR="$PROJECT_ROOT/.qwen"
AGENTS_DIR="$QWEN_DIR/agents"
COMMANDS_DIR="$QWEN_DIR/commands"
CONFIG_FILE="$QWEN_DIR/agents.yaml"
SETTINGS_FILE="$QWEN_DIR/settings.json"

# Флаг регистрации
REGISTER_ONLY=false

# ============================================================================
# ФУНКЦИИ (объявлены до использования)
# ============================================================================

# Функция валидации конфигурации
validate_config() {
    local errors=0
    
    # Проверка config файла
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}✗ agents.yaml не найден${NC}"
        errors=$((errors + 1))
    else
        echo -e "${GREEN}✓ agents.yaml найден${NC}"
    fi
    
    # Проверка settings.json
    if [ ! -f "$SETTINGS_FILE" ]; then
        echo -e "${RED}✗ settings.json не найден${NC}"
        errors=$((errors + 1))
    else
        echo -e "${GREEN}✓ settings.json найден${NC}"
    fi
    
    # Проверка директорий
    if [ ! -d "$AGENTS_DIR" ]; then
        echo -e "${RED}✗ Директория агентов не найдена${NC}"
        errors=$((errors + 1))
    else
        echo -e "${GREEN}✓ Директория агентов найдена${NC}"
    fi
    
    if [ ! -d "$COMMANDS_DIR" ]; then
        echo -e "${RED}✗ Директория команд не найдена${NC}"
        errors=$((errors + 1))
    else
        echo -e "${GREEN}✓ Директория команд найдена${NC}"
    fi
    
    # Проверка исполняемости скриптов
    local non_exec=0
    for cmd in $(find "$COMMANDS_DIR" -name "*.sh" -type f 2>/dev/null); do
        if [ ! -x "$cmd" ]; then
            non_exec=$((non_exec + 1))
        fi
    done
    
    if [ $non_exec -gt 0 ]; then
        echo -e "${YELLOW}⚠ $non_exec скрипт(ов) не исполняемые${NC}"
    else
        echo -e "${GREEN}✓ Все скрипты исполняемые${NC}"
    fi
    
    return $errors
}

# Функция регистрации агента
register_agent() {
    local agent_file="$1"
    local name=$(basename "$agent_file" .md)
    # Заменяем дефисы на подчёркивания для имён переменных
    local var_name=${name//-/_}
    
    # Парсим frontmatter из .md файла
    local description=""
    local kind="local"
    local tools=""
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^description:[[:space:]]*(.*)$ ]]; then
            description="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^kind:[[:space:]]*(.*)$ ]]; then
            kind="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^tools:[[:space:]]*\[(.*)\]$ ]]; then
            tools="${BASH_REMATCH[1]}"
        fi
    done < "$agent_file"
    
    echo -e "  ${GREEN}✓${NC} Регистрирую агента: $name"
    
    # Экспортируем переменные окружения для Qwen CLI
    export QWEN_AGENT_${var_name^^}_FILE="$agent_file"
    export QWEN_AGENT_${var_name^^}_DESCRIPTION="$description"
    export QWEN_AGENT_${var_name^^}_KIND="$kind"
}

# Функция регистрации slash-команды
register_command() {
    local cmd_file="$1"
    local cmd_name=$(basename "$cmd_file" .sh | sed 's/_/:/g')
    local cmd_dir=$(dirname "$cmd_file" | sed "s|$COMMANDS_DIR/||")
    
    # Формируем полное имя команды
    local full_cmd="/${cmd_dir}:${cmd_name}"
    if [ "$cmd_dir" = "agents" ]; then
        full_cmd="/${cmd_name}"
    fi
    
    echo -e "  ${GREEN}✓${NC} Регистрирую команду: $full_cmd"
    # Команда доступна через прямой вызов скрипта
}

# Функция авто-загрузки
auto_load() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Qwen Agents: Авто-загрузка                              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Проверка конфигурации
    echo -e "${CYAN}Проверка конфигурации...${NC}"
    if ! validate_config; then
        echo -e "${RED}Ошибка валидации конфигурации${NC}"
        return 1
    fi
    echo ""
    
    # Загрузка агентов
    echo -e "${CYAN}Загрузка агентов...${NC}"
    local agent_count=0
    for agent_file in "$AGENTS_DIR"/*.md; do
        if [ -f "$agent_file" ]; then
            register_agent "$agent_file"
            agent_count=$((agent_count + 1))
        fi
    done
    echo -e "  ${GREEN}✓ Загружено агентов: $agent_count${NC}"
    echo ""
    
    # Регистрация команд
    echo -e "${CYAN}Регистрация slash-команд...${NC}"
    local cmd_count=0
    for cmd_dir in "$COMMANDS_DIR"/*/; do
        if [ -d "$cmd_dir" ]; then
            for cmd_file in "$cmd_dir"*.sh; do
                if [ -f "$cmd_file" ]; then
                    register_command "$cmd_file"
                    cmd_count=$((cmd_count + 1))
                fi
            done
        fi
    done
    echo -e "  ${GREEN}✓ Зарегистрировано команд: $cmd_count${NC}"
    echo ""
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}✓ Авто-загрузка завершена успешно!${NC}"
    echo ""
    echo "Доступные команды:"
    echo "  /agents:plan <задача>     — декомпозиция задачи"
    echo "  /agents:status            — статус задач"
    echo "  /agents:report <id>       — отчёт по задаче"
    echo "  /agents:validate          — валидация проекта"
    echo "  /shop:init                — инициализация фазы магазина"
    echo "  /blog:init                — инициализация фазы блога"
    echo "  /iot:init                 — инициализация фазы IoT"
    echo "  /admin:init               — инициализация фазы админ-панели"
    echo ""
}

# Функция помощи
show_help() {
    echo "Qwen Agents Auto-Loader"
    echo ""
    echo "Использование:"
    echo "  source $0              — загрузить агенты в текущую сессию"
    echo "  $0 --register          — зарегистрировать команды в Qwen CLI"
    echo "  $0 --list              — показать список агентов"
    echo "  $0 --validate          — проверить конфигурацию"
    echo "  $0 --help              — показать эту справку"
}

# Функция списка агентов
show_list() {
    echo "Доступные агенты:"
    for agent_file in "$AGENTS_DIR"/*.md; do
        if [ -f "$agent_file" ]; then
            name=$(basename "$agent_file" .md)
            echo "  - $name"
        fi
    done
    echo ""
    echo "Доступные команды:"
    find "$COMMANDS_DIR" -name "*.sh" -type f | sort | while read -r cmd; do
        cmd_name=$(basename "$cmd" .sh | sed 's/_/:/g')
        cmd_dir=$(dirname "$cmd" | sed "s|$COMMANDS_DIR/||")
        if [ "$cmd_dir" = "agents" ]; then
            echo "  /$cmd_name"
        else
            echo "  /${cmd_dir}:${cmd_name}"
        fi
    done
}

# ============================================================================
# ПАРСИНГ АРГУМЕНТОВ (теперь функции уже объявлены)
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --register|-r)
            REGISTER_ONLY=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        --list|-l)
            show_list
            exit 0
            ;;
        --validate|-v)
            echo -e "${CYAN}Валидация конфигурации...${NC}"
            validate_config
            exit $?
            ;;
        *)
            shift
            ;;
    esac
done

# ============================================================================
# ОСНОВНОЙ ЗАПУСК
# ============================================================================

if [ "$REGISTER_ONLY" = true ]; then
    echo -e "${CYAN}Регистрация агентов в Qwen CLI...${NC}"
    auto_load
else
    # Загружаем агенты в текущую сессию
    auto_load
fi
