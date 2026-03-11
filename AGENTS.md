# AGENTS.md — Policy Gateway

> READ FIRST before any action.
> Canonical Architecture & Invariants: [ARCHITECTURE.md](ARCHITECTURE.md)
> DevOps & Deployment: [DEVOPS.md](DEVOPS.md)
> Orchestration & Agent Details: [GEMINI.md](GEMINI.md)
> Code Examples: [docs/examples/](docs/examples/)

---

## 🎯 Purpose
WifiOBD Site — E-commerce for OBD electronics.
**Backend**: FastAPI + PostgreSQL/TimescaleDB + Redis + Meilisearch.
**Frontend**: Nuxt 3 SSR + Vue 3 + Pinia.

---

## ⚖️ Hierarchy of Truth (Priority: Top → Down)
1. **Enforcement** — CI/CD, ruff, mypy, vue-tsc, pytest (Violation = Build Failure).
2. **Policy** — This file (AGENTS.md).
3. **Architecture** — ARCHITECTURE.md (Layers, Invariants).
4. **Operations** — docs/runbook.md (Dev/Deploy/Debug).
5. **Examples** — docs/examples/ (Canonical PRs, Tests, Endpoints).

---

## 🔧 Tooling — Mandatory Commands

```bash
# Backend (from /backend directory):
# Static analysis only (no live DB required)
ruff check app/ --fix && ruff check app/ && mypy app/ --ignore-missing-imports

# Frontend (from /frontend directory):
npm install --legacy-peer-deps --quiet
npm run lint

# Database:
# SKIP: alembic check && alembic heads (requires live DB)

# Tests:
# Use mocks for DB/Redis. Skip integration tests requiring live services.
pytest tests/unit/ -x -v
```

---

## 🔄 Agent Lifecycle (4 Mandatory Phases)

### Phase 1 — PLAN [Mode: xhigh reasoning]
**DO NOT WRITE CODE.**
- Read the task and this policy.
- Investigate affected files (`grep_search`, `glob`, `read_file`).
- Formulate a 5–10 step plan.
- Define a verification strategy (commands to prove success).

### Phase 2 — IMPLEMENT [Mode: high reasoning]
- Write code with testability in mind.
- Create unit tests alongside the code (not at the end).

### Phase 3 — VERIFY [Mode: xhigh reasoning]
- Run `bash scripts/agents/verify_dod.sh` for full DoD validation.
- Inspect full tool output — do not skim.
- Compare results with the Definition of Done below.

### Phase 4 — FIX
- Fix based on specific errors from Phase 3.
- Repeat Phase 3 until all DoD criteria are met.

> ⚠️ If a single file is edited 3+ times, reconsider the entire approach.

---

## ✅ MUST (Strict Requirements)
- Follow all 4 phases for every task.
- Run `bash scripts/agents/verify_dod.sh` before every commit.
- Run `bash scripts/agents/context_snapshot.sh` at task startup.
- New endpoints → only in `backend/app/api/v1/<feature>/` (router/service/repository/schemas).
- New dependencies → strictly pinned in `requirements.txt`, verify with `pip install`.
- Infrastructure changes → sync both `docker-compose.yml` and `deploy/docker-compose.prod.yml`.
- Docker images → strictly fixed versions (e.g., `v1.36.0`).
- Reports → write to `.gemini/agents/reports/<domain>/<task_id>.md` using the template.

## ❌ MUST NOT (Strict Prohibitions)
- Commit `.env` or any secrets.
- Hardcode colors/margins in `.vue` (use tokens from `tokens.css`).
- Modify `backend/app/core/` without unit tests.
- Use GitHub Actions (use GitLab CI/CD only).
- Use Docker Hub (use GitLab Container Registry only).
- Use `:latest` in docker images.
- Duplicate types: use feature-specific folders instead of global `app/models/`.
- Manually add `/api/v1` to paths when using `useFetch` with `baseURL: apiBase`.

---

## 🏁 Definition of Done (DoD)

A task is considered DONE only when all boxes are checked:

- [ ] `ruff check app/` → **0 errors**
- [ ] `mypy app/ --ignore-missing-imports` → **Success: no issues found**
- [ ] `npm run lint` → **SUCCESS** (vue-tsc)
- [ ] `pytest tests/unit/` → **ALL GREEN** (using mocks)
- [ ] Manual check of Alembic migration file logic (no live check)
- [ ] Agent report written in `.gemini/agents/reports/<domain>/<task_id>.md`

Quick Check: `bash scripts/agents/verify_dod.sh`

---

## 🧹 Agent Report Template

```markdown
## Status: DONE | IN_PROGRESS | BLOCKED
## Completed:
- Subtask 1...
- Subtask 2...
## Artifacts:
- path/to/file.py
## Contracts Verified:
- Pydantic schemas: ✅ | DI: ✅ | ruff: ✅ | mypy: ✅ | pytest: ✅
## Next:
- Handover instructions for the next agent/step
## Blockers:
- None or description
```
