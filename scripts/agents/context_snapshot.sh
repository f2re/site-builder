#!/usr/bin/env bash
# context_snapshot.sh — LocalContext Middleware
# Запускать при старте каждой агентской задачи.
# Даёт агенту мгновенный снапшот среды без лишнего контекста.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/.claude/agents/reports/_meta"
mkdir -p "$OUT"

SNAPSHOT="$OUT/context_snapshot.txt"

{
  echo "=== Context Snapshot ==="
  echo "date:      $(date -Iseconds)"
  echo "pwd:       $ROOT"
  echo "git_sha:   $(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo 'n/a')"
  echo "git_branch: $(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'n/a')"
  echo ""
  echo "=== Runtimes ==="
  echo "python:    $(python --version 2>/dev/null || echo 'not found')"
  echo "node:      $(node --version 2>/dev/null || echo 'not found')"
  echo "npm:       $(npm --version 2>/dev/null || echo 'not found')"
  echo "docker:    $(docker --version 2>/dev/null || echo 'not found')"
  echo "ruff:      $(ruff --version 2>/dev/null || echo 'not found')"
  echo "mypy:      $(mypy --version 2>/dev/null || echo 'not found')"
  echo "pytest:    $(pytest --version 2>/dev/null || echo 'not found')"
  echo "alembic:   $(alembic --version 2>/dev/null || echo 'not found')"
  echo ""
  echo "=== Project structure (top-level) ==="
  ls -1 "$ROOT" 2>/dev/null || true
  echo ""
  echo "=== Active tasks ==="
  TASKS_DIR="$ROOT/.claude/agents/tasks"
  if [ -d "$TASKS_DIR" ]; then
    ls -1 "$TASKS_DIR"/*.json 2>/dev/null | head -10 || echo '(no tasks)'
  else
    echo '(tasks dir not found)'
  fi
  echo ""
  echo "=== Recent reports ==="
  REPORTS_DIR="$ROOT/.claude/agents/reports"
  if [ -d "$REPORTS_DIR" ]; then
    find "$REPORTS_DIR" -name '*.md' -newer "$ROOT/AGENTS.md" 2>/dev/null | head -10 || echo '(no recent reports)'
  fi
} > "$SNAPSHOT"

echo "[context_snapshot] Written to: $SNAPSHOT"
cat "$SNAPSHOT"
