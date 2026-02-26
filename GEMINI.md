# PROJECT: FastAPI E-Commerce + Blog + IoT

## Stack

### Backend
- Python 3.12, FastAPI, SQLAlchemy 2.x (async), Alembic
- PostgreSQL 16, TimescaleDB (IoT hypertable), Redis 7
- Celery + Redis broker (db=1), Celery beat (timezone: Europe/Moscow)
- Meilisearch (full-text search), MinIO (S3-compatible media storage)
- Monitoring: Prometheus, Grafana, Loki, Promtail

### Frontend
- Nuxt 3 (SSR), Vue 3 Composition API, TypeScript, Pinia
- CSS Design Tokens: `frontend/assets/css/tokens.css`
- Theme system: dark (default) / light via `themeStore` + `UThemeToggle`
- PWA: `@vite-pwa/nuxt`, i18n: `@nuxtjs/i18n` (ru/en)

### Integrations
- CDEK v2 API, YooMoney/aiomoney, ЦБ РФ (currency rates)
- GitLab CI/CD (NEVER GitHub Actions)
- GitLab Container Registry (NEVER Docker Hub)

### Infrastructure
- Docker Compose (dev: `docker-compose.yml`, prod: `deploy/docker-compose.prod.yml`)
- Nginx: `deploy/nginx/nginx.conf`
- CI/CD: `.gitlab-ci.yml`
- Secrets: `.env` (gitignored), template: `.env.example`

---

## Coding Contracts (Design-by-Contract)

### Universal (all agents)
1. Все эндпоинты MUST иметь Pydantic-схемы (Request + Response)
2. Все сервисы MUST принимать зависимости через DI (Depends)
3. Все внешние API-вызовы MUST иметь retry через tenacity (3 retries, exponential backoff)
4. Все репозитории MUST использовать параметризованные запросы (no raw SQL)
5. Все агенты MUST писать отчёт в `.gemini/agents/reports/<domain>/<task_id>.md`
6. NEVER использовать GitHub Actions (.github/workflows/) — только GitLab CI/CD
7. NEVER использовать Docker Hub — только GitLab Container Registry

---

## Theme Design Contract

All agents working on frontend MUST follow this contract.

### Token File
```
frontend/assets/css/tokens.css   ← SINGLE source of truth for all design tokens
```

```css
/* tokens.css structure */
:root {
  /* Dark theme (default) */
  --color-bg-primary: #0f1117;
  --color-bg-surface: #1a1d27;
  --color-bg-elevated: #242736;
  --color-text-primary: #e8eaf0;
  --color-text-secondary: #9499b0;
  --color-accent: #6c7aff;
  --color-accent-hover: #8490ff;
  --color-success: #4caf82;
  --color-error: #f06474;
  --color-border: #2e3147;
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 20px;
  --shadow-card: 0 4px 24px rgba(0,0,0,0.32);
}

[data-theme="light"] {
  --color-bg-primary: #f5f6fa;
  --color-bg-surface: #ffffff;
  --color-bg-elevated: #eef0f8;
  --color-text-primary: #1a1d2e;
  --color-text-secondary: #5a6070;
  --color-accent: #4a5aef;
  --color-accent-hover: #3a4adf;
  --color-border: #dde0ef;
  --shadow-card: 0 2px 12px rgba(0,0,0,0.08);
}
```

### themeStore Contract
```
frontend/stores/themeStore.ts   ← SINGLE source of truth for theme state
```

```typescript
// themeStore interface contract
interface ThemeStore {
  theme: 'dark' | 'light'          // current theme
  isDark: ComputedRef<boolean>      // computed
  toggle(): void                    // switch theme
  setTheme(t: 'dark'|'light'): void // explicit set
}
```

Rules:
- `themeStore.toggle()` MUST update `document.documentElement.dataset.theme`
- Theme preference MUST be persisted in `localStorage` key `theme`
- SSR: read theme from cookie `theme` (httpOnly=false) to avoid hydration mismatch
- Default theme: `dark`
- FORBIDDEN: hardcoded color values in any `.vue` component — ALWAYS use CSS variables from tokens.css

### UThemeToggle Component Contract
```
frontend/components/U/UThemeToggle.vue   ← global theme toggle button
```
- Calls `themeStore.toggle()` on click
- Shows sun icon in dark mode, moon icon in light mode
- MUST have `aria-label` for accessibility (WCAG 2.1 AA)
- MUST be rendered in `AppHeader.vue`

### WCAG Contrast Contract
- Normal text contrast ratio MUST be ≥ 4.5:1 in BOTH themes
- Large text contrast ratio MUST be ≥ 3:1 in BOTH themes
- Interactive elements MUST have visible focus ring
- Verified by: `npx axe-cli` (run by security-agent)

---

## Project Structure Reference

Canonical structure — all agents MUST place files here:

```
site-builder/
├── backend/
│   ├── app/
│   │   ├── api/v1/{products,orders,cart,blog,delivery,payments,iot,users,auth,admin,search}/
│   │   ├── core/{config,security,dependencies,exceptions}.py
│   │   ├── db/{base,session,models/}
│   │   ├── migrations/versions/
│   │   ├── tasks/{celery_app,notifications,inventory,search_index}.py
│   │   └── integrations/{cdek,yoomoney,cbr_rates,meilisearch,minio}.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── assets/css/tokens.css          ← design tokens
│   ├── stores/{themeStore,cartStore,authStore,productStore}.ts
│   ├── components/U/                   ← UI kit (UButton, UCard, UThemeToggle…)
│   ├── pages/
│   ├── composables/
│   ├── nuxt.config.ts
│   └── Dockerfile
├── deploy/
│   ├── nginx/nginx.conf
│   ├── docker-compose.prod.yml
│   └── monitoring/{prometheus.yml,loki.yml,promtail.yml}
├── tests/
│   ├── unit/, integration/, load/
│   └── conftest.py
├── .gemini/
│   ├── agents/{backend,frontend,devops,testing,security,cdek,orchestrator}-agent.md
│   ├── agents/contracts/{api_contracts,project_structure}.md
│   ├── agents/tasks/
│   ├── agents/reports/
│   └── policies/{agents,security-agent}.toml
├── docker-compose.yml               ← dev environment
├── .gitlab-ci.yml
├── .env.example
├── GEMINI.md
└── plan.md
```

---

## Report Contract

Каждый отчёт агента ОБЯЗАН содержать секции:
- `## Status: DONE | IN_PROGRESS | BLOCKED`
- `## Completed:` (список выполненного)
- `## Artifacts:` (список созданных файлов)
- `## Contracts Verified:` (какие контракты выполнены)
- `## Next:` (что передать следующему агенту)
- `## Blockers:` (если есть)

## Agent Invocation

Агенты вызываются: @orchestrator, @backend-agent, @frontend-agent,
@security-agent, @testing-agent, @cdek-agent, @devops-agent

Порядок вызова: devops → backend → cdek → frontend → testing → security
Полный граф зависимостей: см. orchestrator.md
