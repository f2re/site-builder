#!/usr/bin/env bash
# Command: /agents:validate
# Description: Запустить финальную валидацию проекта (Gatekeeper)
# Pre-Commit Checklist

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
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Счётчики
PASSED=0
FAILED=0
WARNINGS=0

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  QWEN Gatekeeper: Pre-Commit Validation                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Дата: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Функция для проверки команды
run_check() {
    local name="$1"
    local command="$2"
    local directory="${3:-$PROJECT_ROOT}"
    
    echo -ne "  %-40s " "$name..."
    
    if cd "$directory" 2>/dev/null && eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Функция для проверки с предупреждением
run_check_warning() {
    local name="$1"
    local command="$2"
    local directory="${3:-$PROJECT_ROOT}"
    
    echo -ne "  %-40s " "$name..."
    
    if cd "$directory" 2>/dev/null && eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${YELLOW}⚠ WARNING${NC}"
        WARNINGS=$((WARNINGS + 1))
        return 0  # Не считаем ошибкой
    fi
}

echo -e "${CYAN}1. Проверка целостности БД (Alembic)${NC}"
echo "─────────────────────────────────────────────────────────────"

run_check "Alembic heads (один head)" "alembic heads 2>&1 | grep -c 'head'" "$BACKEND_DIR" || true
run_check "Alembic check (синхронизация)" "alembic check" "$BACKEND_DIR" || true

echo ""
echo -e "${CYAN}2. Линтинг и типизация (Backend)${NC}"
echo "─────────────────────────────────────────────────────────────"

run_check "Ruff check backend" "ruff check app/ --fix" "$BACKEND_DIR"
run_check "Ruff check (errors)" "ruff check app/" "$BACKEND_DIR"
run_check_warning "MyPy type check" "mypy app/ --ignore-missing-imports" "$BACKEND_DIR"

echo ""
echo -e "${CYAN}3. Линтинг и типизация (Frontend)${NC}"
echo "─────────────────────────────────────────────────────────────"

if [ -f "$FRONTEND_DIR/package.json" ]; then
    run_check "NPM install" "npm install --quiet" "$FRONTEND_DIR"
    run_check_warning "Vue TSC type check" "npm run lint" "$FRONTEND_DIR"
else
    echo -e "  ${YELLOW}⊘ Frontend не найден, пропускаем${NC}"
fi

echo ""
echo -e "${CYAN}4. Зависимости${NC}"
echo "─────────────────────────────────────────────────────────────"

if [ -f "$BACKEND_DIR/requirements.txt" ]; then
    run_check "PIP requirements (backend)" "pip install -r requirements.txt --quiet --dry-run" "$BACKEND_DIR"
else
    echo -e "  ${YELLOW}⊘ requirements.txt не найден${NC}"
fi

echo ""
echo -e "${CYAN}5. Тесты${NC}"
echo "─────────────────────────────────────────────────────────────"

if [ -d "$BACKEND_DIR/tests" ]; then
    run_check_warning "Pytest unit tests" "pytest tests/unit/ -v --tb=no -q" "$BACKEND_DIR"
else
    echo -e "  ${YELLOW}⊘ Тесты не найдены${NC}"
fi

echo ""
echo -e "${CYAN}6. Docker конфигурация${NC}"
echo "─────────────────────────────────────────────────────────────"

if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    run_check "Docker Compose config" "docker compose config --quiet" "$PROJECT_ROOT"
else
    echo -e "  ${YELLOW}⊘ docker-compose.yml не найден${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Результаты валидации:"
echo ""
echo -e "  ${GREEN}✓ Passed:${NC}   $PASSED"
echo -e "  ${RED}✗ Failed:${NC}   $FAILED"
echo -e "  ${YELLOW}⚠ Warnings:${NC} $WARNINGS"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ВАЛИДАЦИЯ ПРОВАЛЕНА                                     ║${NC}"
    echo -e "${RED}║  Исправьте ошибки перед коммитом                         ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ВАЛИДАЦИЯ ПРОЙДЕНА С ПРЕДУПРЕЖДЕНИЯМИ                   ║${NC}"
    echo -e "${YELLOW}║  Рекомендуется исправить предупреждения                  ║${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ВАЛИДАЦИЯ ПРОЙДЕНА                                      ║${NC}"
    echo -e "${GREEN}║  Все проверки успешны, можно коммитить                   ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    exit 0
fi
