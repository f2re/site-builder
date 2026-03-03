#!/usr/bin/env bash
# Command: /agents:contract <domain>
# Description: Показать контракты для домена

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
CONTRACTS_DIR="$PROJECT_ROOT/.qwen/agents/contracts"

# Проверка аргументов
if [ $# -lt 1 ]; then
    echo -e "${RED}Ошибка: Не указан домен${NC}"
    echo ""
    echo "Использование:"
    echo "  /agents:contract <domain>"
    echo ""
    echo "Доступные домены:"
    echo "  api     — API контракты (эндпоинты, схемы)"
    echo "  auth    — Аутентификация и авторизация"
    echo "  iot     — IoT телеметрия, WebSocket"
    echo "  theme   — Design tokens, темы"
    echo "  cart    — Корзина, резервирование"
    echo "  payment — Платежи, ЮKassa"
    echo ""
    echo "Пример:"
    echo "  /agents:contract api"
    exit 1
fi

DOMAIN="$1"
CONTRACT_FILE="$CONTRACTS_DIR/${DOMAIN}_contracts.md"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  QWEN Agents: Контракты домена                           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка существования файла контрактов
if [ ! -f "$CONTRACT_FILE" ]; then
    # Проверяем основной файл контрактов
    MAIN_CONTRACTS="$CONTRACTS_DIR/api_contracts.md"
    if [ -f "$MAIN_CONTRACTS" ] && [ "$DOMAIN" = "api" ]; then
        CONTRACT_FILE="$MAIN_CONTRACTS"
    else
        echo -e "${RED}Ошибка: Контракты для домена '$DOMAIN' не найдены${NC}"
        echo ""
        echo "Проверьте доступные контракты:"
        if [ -d "$CONTRACTS_DIR" ]; then
            for contract_file in "$CONTRACTS_DIR"/*.md; do
                if [ -f "$contract_file" ]; then
                    name=$(basename "$contract_file" _contracts.md)
                    echo "  - $name"
                fi
            done
        fi
        exit 1
    fi
fi

echo -e "${CYAN}Домен:${NC} $DOMAIN"
echo -e "${CYAN}Файл:${NC} $CONTRACT_FILE"
echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""

# Вывод содержимого
cat "$CONTRACT_FILE"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
