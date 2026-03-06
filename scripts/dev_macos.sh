#!/usr/bin/env bash
# scripts/dev_macos.sh — Полный старт dev-окружения на macOS без Docker
# Использование:
#   ./scripts/dev_macos.sh          — установка + запуск всех сервисов
#   ./scripts/dev_macos.sh stop     — остановка всех сервисов
#   ./scripts/dev_macos.sh e2e      — запуск E2E тестов (поднимает окружение, если нужно)
#   ./scripts/dev_macos.sh seed     — только засеять тестовые данные

set -euo pipefail

# ── Цвета ─────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERR]${NC}  $*"; exit 1; }

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOGS_DIR="$ROOT_DIR/.logs"
PIDS_DIR="$ROOT_DIR/.pids"
LOCAL_BIN="$ROOT_DIR/.bin"   # локальные бинари (meilisearch и др.)
VENV="$ROOT_DIR/backend/.venv"

mkdir -p "$LOGS_DIR" "$PIDS_DIR" "$LOCAL_BIN"

# Добавляем .bin в PATH чтобы найти meilisearch и др.
export PATH="$LOCAL_BIN:$PATH"

# ── Безопасная загрузка .env ──────────────────────────────────────────────────
# Стандартный "source .env" с set -o allexport ломается на значениях
# с пробелами (EMAILS_FROM_NAME=WifiOBD Shop → shell видит "Shop" как команду).
# Парсим файл построчно: пропускаем комментарии и пустые строки,
# кавычим значение перед export.
load_env() {
  local env_file="$1"
  while IFS= read -r line || [[ -n "$line" ]]; do
    # пропускаем комментарии и пустые строки
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue
    # строки вида KEY=VALUE (VALUE может содержать пробелы и спецсимволы)
    if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
      local key="${BASH_REMATCH[1]}"
      local val="${BASH_REMATCH[2]}"
      # снимаем обрамляющие кавычки если есть
      val="${val%\"}"
      val="${val#\"}"
      val="${val%\'}"
      val="${val#\'}"
      export "$key=$val"
    fi
  done < "$env_file"
}

# ── Команда stop ──────────────────────────────────────────────────────────────
cmd_stop() {
  info "Останавливаем сервисы..."
  for pidfile in "$PIDS_DIR"/*.pid; do
    [[ -f "$pidfile" ]] || continue
    pid=$(cat "$pidfile")
    name=$(basename "$pidfile" .pid)
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" && success "Остановлен $name (pid $pid)"
    fi
    rm -f "$pidfile"
  done
  brew services stop postgresql 2>/dev/null && success "PostgreSQL остановлен" || true
  brew services stop redis          2>/dev/null && success "Redis остановлен"      || true
  info "Логи остались в $LOGS_DIR/"
}

# ── Ожидание порта ────────────────────────────────────────────────────────────
wait_port() {
  local name=$1 host=${2:-localhost} port=$3 max=${4:-30}
  local i=0
  printf "${BLUE}[INFO]${NC} Ждём $name на $host:$port"
  until nc -z "$host" "$port" 2>/dev/null; do
    ((i++)) && [[ $i -ge $max ]] && echo "" && error "$name не поднялся за ${max}с"
    printf "."
    sleep 1
  done
  echo " ${GREEN}готов${NC}"
}

# ── 1. Проверка зависимостей ───────────────────────────────────────────────────
check_deps() {
  info "Проверяем зависимости..."
  command -v brew      >/dev/null || error "Homebrew не установлен: https://brew.sh"
  command -v python3   >/dev/null || error "python3 не найден. Установи: brew install python@3.12"
  command -v node      >/dev/null || error "node не найден. Установи: brew install node"
  command -v npm       >/dev/null || error "npm не найден"
  command -v psql      >/dev/null || brew install postgresql
  command -v redis-cli >/dev/null || brew install redis

  if ! command -v meilisearch >/dev/null 2>&1; then
    warn "Meilisearch не найден, пробуем brew..."
    if brew install meilisearch 2>/dev/null; then
      success "Meilisearch установлен через brew"
    else
      warn "brew install не сработал (старый Xcode — это нормально), скачиваем бинарь..."
      # Скачиваем в локальную папку проекта — не требует SIP-прав
      curl -L https://install.meilisearch.com | sh
      mv ./meilisearch "$LOCAL_BIN/meilisearch"
      chmod +x "$LOCAL_BIN/meilisearch"
      success "Meilisearch бинарь сохранён в $LOCAL_BIN/meilisearch"
    fi
  fi

  success "Все зависимости в наличии"
}

# ── 2. Настройка .env ──────────────────────────────────────────────────────────
setup_env() {
  local env_file="$ROOT_DIR/.env"
  if [[ ! -f "$env_file" ]]; then
    info "Создаём .env из .env.example..."
    cp "$ROOT_DIR/.env.example" "$env_file"

    # Подменяем docker-имена сервисов на localhost
    sed -i '' \
      -e 's|POSTGRES_HOST=postgres|POSTGRES_HOST=localhost|' \
      -e 's|@postgres:|@localhost:|g' \
      -e 's|@redis:|@localhost:|g' \
      -e 's|http://meilisearch:|http://localhost:|g' \
      -e 's|REDIS_URL=redis://:.*@redis:6379/0|REDIS_URL=redis://localhost:6379/0|' \
      -e 's|CELERY_BROKER_URL=redis://:.*@redis:6379/1|CELERY_BROKER_URL=redis://localhost:6379/1|' \
      -e 's|CELERY_RESULT_BACKEND=redis://:.*@redis:6379/2|CELERY_RESULT_BACKEND=redis://localhost:6379/2|' \
      -e 's|MEILI_URL=http://meilisearch:7700|MEILI_URL=http://localhost:7700|' \
      "$env_file"

    # Генерируем случайные ключи
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(16))")
    FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null \
                 || python3 -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())")

    sed -i '' \
      -e "s|SECRET_KEY=change-me-to-a-long-random-string-at-least-64-chars|SECRET_KEY=$SECRET_KEY|" \
      -e "s|JWT_SECRET_KEY=change-me-jwt-secret-at-least-32-chars|JWT_SECRET_KEY=$JWT_SECRET|" \
      -e "s|FERNET_KEY=change-me-fernet-key|FERNET_KEY=$FERNET_KEY|" \
      -e "s|REDIS_PASSWORD=PWD-YOUR|REDIS_PASSWORD=|" \
      -e "s|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://sb_user:devpassword@localhost:5432/site_builder|" \
      -e "s|TEST_DATABASE_URL=.*|TEST_DATABASE_URL=postgresql+asyncpg://sb_user:devpassword@localhost:5432/site_builder_test|" \
      "$env_file"

    success ".env создан"
  else
    success ".env уже существует"
  fi

  # Безопасная загрузка: парсим построчно, не через shell-source
  load_env "$env_file"
}

# ── 3. PostgreSQL ──────────────────────────────────────────────────────────────
setup_postgres() {
  info "Запускаем PostgreSQL..."
  # brew services start postgresql
  wait_port "PostgreSQL" localhost 5432 20

  psql postgres -tc "SELECT 1 FROM pg_roles WHERE rolname='sb_user'" \
    | grep -q 1 || psql postgres -c "CREATE USER sb_user WITH PASSWORD 'devpassword';"
  psql postgres -tc "SELECT 1 FROM pg_database WHERE datname='site_builder'" \
    | grep -q 1 || psql postgres -c "CREATE DATABASE site_builder OWNER sb_user;"
  psql postgres -tc "SELECT 1 FROM pg_database WHERE datname='site_builder_test'" \
    | grep -q 1 || psql postgres -c "CREATE DATABASE site_builder_test OWNER sb_user;"

  if psql postgres -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;" site_builder 2>/dev/null; then
    success "TimescaleDB подключён"
  else
    warn "TimescaleDB недоступен — IoT-функции не будут работать (для dev это ок)"
  fi
  success "PostgreSQL настроен"
}

# ── 4. Redis ───────────────────────────────────────────────────────────────────
setup_redis() {
  info "Запускаем Redis..."
  brew services start redis
  wait_port "Redis" localhost 6379 15
  success "Redis запущен"
}

# ── 5. Python venv + зависимости ──────────────────────────────────────────────
setup_python() {
  info "Настройка Python venv..."
  if [[ ! -d "$VENV" ]]; then
    python3 -m venv "$VENV"
    success "venv создан в $VENV"
  fi
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
  pip install --quiet --upgrade pip
  pip install --quiet -r "$ROOT_DIR/backend/requirements.txt"
  success "Python зависимости установлены"
}

# ── 6. Alembic миграции ────────────────────────────────────────────────────────
run_migrations() {
  info "Применяем миграции..."
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
  cd "$ROOT_DIR/backend"
  alembic upgrade head
  alembic check && success "Миграции актуальны" || warn "alembic check вернул предупреждение"
  cd "$ROOT_DIR"
}

# ── 7. Frontend зависимости ────────────────────────────────────────────────────
setup_frontend() {
  info "Устанавливаем npm-зависимости..."
  cd "$ROOT_DIR/frontend"
  npm install --legacy-peer-deps --silent
  cd "$ROOT_DIR"
  success "Frontend зависимости установлены"
}

# ── 8. Meilisearch ─────────────────────────────────────────────────────────────
start_meilisearch() {
  info "Запускаем Meilisearch..."
  local meili_key="${MEILI_MASTER_KEY:-devmasterkey}"
  meilisearch \
    --master-key="$meili_key" \
    --db-path="$ROOT_DIR/.meilisearch_data" \
    --no-analytics \
    > "$LOGS_DIR/meilisearch.log" 2>&1 &
  echo $! > "$PIDS_DIR/meilisearch.pid"
  wait_port "Meilisearch" localhost 7700 20
  success "Meilisearch запущен (pid $(cat "$PIDS_DIR/meilisearch.pid"))"
}

# ── 9. Backend ─────────────────────────────────────────────────────────────────
start_backend() {
  info "Запускаем Backend (uvicorn)..."
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
  cd "$ROOT_DIR/backend"
  uvicorn app.main:app \
    --host 0.0.0.0 --port 8000 \
    --reload --reload-dir app \
    > "$LOGS_DIR/backend.log" 2>&1 &
  echo $! > "$PIDS_DIR/backend.pid"
  cd "$ROOT_DIR"
  wait_port "Backend" localhost 8000 30

  if curl -sf http://localhost:8000/health >/dev/null; then
    success "Backend /health OK (pid $(cat "$PIDS_DIR/backend.pid"))"
  else
    warn "Backend поднялся, но /health не ответил — проверь $LOGS_DIR/backend.log"
  fi
}

# ── 10. Celery worker ──────────────────────────────────────────────────────────
start_celery() {
  info "Запускаем Celery worker..."
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
  cd "$ROOT_DIR/backend"
  celery -A app.tasks.celery_app worker -B \
    --loglevel=warning --concurrency=2 \
    > "$LOGS_DIR/celery.log" 2>&1 &
  echo $! > "$PIDS_DIR/celery.pid"
  cd "$ROOT_DIR"
  success "Celery запущен (pid $(cat "$PIDS_DIR/celery.pid"))"
}

# ── 11. Frontend ───────────────────────────────────────────────────────────────
start_frontend() {
  info "Запускаем Frontend (Nuxt dev)..."
  cd "$ROOT_DIR/frontend"
  npm run dev > "$LOGS_DIR/frontend.log" 2>&1 &
  echo $! > "$PIDS_DIR/frontend.pid"
  cd "$ROOT_DIR"
  wait_port "Frontend" localhost 3000 60
  success "Frontend запущен (pid $(cat "$PIDS_DIR/frontend.pid"))"
}

# ── 12. Seed E2E данные ────────────────────────────────────────────────────────
cmd_seed() {
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
  load_env "$ROOT_DIR/.env"
  info "Засеваем тестовые данные..."
  cd "$ROOT_DIR"
  python "$ROOT_DIR/scripts/seed_e2e.py"
  success "Seed завершён"
}

# ── 13. E2E тесты ─────────────────────────────────────────────────────────────
cmd_e2e() {
  if ! nc -z localhost 8000 2>/dev/null; then
    warn "Backend не запущен — поднимаем окружение..."
    cmd_start
  fi
  cmd_seed
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
  pip install --quiet pytest playwright requests
  playwright install chromium
  info "Запускаем E2E тесты..."
  pytest "$ROOT_DIR/tests/e2e/" -v --headed -s \
    -p no:warnings \
    2>&1 | tee "$LOGS_DIR/e2e.log"
}

# ── Основной старт ─────────────────────────────────────────────────────────────
cmd_start() {
  echo ""
  echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║   site-builder — macOS dev start     ║${NC}"
  echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
  echo ""

  check_deps
  setup_env
  setup_postgres
  setup_redis
  setup_python
  run_migrations
  setup_frontend
  start_meilisearch
  start_backend
  start_celery
  start_frontend

  echo ""
  success "════ Все сервисы запущены ════"
  echo -e "  Frontend:    ${GREEN}http://localhost:3000${NC}"
  echo -e "  Backend API: ${GREEN}http://localhost:8000${NC}"
  echo -e "  API Docs:    ${GREEN}http://localhost:8000/docs${NC}"
  echo -e "  Meilisearch: ${GREEN}http://localhost:7700${NC}"
  echo ""
  echo -e "  Логи:  ${YELLOW}$LOGS_DIR/${NC}"
  echo -e "  Стоп:  ${YELLOW}./scripts/dev_macos.sh stop${NC}"
  echo -e "  E2E:   ${YELLOW}./scripts/dev_macos.sh e2e${NC}"
  echo ""

  trap cmd_stop INT TERM
  wait
}

# ── Роутинг команд ────────────────────────────────────────────────────────────
case "${1:-start}" in
  start)  cmd_start ;;
  stop)   cmd_stop  ;;
  e2e)    cmd_e2e   ;;
  seed)   cmd_seed  ;;
  *)      echo "Использование: $0 [start|stop|e2e|seed]"; exit 1 ;;
esac
