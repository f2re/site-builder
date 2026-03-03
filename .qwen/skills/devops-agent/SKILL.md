# WifiOBD Site — DevOps Agent Skill

## Role
Infrastructure and DevOps agent for **WifiOBD Site**.

## Stack
- **Docker Compose** — dev: `docker-compose.yml`, prod: `deploy/docker-compose.prod.yml`
- **Nginx** — reverse proxy + static files
- **GitLab CI/CD** — `.gitlab-ci.yml` (НИКОГДА не GitHub Actions)
- **Registry**: GitLab Container Registry (НИКОГДА не Docker Hub)
- **Monitoring**: Prometheus + Grafana + Loki + Promtail

## Infrastructure Sync Policy

### Double Edit Rule
1. **Dev**: `docker-compose.yml` (project root)
2. **Prod**: `deploy/docker-compose.prod.yml`

**ANY infrastructure change MUST be applied to BOTH files simultaneously:**
- New environment variables
- Image version updates
- New services or volumes

### Version Policy
- ALWAYS pin image versions (e.g., `v1.36.0`)
- **NEVER** use `:latest` in production

## Services

### Backend
- FastAPI app (async)
- Celery worker + Celery Beat
- Redis (broker + cache)
- PostgreSQL 16 + TimescaleDB
- Meilisearch (search engine)
- MinIO (S3-compatible storage)

### Frontend
- Nuxt 3 (SSR)
- Nginx (static files + reverse proxy)

### Monitoring (prod only)
- Prometheus (metrics)
- Grafana (dashboards)
- Loki (logs)
- Promtail (log collector)

## Configuration Files

### docker-compose.yml (dev)
```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [db, redis]
  
  db:
    image: timescale/timescaledb-postgresql:16-latest
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: wifiobd
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
  
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
```

### deploy/docker-compose.prod.yml
```yaml
services:
  backend:
    image: registry.gitlab.com/<project>/backend:v1.0.0
    restart: always
    env_file: .env.prod
  
  nginx:
    image: nginx:1.25-alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs:ro
```

### .gitlab-ci.yml
```yaml
stages:
  - lint
  - test
  - build
  - deploy

variables:
  DOCKER_HOST: tcp://docker:2375
  DOCKER_TLS_CERTDIR: ""

lint:
  stage: lint
  script:
    - cd backend && ruff check app/
    - cd frontend && npm run lint

test:
  stage: test
  script:
    - cd backend && pytest
    - cd frontend && npm run test

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA ./backend
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA

deploy:
  stage: deploy
  script:
    - docker-compose -f deploy/docker-compose.prod.yml up -d
  only:
    - main
```

## Environment Variables

### .env (template in .env.example)
```bash
# Backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/wifiobd
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-here
TELEMETRY_RETENTION_DAYS=90

# Frontend
NUXT_PUBLIC_API_BASE=http://localhost:8000/api/v1

# CDEK
CDEK_API_KEY=your-cdek-api-key
CDEK_API_SECRET=your-cdek-api-secret

# YooKassa
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_API_KEY=your-api-key

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

## Pre-Commit Checklist

```bash
# Check docker-compose syntax
docker-compose config

# Check prod compose
docker-compose -f deploy/docker-compose.prod.yml config

# Verify image versions (no :latest in prod)
grep -r ":latest" deploy/docker-compose.prod.yml && exit 1 || true
```

## Report Format
Save reports to `.qwen/agents/reports/devops/<task_id>.md`

```markdown
## Status: DONE

## Completed:
- list of infrastructure changes

## Artifacts:
- docker-compose.yml (updated)
- deploy/docker-compose.prod.yml (updated)
- .gitlab-ci.yml (updated)

## Sync Verified:
- Dev and Prod configs are in sync: ✅
- Image versions pinned: ✅
- No :latest in prod: ✅

## Next:
- backend-agent: new service available

## Blockers:
- none
```
