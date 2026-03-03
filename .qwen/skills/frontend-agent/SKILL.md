# WifiOBD Site — Frontend Agent Skill

## Role
Frontend development agent for **WifiOBD Site** e-commerce platform.

## Stack
- **Nuxt 3** (SSR), **Vue 3** Composition API, **TypeScript**, **Pinia**
- **PWA**: `@vite-pwa/nuxt` | **i18n**: `@nuxtjs/i18n` (ru/en)
- **Design tokens**: `frontend/assets/css/tokens.css` — SINGLE source of truth

## Architecture
**Mobile-First · Race-Style UI · Zero Confusion UX · Theme-Aware**

### Coding Contracts

#### API Calls
- ALL API calls MUST go through composables: `composables/use*.ts`
- ALL state MUST be in Pinia stores: `stores/*.ts`
- NO hardcoded API URLs — use `useRuntimeConfig()` everywhere
- `apiBase` MUST include version (e.g., `/api/v1`)

#### Components
- Every component MUST have `<script setup lang="ts">`
- NO inline styles — use CSS custom properties from `tokens.css` ONLY
- **NO hardcoded colors** — ALWAYS use `var(--color-*)` tokens
- ALL async actions MUST expose `pending`, `error`, `data` refs

#### Forms
- Client-side validation with `vee-validate` + `zod` schemas
- NO form submission without validation

## Design System — Race-Style UI

### Theme System
- Dark (default) / Light — managed by `themeStore` + `UThemeToggle`
- Theme persisted in `localStorage` key `theme`
- SSR: read theme from cookie `theme` to avoid hydration mismatch
- Default theme follows `prefers-color-scheme`

### Token File: `frontend/assets/css/tokens.css`
**SINGLE source of ALL design tokens**

Key tokens:
- `--color-bg`, `--color-surface`, `--color-text` — theme-aware
- `--color-accent` (#e63946) — Racing Red
- `--color-neon` (#00f5d4) — Speed Teal
- `--transition-fast/normal/slow` — animation timings
- `--radius-sm/md/lg/xl` — border radius
- `--shadow-sm/card/modal` — shadows for both themes

### Theme Store: `frontend/stores/themeStore.ts`
```ts
// MUST implement:
- init() — load from localStorage or system preference
- toggle() — switch theme, update localStorage
- setTheme(theme) — explicit theme setting
- applyTheme(theme, instant) — apply to document.documentElement
```

### Theme Toggle: `frontend/components/U/UThemeToggle.vue`
- MUST be in header (desktop) AND settings/profile menu (mobile)
- aria-label for accessibility
- Icon transition on theme switch

## Layout Rules — Mobile-First

1. **Base styles target 320px** — expand with `min-width` breakpoints
2. **Touch targets** ≥ 44×44px (WCAG 2.5.5)
3. Grid: CSS Grid for page layout, Flexbox for components
4. `max-width: 1440px` centered, fluid padding
5. Sticky header with `backdrop-filter: blur(12px)`
6. Bottom navigation on mobile (<768px) — NO hamburger menus

## Animation & Motion Contract

**Rule:** Every interaction MUST have visible, smooth feedback. No dead clicks.

### Micro-interactions
```css
.btn {
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}
.btn:hover  { transform: translateY(-1px); }
.btn:active { transform: scale(.97); }
```

### Page Transitions
- Use `<Transition name="fade-slide">` for route changes
- Skeleton loaders for ALL async content while `pending === true`

## Accessibility (WCAG 2.1 AA — BOTH themes)

- Contrast ≥ 4.5:1 for text in dark AND light themes
- Focus ring: `outline: 2px solid var(--color-accent); outline-offset: 2px`
- `aria-label` on all icon-only buttons
- Modal: focus trap, `Escape` closes

## Performance Contract

**Core Web Vitals:** LCP < 2.5s · INP < 200ms · CLS < 0.1

- Images: `<NuxtImg>` / `<NuxtPicture>` — `webp`+`avif`, `lazy`, explicit dimensions
- No chunk > 200 KB gzipped
- Code splitting for routes

## Pre-Commit Checklist

```bash
# Install dependencies
npm install --quiet

# Lint & type check
npm run lint  # or: ./node_modules/.bin/vue-tsc --noEmit
```

**Success:** Empty output or "SUCCESS" from vue-tsc

## Report Format
Save reports to `.qwen/agents/reports/frontend/<task_id>.md`

```markdown
## Status: DONE

## Completed:
- list of implemented files

## Artifacts:
- frontend/pages/shop/cart.vue
- frontend/components/shop/CartItem.vue
- frontend/stores/cartStore.ts
- frontend/composables/useCart.ts

## Contracts Verified:
- Design tokens from tokens.css: ✅
- Theme switching works (dark/light): ✅
- Mobile-first responsive: ✅
- Accessibility (axe-core): ✅

## Performance:
- Lighthouse Mobile: 95+
- Bundle size: < 200 KB

## Next:
- backend-agent: cart API integration complete

## Blockers:
- none
```
