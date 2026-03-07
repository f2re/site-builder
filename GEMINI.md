# GEMINI.md — AI Agent Entry Point

> **READ THIS FIRST.** This file contains the project concept, agent roles, and execution rules.
> **Detailed Documentation:** [ARCHITECTURE.md](ARCHITECTURE.md) | [AGENTS.md](AGENTS.md) | [DEVOPS.md](DEVOPS.md)
> **Active Tasks:** [.gemini/agents/tasks/](.gemini/agents/tasks/)

---

## 🎯 Project Concept

**WifiOBD Site** — E-commerce platform for automotive electronics (OBD adapters, telematics) featuring:
- 🛒 **Store**: Product catalog, cart, checkout, CDEK delivery, payments.
- 📝 **Blog**: Articles, documentation, reviews.
- 📊 **IoT Dashboard**: Online telemetry via WebSocket and TimescaleDB.
- 🔧 **Admin Panel**: Management of products, orders, content, and users.

---

## 🤖 Agents & Orchestration

### Available Agents
| Agent | Role | Responsibility |
|---|---|---|
| `@orchestrator` | Coordinator | Task decomposition, report validation. |
| `@backend-agent` | Backend Dev | FastAPI, SQLAlchemy, Alembic, REST API, WebSocket. |
| `@cdek-agent` | Integrations | CDEK API, YooMoney, CBR currency rates, Celery. |
| `@frontend-agent`| Frontend Dev | Nuxt 3, Vue 3, Pinia, UI Kit, PWA. |
| `@devops-agent`  | Infrastructure| Docker, Nginx, GitLab CI/CD, Monitoring. |
| `@testing-agent` | QA/Testing | pytest, Integration tests, Locust. |
| `@e2e-agent`     | E2E Testing | Playwright UI tests. |
| `@security-agent`| Security | READ-ONLY security auditing (OWASP, GDPR). |

### Phase Execution Order
`devops-agent` → `backend-agent` → `cdek-agent` → `frontend-agent` → `testing-agent` → `security-agent`

---

## 🛡 Mandatory Gatekeeper Rules (DoD)

NO commit shall be proposed to the user without passing this checklist:

1. **Linting & Type Checking**:
   - `backend`: `ruff check app/ --fix && mypy app/` (Success: 0 errors).
   - `frontend`: `npm run lint` (Success: SUCCESS).
2. **Database Integrity**:
   - `alembic heads` → exactly ONE head.
   - `alembic check` → models match migrations.
3. **Tests**:
   - `pytest` for all affected backend logic.
   - Playwright tests for critical frontend flows (Checkout, Auth).
4. **Persistence**:
   - All state-changing methods (POST/PUT/PATCH/DELETE) MUST call `await session.commit()`.

---

## 🧹 Agent Report Format

Every agent report MUST contain:
```markdown
## Status: DONE | IN_PROGRESS | BLOCKED
## Completed:
- List of completed subtasks
## Artifacts:
- List of created/modified files with paths
## Contracts Verified:
- Pydantic schemas, DI, UI testids, etc.
## Next:
- Handover instructions for the next agent
## Blockers:
- Description of any issues
```

---

## 🚀 Entry Point for New Tasks
Use `/agents:plan <task description>` to start the orchestration process.
The orchestrator will decompose the task and create JSON files in `.gemini/agents/tasks/`.
