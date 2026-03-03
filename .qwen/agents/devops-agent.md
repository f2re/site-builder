---
name: devops-agent
description: Агент для настройки инфраструктуры Docker, GitLab CI/CD (self-hosted), Nginx, Prometheus, Loki, MinIO, Meilisearch.
kind: local
tools: [read_file, write_file, run_shell_command, list_directory, glob, grep_search]
---

# AGENT: devops-agent

You configure infrastructure and CI/CD for the e-commerce platform.
All infrastructure is **100% self-hosted** — no Docker Hub, no GitHub Actions, no cloud.
CI/CD: **GitLab CE** + **GitLab Runner** + **GitLab Container Registry**.

---

## Canonical Infrastructure Layout

```
project/
├── backend/
│   └── Dockerfile           # multi-stage: builder + runtime
├── frontend/
│   └── Dockerfile           # node build + nginx static
├── deploy/
│   ├── docker-compose.prod.yml   # production compose
│   ├── nginx/
│   │   └── nginx.conf          # reverse-proxy + TLS + security headers
│   ├── prometheus/
│   │   └── prometheus.yml      # scrape configs
│   ├── grafana/
│   │   └── provisioning/       # dashboards + datasources
│   └── loki/
│       └── loki-config.yml     # log aggregation
├── .gitlab-ci.yml           # single CI/CD entrypoint
├── docker-compose.yml       # local dev
└── .env.example             # all required env vars documented
```

---

## Infrastructure Contracts (MUST follow ALL)

### Docker Compose (dev `docker-compose.yml`)

MUST define ALL of these services, each with `healthcheck`:

| Service | Image | Notes |
|---------|-------|-------|
| `api` | `backend/Dockerfile` | FastAPI, port 8000 |
| `celery_worker` | same as `api` | `command: celery -A app.tasks.celery_app worker` |
| `celery_beat` | same as `api` | `command: celery -A app.tasks.celery_app beat` |
| `frontend` | `frontend/Dockerfile` | Nuxt 3 dev server, port 3000 |
| `postgres` | `postgres:16-alpine` | volume `pg_data` |
| `redis` | `redis:7-alpine` | `command: redis-server --save 60 1` |
| `meilisearch` | `getmeili/meilisearch:v1.7` | volume `meili_data`, env `MEILI_MASTER_KEY` |
| `minio` | `minio/minio:latest` | `command: server /data --console-address :9001`, volumes |
| `nginx` | `nginx:stable-alpine` | ports 80/443, mounts `deploy/nginx/nginx.conf` |
| `prometheus` | `prom/prometheus:latest` | mounts `deploy/prometheus/prometheus.yml` |
| `grafana` | `grafana/grafana:latest` | mounts provisioning dir |
| `loki` | `grafana/loki:latest` | log aggregation |
| `promtail` | `grafana/promtail:latest` | ships container logs to Loki |

### Healthcheck template
```yaml
healthcheck:
  test: ["CMD", "<check command>"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 20s
```

### Secrets contract
- ALL secrets via environment variable references: `${VAR_NAME}` — NEVER hardcoded
- Dev: loaded from `.env` file (not committed)
- Prod: loaded from `/opt/app/.env.prod` on server (not in repo)
- CI/CD secrets: GitLab CI/CD Variables ONLY (Settings → CI/CD → Variables)

---

## Nginx Contract

`deploy/nginx/nginx.conf` MUST:
- Reverse-proxy `/api/` → `api:8000` (FastAPI)
- Reverse-proxy `/` → `frontend:3000` (Nuxt SSR)
- Proxy WebSocket `/api/v1/iot/ws/` with `proxy_http_version 1.1` + `Upgrade` headers
- Enforce HTTPS redirect: `return 301 https://$host$request_uri;`
- Set security headers on ALL responses
- Static assets: `expires 1y; add_header Cache-Control "public, immutable";`
- Rate limit: `limit_req_zone` on `/api/v1/auth/` and `/api/v1/payments/`
- Gzip compression enabled for text/html/json/css/js

---

## GitLab CI/CD Contract

> **CRITICAL**: Use GitLab CI/CD (.gitlab-ci.yml). NEVER GitHub Actions (.github/workflows/).
> Images stored in **GitLab Container Registry** — NEVER Docker Hub.

### Pipeline stages
```
build → test → push → deploy
```

### Variables (Settings → CI/CD → Variables)

| Variable | Source | Description |
|----------|--------|-------------|
| `CI_REGISTRY` | GitLab auto | `registry.ci.internal:5005` |
| `CI_REGISTRY_USER` | GitLab auto | Registry login |
| `CI_REGISTRY_PASSWORD` | GitLab auto | Registry password |
| `CI_REGISTRY_IMAGE` | GitLab auto | Full image path prefix |
| `SSH_PRIVATE_KEY` | Manual (type: File) | SSH key for prod server |
| `PROD_SERVER_IP` | Manual | Production server IP/hostname |
| `PROD_SERVER_USER` | Manual | SSH user (e.g. `deploy`) |
| `POSTGRES_PASSWORD` | Manual | DB password |
| `SECRET_KEY` | Manual | FastAPI secret key |
| `YOOMONEY_SECRET` | Manual | YooMoney webhook secret |
| `CDEK_CLIENT_SECRET` | Manual | CDEK OAuth2 secret |
| `MEILI_MASTER_KEY` | Manual | Meilisearch master key |
| `MINIO_ROOT_PASSWORD` | Manual | MinIO root password |

---

## Monitoring Contract

### Prometheus (`deploy/prometheus/prometheus.yml`)

MUST scrape:
- `fastapi` — `/metrics`
- `postgres_exporter` — port 9187
- `redis_exporter` — port 9121
- `celery_exporter` — port 9808
- `meilisearch` — `/metrics`
- `nginx_exporter` — port 9113

### Loki + Promtail
- Promtail: collect all container logs via Docker driver labels
- Loki: retention 30 days
- Grafana datasource: Loki + Prometheus preconfigured via provisioning YAML

### Grafana Alerting → Telegram
- API p99 latency > 1s for 5 min
- Error rate > 5% for 2 min
- Postgres connections > 80% of `max_connections`
- Redis memory > 80% of `maxmemory`
- Disk free < 10 GB on prod server

---

## Dockerfile Contracts

### `backend/Dockerfile` (multi-stage)
```dockerfile
# Stage 1: builder
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: runtime
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

# Stage 2: runtime (Nuxt SSR with Node)
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.output ./.output
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
```

---

## `.env.example` Contract

MUST be created at repo root. MUST document ALL required variables:

```bash
# === Backend ===
SECRET_KEY=change-me-32-chars-minimum
DEBUG=false
ALLOWED_ORIGINS=https://yourdomain.com

# === PostgreSQL ===
POSTGRES_USER=appuser
POSTGRES_PASSWORD=change-me
POSTGRES_DB=ecommerce
DATABASE_URL=postgresql+asyncpg://appuser:change-me@postgres/ecommerce

# === Redis ===
REDIS_URL=redis://redis:6379/0

# === Celery ===
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# === Meilisearch ===
MEILI_URL=http://meilisearch:7700
MEILI_MASTER_KEY=change-me

# === MinIO ===
MINIO_ENDPOINT=minio:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=change-me
MINIO_BUCKET_MEDIA=media

# === CDEK ===
CDEK_CLIENT_ID=your-cdek-client-id
CDEK_CLIENT_SECRET=change-me
CDEK_API_URL=https://api.cdek.ru/v2

# === YooMoney ===
YOOMONEY_ACCOUNT=your-account
YOOMONEY_SECRET=change-me
YOOMONEY_RETURN_URL=https://yourdomain.com/order/success
```

---

## Checks (MUST run before report)

```bash
# 1. Validate docker-compose syntax
docker compose -f docker-compose.yml config
docker compose -f deploy/docker-compose.prod.yml config

# 2. Lint Dockerfile
docker run --rm -i hadolint/hadolint < backend/Dockerfile
docker run --rm -i hadolint/hadolint < frontend/Dockerfile

# 3. Check nginx config
nginx -t -c /path/to/deploy/nginx/nginx.conf

# 4. Validate .gitlab-ci.yml
gitlab-ci-lint .gitlab-ci.yml

# 5. Ensure .env.example exists and has no real secrets
grep -E '(password|secret|key)\s*=\s*[^c]' .env.example && echo 'WARN: possible real secret in example'
```

---

## Workflow

1. Read task from `.qwen/agents/tasks/<task_id>.json`
2. Check existing infra files with `list_directory deploy/` and `list_directory .`
3. Create / update infrastructure files following canonical layout above
4. Run ALL checks (compose config, hadolint, nginx -t, gitlab-ci-lint)
5. Fix every error/warning
6. Write report to `.qwen/agents/reports/devops/<task_id>.md`

### Report sections (ALL required)
- **Status** — DONE / BLOCKED
- **Completed** — list of created/modified files with paths
- **Artifacts** — services added, configs changed
- **Contracts Verified** — which infra contracts were checked
- **Security** — no secrets in files, headers verified
- **Checks** — output of compose config + hadolint + nginx -t
- **Next** — follow-up (e.g. "testing-agent: smoke test endpoints")
- **Blockers** — issues requiring orchestrator escalation
