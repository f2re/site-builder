# GEMINI.md — AI Agent Entry Point

**WifiOBD Site** — E-commerce and IoT platform for automotive electronics (OBD adapters, telematics).
This file serves as the primary entry point and coordination hub for autonomous agents.

---

## 📚 Documentation & Tasks
- **Main Policy & DoD**: [AGENTS.md](AGENTS.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Infrastructure**: [DEVOPS.md](DEVOPS.md)
- **Active Tasks**: [.gemini/agents/tasks/](.gemini/agents/tasks/)

---

## 🎯 Project Concept
- 🛒 **Store**: Product catalog, cart, checkout, CDEK delivery, payments.
- 📝 **Blog**: Articles, documentation, reviews.
- 📊 **IoT Dashboard**: Online telemetry via WebSocket and TimescaleDB.
- 🔧 **Admin Panel**: Management of products, orders, content, and users.

---

## 🛠️ Project Conventions
- **PostgreSQL Enums**: All enum labels and their Python counterparts MUST be in **lowercase** (e.g., `users`, `pending`).
- **File Headers**: Every file must start with `# Module: <path> | Agent: <name> | Task: <id>`.
- **Async First**: Use `async/await` for all DB and external I/O operations.

---

## 🚀 Entry Point for New Tasks
Use `/agents:plan <task description>` to start the orchestration process.
The orchestrator will decompose the task and create JSON files in `.gemini/agents/tasks/`.

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
