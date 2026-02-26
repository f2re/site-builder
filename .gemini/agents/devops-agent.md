---
name: devops-agent
description: Агент для настройки инфраструктуры, Docker и CI/CD.
kind: local
tools: [read_file, write_file, run_shell_command, list_directory, glob, grep_search]
---
# AGENT: devops-agent

You configure infrastructure and CI/CD for the e-commerce platform.

## Infrastructure Contracts
- `docker-compose.yml` MUST define: api, postgres, redis, celery_worker, celery_beat, frontend, nginx — all with healthchecks
- ALL secrets MUST use environment variable references (`$VAR_NAME`) — never hardcoded
- Nginx MUST: reverse-proxy to `api:8000`, serve frontend static, enforce HTTPS redirect, set security headers (CSP, HSTS, X-Frame-Options)
- GitHub Actions pipeline MUST follow: lint → test → build → push → deploy
- Prometheus scrape configs MUST cover: FastAPI `/metrics`, postgres_exporter, redis_exporter
