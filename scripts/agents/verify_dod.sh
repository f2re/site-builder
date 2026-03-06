#!/usr/bin/env bash
# verify_dod.sh — PreCompletionChecklist Middleware
# Запускать в Фазе VERIFY перед каждым коммитом.
# Нельзя объявлять задачу выполненной без прохождения этого скрипта.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

fail() { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }
pass() { echo -e "${GREEN}[OK]${NC}   $1"; }
info() { echo -e "${YELLOW}[INFO]${NC} $1"; }

echo ""
info "=== DoD Verification Start ==="
info "Root: $ROOT"
echo ""

# --- Backend ---
if [ -d "$ROOT/backend" ]; then
  info "Backend checks..."
  cd "$ROOT/backend"

  if command -v ruff &>/dev/null; then
    ruff check app/ --fix --quiet || fail "ruff --fix failed"
    ruff check app/ || fail "ruff check app/ has errors"
    pass "ruff check"
  else
    info "ruff not found, skipping"
  fi

  if command -v mypy &>/dev/null; then
    mypy app/ --ignore-missing-imports --no-error-summary 2>&1 | tail -5
    pass "mypy"
  else
    info "mypy not found, skipping"
  fi

  if command -v alembic &>/dev/null; then
    HEADS=$(alembic heads 2>/dev/null | grep -c 'head' || true)
    [ "$HEADS" -eq 1 ] || fail "alembic heads: expected 1, got $HEADS"
    alembic check 2>/dev/null || fail "alembic check: models do not match migrations"
    pass "alembic (1 head, models match)"
  else
    info "alembic not found, skipping"
  fi

  cd "$ROOT"
else
  info "backend/ not found, skipping backend checks"
fi

# --- Frontend ---
if [ -d "$ROOT/frontend" ]; then
  info "Frontend checks..."
  cd "$ROOT/frontend"

  if command -v npm &>/dev/null; then
    npm install --legacy-peer-deps --quiet 2>&1 | tail -3
    npm run lint || fail "npm run lint failed"
    pass "npm lint"
  else
    info "npm not found, skipping"
  fi

  cd "$ROOT"
else
  info "frontend/ not found, skipping frontend checks"
fi

# --- Tests ---
if [ -d "$ROOT/tests" ]; then
  info "Tests..."
  cd "$ROOT"
  if command -v pytest &>/dev/null; then
    pytest tests/ -x -q || fail "pytest: some tests failed"
    pass "pytest"
  else
    info "pytest not found, skipping"
  fi
else
  info "tests/ not found, skipping"
fi

# --- Report check ---
info "Checking for agent report..."
REPORTS_DIR="$ROOT/.claude/agents/reports"
if [ -d "$REPORTS_DIR" ]; then
  REPORT_COUNT=$(find "$REPORTS_DIR" -name '*.md' -newer "$ROOT/AGENTS.md" 2>/dev/null | wc -l || echo 0)
  if [ "$REPORT_COUNT" -gt 0 ]; then
    pass "agent report found ($REPORT_COUNT new file(s))"
  else
    echo -e "${YELLOW}[WARN]${NC} No new agent report found in .claude/agents/reports/"
    echo "       Create: .claude/agents/reports/<domain>/<task_id>.md"
  fi
fi

echo ""
pass "=== DoD Verification PASSED ==="
echo ""
