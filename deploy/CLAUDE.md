# deploy/CLAUDE.md — devops-agent

> Агент читает этот файл при работе с инфраструктурой.
> Глобальные правила проекта, стек, DoD и граф фаз: [../CLAUDE.md](../CLAUDE.md)
> Задачи: [../.claude/agents/tasks/](../.claude/agents/tasks/)
> Отчёты: [../.claude/agents/reports/devops/](../.claude/agents/reports/devops/)

---

## 🔄 Рабочий цикл (ОБЯЗАТЕЛЕН — без исключений)

### ФАЗА 1 — PLAN [максимальный reasoning]
НЕ ПИШИ КОД. Выполни:
1. Прочитай `../CLAUDE.md` → проверь DoD задачи
2. Проверь существующие файлы: `deploy/` и корень проекта
3. Составь план в 5–10 шагов
4. Опиши стратегию верификации (compose config, hadolint, nginx -t)

### ФАЗА 2 — IMPLEMENT
- Следуй плану из Фазы 1
- Если файл правился 3+ раза — СТОП, пересмотри подход

### ФАЗА 3 — VERIFY [максимальный reasoning]
```bash
docker compose -f ../docker-compose.yml config
docker compose -f docker-compose.prod.yml config
docker run --rm -i hadolint/hadolint < ../backend/Dockerfile
docker run --rm -i hadolint/hadolint < ../frontend/Dockerfile
nginx -t -c /path/to/deploy/nginx/nginx.conf
```

### ФАЗА 4 — FIX
- Исправляй строго по ошибкам из Фазы 3
- Повторяй до полного прохождения DoD

---

You configure infrastructure and CI/CD for the WifiOBD Site.
All infrastructure is **100% self-hosted**.
CI/CD: **GitLab CE + GitLab Runner + GitLab Container Registry**.

> ⚠️ CRITICAL: NEVER use GitHub Actions (.github/workflows/).
> NEVER use Docker Hub. ALWAYS use GitLab Container Registry.
> NEVER use `:latest` image tags.

---

## 📁 Canonical Infrastructure Layout

```
project/
├── backend/Dockerfile           # multi-stage: builder + runtime
├── frontend/Dockerfile          # node build + nuxt SSR
├── deploy/
│   ├── docker-compose.prod.yml
│   ├── nginx/
│   │   └── nginx.conf           # reverse-proxy + TLS + security headers
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── grafana/provisioning/
│   └── loki/loki-config.yml
├── .gitlab-ci.yml               # single CI/CD entrypoint
├── docker-compose.yml           # local dev
└── .env.example
```

---

## 🐳 Docker Compose Contracts

### Dev `docker-compose.yml` — MUST define ALL services with `healthcheck`:

| Service | Image | Port |
|---------|-------|------|
| `api` | `backend/Dockerfile` | 8000 |
| `celery_worker` | same as `api` | — |
| `celery_beat` | same as `api` | — |
| `frontend` | `frontend/Dockerfile` | 3000 |
| `postgres` | `postgres:16-alpine` | 5432 |
| `redis` | `redis:7-alpine` | 6379 |
| `meilisearch` | `getmeili/meilisearch:v1.7` | 7700 |
| `minio` | `minio/minio` (fixed version) | 9000/9001 |
| `nginx` | `nginx:stable-alpine` | 80/443 |
| `prometheus` | `prom/prometheus` (fixed) | 9090 |
| `grafana` | `grafana/grafana` (fixed) | 3001 |
| `loki` | `grafana/loki` (fixed) | 3100 |
| `promtail` | `grafana/promtail` (fixed) | — |

### Healthcheck template
```yaml
healthcheck:
  test: ["CMD", "<check command>"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 20s
```
- `api`: `CMD curl -f http://localhost:8000/health`
- `postgres`: `CMD pg_isready -U $POSTGRES_USER`
- `redis`: `CMD redis-cli ping`
- `meilisearch`: `CMD curl -f http://localhost:7700/health`
- `minio`: `CMD curl -f http://localhost:9000/minio/health/live`

### Double Edit Rule
Any infra change (new env vars, image versions, new services) MUST be applied to **both** files simultaneously:
- `docker-compose.yml` (dev)
- `deploy/docker-compose.prod.yml` (prod)

### Secrets contract
- ALL secrets via env variable references: `${VAR_NAME}` — NEVER hardcoded
- Dev: loaded from `.env` (not committed)
- Prod: loaded from `/opt/app/.env.prod` (not in repo)
- CI/CD secrets: GitLab CI/CD Variables ONLY

---

## 🌐 Nginx Contract

`deploy/nginx/nginx.conf` MUST:
- Reverse-proxy `/api/` → `api:8000` (FastAPI)
- Reverse-proxy `/` → `frontend:3000` (Nuxt SSR)
- WebSocket `/api/v1/iot/ws/` with `proxy_http_version 1.1` + `Upgrade` headers
- HTTPS redirect: `return 301 https://$host$request_uri;`
- Security headers on ALL responses:
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; ..." always;
```
- Static assets: `expires 1y; add_header Cache-Control "public, immutable";`
- Rate limit: `limit_req_zone` on `/api/v1/auth/` and `/api/v1/payments/`
- Gzip enabled for text/html/json/css/js

---

## 🚀 GitLab CI/CD Contract

### Pipeline stages: `build → test → push → deploy`

### `.gitlab-ci.yml` variables block MUST include:
```yaml
variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  BACKEND_IMAGE:  $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHORT_SHA
  FRONTEND_IMAGE: $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHORT_SHA
```

### Jobs
- **build:backend / build:frontend** — `docker:26` + `docker:26-dind`, `--cache-from` latest
- **test:backend** — services: `postgres:16-alpine`, `redis:7-alpine`; fail if coverage < 70%
- **push:images** — only on `main` branch, push SHA tag + `latest` to GitLab registry
- **deploy:production** — only `main`, `when: manual`; `rsync` + SSH; `docker compose pull && up -d`

### GitLab CI/CD Variables (Settings → CI/CD → Variables)

| Variable | Type | Description |
|----------|------|-------------|
| `SSH_PRIVATE_KEY` | File | SSH key for prod server |
| `PROD_SERVER_IP` | Variable | Production server IP |
| `PROD_SERVER_USER` | Variable | SSH user |
| `POSTGRES_PASSWORD` | Variable (masked) | DB password |
| `SECRET_KEY` | Variable (masked) | FastAPI secret key |
| `YOOMONEY_SECRET` | Variable (masked) | YooMoney webhook secret |
| `CDEK_CLIENT_SECRET` | Variable (masked) | CDEK OAuth2 secret |
| `MEILI_MASTER_KEY` | Variable (masked) | Meilisearch key |
| `MINIO_ROOT_PASSWORD` | Variable (masked) | MinIO password |

---

## 📊 Monitoring Contract

### Prometheus scrape targets (`deploy/prometheus/prometheus.yml`)
```yaml
scrape_configs:
  - job_name: fastapi
    static_configs: [{targets: ['api:8000']}]
    metrics_path: /metrics
  - job_name: postgres
    static_configs: [{targets: ['postgres_exporter:9187']}]
  - job_name: redis
    static_configs: [{targets: ['redis_exporter:9121']}]
  - job_name: celery
    static_configs: [{targets: ['celery_exporter:9808']}]
  - job_name: meilisearch
    static_configs: [{targets: ['meilisearch:7700']}]
    metrics_path: /metrics
  - job_name: nginx
    static_configs: [{targets: ['nginx_exporter:9113']}]
```

### Grafana Alerting → Telegram
- API p99 latency > 1s for 5 min
- Error rate > 5% for 2 min
- Postgres connections > 80% of `max_connections`
- Redis memory > 80% of `maxmemory`
- Disk free < 10 GB on prod server

### Loki
- Promtail: collect container logs via Docker driver labels
- Retention: 30 days

---

## 🐋 Dockerfile Contracts

### `backend/Dockerfile` (multi-stage)
```dockerfile
# Stage 1: builder
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: runtime (non-root user)
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY alembic.ini .
COPY migrations/ ./migrations/
RUN adduser --disabled-password appuser && chown -R appuser /app
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### `frontend/Dockerfile` (multi-stage)
```dockerfile
# Stage 1: build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: runtime (Nuxt SSR)
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.output ./.output
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
```

---

## ✅ Checks Before Report

```bash
# 1. Docker Compose syntax
docker compose -f ../docker-compose.yml config
docker compose -f docker-compose.prod.yml config

# 2. Dockerfile linting
docker run --rm -i hadolint/hadolint < ../backend/Dockerfile
docker run --rm -i hadolint/hadolint < ../frontend/Dockerfile

# 3. Nginx config
nginx -t -c /path/to/deploy/nginx/nginx.conf

# 4. No real secrets in .env.example
grep -E '(password|secret|key)\s*=\s*[^c]' ../.env.example
```

---

## 📝 Report Template

Write to: `../.claude/agents/reports/devops/<task_id>.md`

```markdown
## Status: DONE | IN_PROGRESS | BLOCKED
## Completed:
- настроен docker-compose.yml с healthchecks для всех сервисов
- настроен deploy/docker-compose.prod.yml (sync с dev)
- обновлён .gitlab-ci.yml: stages build/test/push/deploy
## Artifacts:
- docker-compose.yml
- deploy/docker-compose.prod.yml
- deploy/nginx/nginx.conf
- .gitlab-ci.yml
- backend/Dockerfile
- frontend/Dockerfile
## Contracts Verified:
- Double Edit Rule: ✅ | healthchecks: ✅ | no :latest: ✅
- security headers: ✅ | no secrets hardcoded: ✅
## Security:
- все секреты через ${VAR}: ✅
- HTTPS redirect: ✅
- security headers: HSTS, X-Frame-Options, CSP: ✅
## Checks:
- compose config: ✅ | hadolint: ✅ | nginx -t: ✅
## Next:
- backend-agent: инфраструктура готова, запускай Phase 2
## Blockers:
- none
```
