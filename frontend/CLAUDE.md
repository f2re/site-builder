# frontend/CLAUDE.md — frontend-agent

> Агент читает этот файл при работе в директории `frontend/`.
> Глобальные правила проекта, стек, DoD и граф фаз: [../CLAUDE.md](../CLAUDE.md)
> Задачи: [../.claude/agents/tasks/](../.claude/agents/tasks/)
> Отчёты: [../.claude/agents/reports/frontend/](../.claude/agents/reports/frontend/)
> API контракты: [../.claude/agents/contracts/api_contracts.md](../.claude/agents/contracts/api_contracts.md)

---

## 🔄 Рабочий цикл (ОБЯЗАТЕЛЕН — без исключений)

### ФАЗА 1 — PLAN [максимальный reasoning]
НЕ ПИШИ КОД. Выполни:
1. Прочитай `../CLAUDE.md` → проверь DoD задачи
2. Прочитай `../.claude/agents/contracts/api_contracts.md` ПЕРВЫМ
3. Прочитай `assets/css/tokens.css` — используй ТОЛЬКО его переменные
4. Поиск по ключевым словам в кодовой базе
5. Составь план в 5–10 шагов

### ФАЗА 2 — IMPLEMENT
- Пиши код строго по плану из Фазы 1
- Если файл правился 3+ раза — СТОП, пересмотри подход

### ФАЗА 3 — VERIFY [максимальный reasoning]
```bash
cd frontend && npm run lint
cd frontend && npm run type-check
```

### ФАЗА 4 — FIX
- Исправляй строго по ошибкам из Фазы 3
- Повторяй до полного прохождения DoD

---

You write **Vue 3 + Nuxt 3 + TypeScript** code for the WifiOBD Site frontend.
Philosophy: **Mobile-First · Race-Style UI · Zero Confusion UX · Theme-Aware**.
Every pixel must feel fast, smooth and intentional. Both **dark and light themes** are mandatory.

---

## 🧪 Testability Contract — data-testid (ОБЯЗАТЕЛЕН)

Frontend-агент ОБЯЗАН добавлять `data-testid` к каждому интерактивному элементу.
e2e-agent использует ТОЛЬКО `data-testid` — никаких CSS-классов, текстов, xpath.

### Обязательные testid по домену:

#### Навигация / Layout
`header` · `theme-toggle` · `cart-icon` · `cart-count` · `user-menu` · `mobile-menu-btn`

#### Аутентификация
`email-input` · `password-input` · `login-btn` · `register-btn` · `logout-btn` · `auth-error` · `user-name`

#### Магазин
`product-card` · `product-title` · `product-price` · `product-stock` · `add-to-cart-btn` · `search-input` · `search-results`

#### Корзина
`cart-item` · `cart-item-qty` · `cart-qty-increase` · `cart-qty-decrease` · `cart-remove-btn` · `cart-total` · `checkout-btn`

#### Оформление заказа
`delivery-form` · `city-input` · `cdek-pickup-point` · `confirm-delivery-btn` · `payment-form` · `pay-btn`

#### Заказы
`order-list` · `order-card` · `order-status` · `order-number`

#### Блог
`blog-post-card` · `blog-post-title` · `blog-post-content`

#### Админка
`admin-product-form` · `admin-product-name` · `admin-product-price` · `admin-product-stock`
`admin-save-btn` · `admin-delete-btn` · `admin-confirm-delete` · `admin-blog-form`

---

## 📜 Coding Contracts (MUST follow all)

- ALL API calls through composables: `composables/use*.ts`
- ALL state in Pinia stores: `stores/*.ts`
- **ЗАПРЕЩЕНО** называть тип `Device` напрямую: используй `IoTDevice` (useIoT.ts) и `FirmwareDevice` (firmwareStore.ts)
- При добавлении библиотек (особенно TipTap): `npm install --legacy-peer-deps`
- ALL forms: client-side validation (`vee-validate` + `zod` schemas)
- NO hardcoded API URLs — use `useRuntimeConfig()` everywhere
- Component hierarchy: `pages/` → `layouts/` → `components/`
- TypeScript strict mode — no `any` types
- NO inline styles — ONLY CSS custom properties from `assets/css/tokens.css`
- NO hardcoded color values — ALWAYS use `var(--color-*)` tokens
- Every component: `<script setup lang="ts">`
- Every async action: expose `pending`, `error`, `data` refs via `useAsyncData` / `useFetch`
- **Multi-root components**: MUST use `v-bind="$attrs"` on ALL root elements (event fallthrough)

---

## 🎨 Design System — Race-Style UI

The full token file is at `assets/css/tokens.css` — **read it before any styling work**.
Theme applied via `data-theme="dark"` or `data-theme="light"` on `<html>`.

### Key tokens summary
- Accent: `--color-accent: #e63946` (Racing Red)
- Neon: `--color-neon: #00f5d4` (Speed Teal)
- Dark bg: `--color-bg: #0a0a0f` | Light bg: `--color-bg: #f8f8fc`
- Surface: `--color-surface` (cards/panels)
- Text: `--color-text`, `--color-text-2`, `--color-muted`
- Transitions: `--transition-fast: 150ms`, `--transition-normal: 250ms`, `--transition-theme: 300ms`
- Spacing/radius: `--radius-sm/md/lg/xl/full`

---

## 🌗 Theme Switching Contract

### `stores/themeStore.ts`
- `init()` — reads from `localStorage` or `prefers-color-scheme`; applies instantly (no flash)
- `toggle()` — switches theme, saves to `localStorage key='theme'`
- `applyTheme(t, instant)` — sets `document.documentElement.setAttribute('data-theme', t)`
- `isDark` — computed ref

### `plugins/theme.client.ts`
```ts
export default defineNuxtPlugin(() => {
  const themeStore = useThemeStore()
  themeStore.init()
})
```

### SSR anti-flash in `nuxt.config.ts → app.head.script`:
```ts
innerHTML: `(function(){
  var s=localStorage.getItem('theme');
  var m=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
  document.documentElement.setAttribute('data-theme', s||m);
})();`
```

### `components/U/UThemeToggle.vue`
- `data-testid="theme-toggle"`
- Icon: `ph:sun-bold` (dark mode) / `ph:moon-bold` (light mode)
- Animated icon swap with `<Transition name="theme-icon" mode="out-in">`
- MUST be placed in **header** (desktop) AND **settings/profile menu** (mobile)

### Rules
- ALL components: only `var(--color-*)` tokens — never `#hex` or `rgb()`
- Test BOTH themes with axe-core: contrast must pass WCAG AA
- Playwright visual regression: screenshots in both themes

---

## 📐 Layout Rules — Mobile-First

1. Base styles target `320px` — expand with `min-width` breakpoints only: `480·768·1024·1280·1536px`
2. Touch targets ≥ `44×44px`
3. CSS Grid for page layout, Flexbox for component internals
4. `max-width: 1440px` centered, `padding-inline: clamp(1rem, 5vw, 3rem)`
5. Sticky header with `backdrop-filter: blur(12px)` — theme-aware
6. Bottom navigation bar on mobile (`<768px`) — no hamburger menus

---

## ✨ Animation & Motion Contract

> Every interaction MUST produce visible, smooth feedback. Dead clicks are forbidden.

- Buttons: `transform: translateY(-1px)` on hover, `scale(.97)` on active, spinner on loading
- Page transitions: `<Transition name="fade-slide">` — `opacity` + `translateY(8px)` 250ms
- Lists: `<TransitionGroup name="list">` with stagger (`transition-delay: calc(var(--i) * 40ms)`)
- Skeleton loaders: `<USkeleton>` while `pending === true` — MUST use `--color-skeleton` tokens
- Numbers: `useCountUp()` composable (600ms easing)
- Scroll: `useScrollReveal()` — `opacity: 0→1` + `translateY(20px→0)` via IntersectionObserver
- `prefers-reduced-motion`: handled globally in `tokens.css`

---

## 🔔 Toast / Notification Contract

```ts
type ToastType = 'success' | 'error' | 'warning' | 'info'
// Error toasts: 6s + action: { label: 'Повторить', handler }
// Success: 3s | Warning: 5s | Info: 4s
// Stack max 3, slide from right (desktop) / bottom (mobile)
// Background: var(--color-surface-2) — theme-aware automatically
```

---

## 🧩 Component Standards

### `components/U/UButton.vue`
Props: `variant` (primary|secondary|ghost|danger), `size` (sm|md|lg), `loading`, `disabled`
- Primary: `background: var(--color-accent)`, `color: var(--color-on-accent)`
- Secondary: `border: 1px solid var(--color-accent)`, `color: var(--color-accent)`
- Loading: spinner overlay, text transparent

### `components/U/UCard.vue`
- `background: var(--color-surface)`, `border: 1px solid var(--color-border)`
- Hover: `border-color: var(--color-accent)` + `box-shadow: var(--shadow-glow-accent)`

### `components/U/UInput.vue`
- Label always visible (no placeholder-as-label)
- Focus: `border-color: var(--color-accent)` + `var(--shadow-glow-accent)`
- `font-size: 16px` minimum — prevents iOS zoom

---

## ♿ Accessibility (WCAG 2.1 AA — BOTH themes)

- Contrast ≥ 4.5:1 for text in dark AND light
- Focus ring: `outline: 2px solid var(--color-accent); outline-offset: 2px`
- `aria-label` on all icon-only buttons
- `role="status"` on toast region
- Modal: focus trap, `Escape` closes
- Skip-to-content link as first focusable element

---

## ⚡ Performance Contract

- Core Web Vitals: **LCP < 2.5s · INP < 200ms · CLS < 0.1**
- Images: `<NuxtImg>` with `webp+avif`, `lazy`, explicit dimensions
- Icons: `@iconify/vue` — tree-shaken SVG
- No chunk > 200 KB gzipped
- `themeStore`: use `storeToRefs` when destructuring

---

## 🔍 Checks Before Report

```bash
# 1. Lint & types
npm run lint
npm run type-check

# 2. Accessibility — BOTH themes
npx axe-cli "http://localhost:3000" --exit
npx axe-cli "http://localhost:3000?theme=light" --exit

# 3. Lighthouse CI (mobile)
npx lhci autorun --collect.url=http://localhost:3000

# 4. Visual regression — both themes
npx playwright test --project=chromium-mobile
```

---

## 📝 Report Template

Write to: `../.claude/agents/reports/frontend/<task_id>.md`

```markdown
## Status: DONE | IN_PROGRESS | BLOCKED
## Completed:
- список реализованных файлов
## Artifacts:
- pages/shop/index.vue
- components/shop/ProductCard.vue
- stores/productStore.ts
## Contracts Verified:
- data-testid на всех элементах: ✅
- Только var(--color-*) токены: ✅
- Mobile-first breakpoints: ✅
- vue-tsc / npm run lint: ✅
## Accessibility:
- axe-core dark: ✅ 0 violations
- axe-core light: ✅ 0 violations
## Performance:
- LCP: 1.8s | INP: 120ms | CLS: 0.02
## Next:
- testing-agent: e2e smoke тесты для shop/ и cart/
## Blockers:
- none
```
