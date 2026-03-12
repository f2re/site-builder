#!/usr/bin/env bash
# Устанавливает git хуки проекта в .git/hooks/
# Запустить один раз после клонирования: bash scripts/install-hooks.sh

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
HOOKS_DIR="$ROOT/.git/hooks"
SRC_HOOK="$ROOT/scripts/hooks/pre-commit"

if [ ! -d "$HOOKS_DIR" ]; then
  echo "❌ .git/hooks не найден. Убедитесь, что запускаете скрипт из git-репозитория."
  exit 1
fi

cp "$SRC_HOOK" "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/pre-commit"

echo "✅ pre-commit хук установлен в $HOOKS_DIR/pre-commit"
echo "   Он будет запускаться автоматически перед каждым git commit."
echo "   Чтобы пропустить проверки (в крайнем случае): git commit --no-verify"
