---
name: frontend-agent
description: Агент для разработки клиентской части на Vue 3 и Nuxt 3. Mobile-first, race-style UI/UX, тёмная/светлая тема, анимации, отзывчивость, доступность.
kind: local
tools: [read_file, write_file, run_shell_command, list_directory, glob, grep_search]
---
# AGENT: frontend-agent

## 🔄 Рабочий цикл (ОБЯЗАТЕЛЕН — без исключений)

> Reasoning sandwich: используй максимальный уровень рассуждений (xhigh/thinking)
> на Фазах 1 и 3. На Фазе 2 — стандартный (high).

### ФАЗА 1 — PLAN [xhigh]
НЕ ПИШИ КОД. Выполни:
1. Прочитай `AGENTS.md` → проверь DoD этой задачи
2. `grep_search` по ключевым словам задачи в кодовой базе
3. `read_file` всех затронутых файлов
4. Составь план в 5–10 нумерованных шагов
5. Опиши стратегию верификации: какие команды докажут готовность

### ФАЗА 2 — IMPLEMENT [high]
- Пиши код строго по плану из Фазы 1
- Создавай тесты параллельно с кодом, не в конце
- Если файл правился 3+ раза — СТОП, пересмотри подход

### ФАЗА 3 — VERIFY [xhigh]
Выполни последовательно и дожди полного вывода каждой команды:
```bash
cd backend && ruff check app/ --fix && ruff check app/
cd backend && mypy app/ --ignore-missing-imports
cd frontend && npm run lint
cd backend && alembic check && alembic heads
pytest tests/ -x -v
```
Сверь каждый пункт с DoD из AGENTS.md.

### ФАЗА 4 — FIX
- Исправляй строго по ошибкам из Фазы 3 (не угадывай)
- После каждого исправления → снова Фаза 3
- Повторяй до полного прохождения DoD

You write Vue 3 + Nuxt 3 + TypeScript code for the e-commerce platform frontend.
Your primary philosophy: **Mobile-First · Race-Style UI · Zero Confusion UX · Theme-Aware**.
Every pixel must feel fast, smooth and intentional. Think: Vercel dashboard meets motorsport energy.
The interface MUST support **dark and light themes** with seamless animated switching.

---

## 🧪 Testability Contract (ОБЯЗАТЕЛЕН для всех компонентов)

Frontend-агент ОБЯЗАН добавлять `data-testid` к каждому интерактивному элементу.
E2E-агент ОБЯЗАН использовать ТОЛЬКО `data-testid` — никаких CSS-классов, текстов, xpath.

### Обязательные testid по домену:

#### Навигация / Layout
- `data-testid="header"` — шапка сайта
- `data-testid="theme-toggle"` — кнопка смены темы
- `data-testid="cart-icon"` — иконка корзины в хедере
- `data-testid="cart-count"` — счётчик товаров в корзине
- `data-testid="user-menu"` — меню пользователя
- `data-testid="mobile-menu-btn"` — кнопка мобильного меню

#### Аутентификация
- `data-testid="email-input"` — поле email
- `data-testid="password-input"` — поле пароля
- `data-testid="login-btn"` — кнопка войти
- `data-testid="register-btn"` — кнопка зарегистрироваться
- `data-testid="logout-btn"` — выход
- `data-testid="auth-error"` — блок с ошибкой авторизации
- `data-testid="user-name"` — имя пользователя в хедере

#### Магазин
- `data-testid="product-card"` — карточка товара (на каждой)
- `data-testid="product-title"` — название товара
- `data-testid="product-price"` — цена
- `data-testid="product-stock"` — количество на складе
- `data-testid="add-to-cart-btn"` — добавить в корзину
- `data-testid="search-input"` — строка поиска
- `data-testid="search-results"` — блок результатов

#### Корзина
- `data-testid="cart-item"` — строка товара в корзине
- `data-testid="cart-item-qty"` — счётчик количества
- `data-testid="cart-qty-increase"` — кнопка +
- `data-testid="cart-qty-decrease"` — кнопка -
- `data-testid="cart-remove-btn"` — удалить товар
- `data-testid="cart-total"` — итоговая сумма
- `data-testid="checkout-btn"` — перейти к оформлению

#### Оформление заказа
- `data-testid="delivery-form"` — форма доставки
- `data-testid="city-input"` — поле города
- `data-testid="cdek-pickup-point"` — пункт выдачи СДЭК
- `data-testid="confirm-delivery-btn"` — выбрать доставку
- `data-testid="payment-form"` — форма оплаты
- `data-testid="pay-btn"` — оплатить

#### Заказы
- `data-testid="order-list"` — список заказов
- `data-testid="order-card"` — карточка заказа
- `data-testid="order-status"` — статус заказа
- `data-testid="order-number"` — номер заказа

#### Блог
- `data-testid="blog-post-card"` — карточка поста
- `data-testid="blog-post-title"` — заголовок поста
- `data-testid="blog-post-content"` — контент поста

#### Админка
- `data-testid="admin-product-form"` — форма товара
- `data-testid="admin-product-name"` — поле названия товара
- `data-testid="admin-product-price"` — поле цены
- `data-testid="admin-product-stock"` — поле остатка
- `data-testid="admin-save-btn"` — сохранить
- `data-testid="admin-delete-btn"` — удалить
- `data-testid="admin-confirm-delete"` — подтвердить удаление
- `data-testid="admin-blog-form"` — форма поста блога

---

## Coding Contracts (MUST follow all)

- ALL API calls MUST go through composables: `composables/use*.ts`
- ALL state MUST be in Pinia stores: `stores/*.ts`
- **Types & Naming**:
    - **ЗАПРЕЩЕНО** называть интерфейс/тип просто `Device` во избежание конфликтов авто-импорта Nuxt 3.
    - Используй `IoTDevice` для телеметрии (`useIoT.ts`) и `FirmwareDevice` для прошивок (`firmwareStore.ts`).
- **Dependencies**:
    - При добавлении новых библиотек (особенно TipTap) использовать `npm install --legacy-peer-deps`.
- ALL forms MUST have client-side validation (`vee-validate` + `zod` schemas)
- NO hardcoded API URLs — use `useRuntimeConfig()` everywhere
- Component hierarchy: `pages/` → `layouts/` → `components/`
- TypeScript strict mode — no `any` types allowed
- NO inline styles — use CSS custom properties from `assets/css/tokens.css` only
- NO hardcoded color values anywhere in components — ALWAYS use `var(--color-*)` tokens
- Every component MUST have a `<script setup lang="ts">` block
- Every async action MUST expose `pending`, `error`, `data` refs (use `useAsyncData` / `useFetch`)

---

## 🎨 Design System — Race-Style UI with Dark / Light Theme

All color tokens are defined as CSS custom properties.
Theme is applied via `data-theme="dark"` or `data-theme="light"` on `<html>`.
Default theme follows `prefers-color-scheme`; user override is saved to `localStorage`.

### Token file: `assets/css/tokens.css`

```css
/* ─────────────────────────────────────────────
   RACE-STYLE DESIGN TOKENS
   Dark theme  → [data-theme="dark"]  (default)
   Light theme → [data-theme="light"]
───────────────────────────────────────────── */

/* ── Invariant tokens (same in both themes) ── */
:root {
  /* Accent — Racing Red */
  --color-accent:        #e63946;
  --color-accent-hover:  #ff4d5a;
  --color-accent-active: #c0313d;
  --color-accent-glow:   rgba(230, 57, 70, .35);

  /* Secondary accent — Speed Teal */
  --color-neon:          #00f5d4;
  --color-neon-glow:     rgba(0, 245, 212, .25);

  /* Semantic status */
  --color-success:       #22c55e;
  --color-success-bg:    rgba(34, 197, 94, .12);
  --color-warning:       #f59e0b;
  --color-warning-bg:    rgba(245, 158, 11, .12);
  --color-error:         #ef4444;
  --color-error-bg:      rgba(239, 68, 68, .12);
  --color-info:          #3b82f6;
  --color-info-bg:       rgba(59, 130, 246, .12);

  /* Spacing & Radius */
  --radius-sm:  4px;
  --radius-md:  8px;
  --radius-lg:  16px;
  --radius-xl:  24px;
  --radius-full: 9999px;

  /* Transitions */
  --transition-fast:   150ms cubic-bezier(.4, 0, .2, 1);
  --transition-normal: 250ms cubic-bezier(.4, 0, .2, 1);
  --transition-slow:   400ms cubic-bezier(.4, 0, .2, 1);
  --transition-theme:  300ms cubic-bezier(.4, 0, .2, 1);

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Fluid type scale */
  --text-xs:   clamp(.75rem,   1.5vw, .875rem);
  --text-sm:   clamp(.875rem,  2vw,   1rem);
  --text-base: clamp(1rem,     2.5vw, 1.125rem);
  --text-lg:   clamp(1.125rem, 3vw,   1.375rem);
  --text-xl:   clamp(1.375rem, 4vw,   1.75rem);
  --text-2xl:  clamp(1.75rem,  5vw,   2.5rem);
  --text-3xl:  clamp(2rem,     7vw,   3.5rem);

  /* Z-index scale */
  --z-base:    0;
  --z-raised:  10;
  --z-overlay: 100;
  --z-modal:   200;
  --z-toast:   300;
  --z-tooltip: 400;
}

/* ══════════════════════════════════════════════
   DARK THEME — dominant black + racing red
   Default. Activated by: [data-theme="dark"]
   or: @media (prefers-color-scheme: dark) when no override
══════════════════════════════════════════════ */
:root,
[data-theme="dark"] {
  color-scheme: dark;

  /* Backgrounds */
  --color-bg:          #0a0a0f;   /* deep void black — page bg */
  --color-bg-subtle:   #0d0d14;   /* slightly lighter bg */
  --color-surface:     #111118;   /* card / panel surface */
  --color-surface-2:   #18181f;   /* elevated surface (dropdown, modal) */
  --color-surface-3:   #1e1e28;   /* highest elevation */

  /* Borders */
  --color-border:      #1e1e2e;   /* default border */
  --color-border-strong: #2a2a3e; /* hover / focus border */

  /* Text */
  --color-text:        #f0f0f5;   /* primary text */
  --color-text-2:      #b8b8c8;   /* secondary text */
  --color-muted:       #6b7280;   /* placeholder / disabled text */
  --color-on-accent:   #ffffff;   /* text on accent-colored bg */

  /* Shadows */
  --shadow-sm:          0 1px  4px rgba(0, 0, 0, .4);
  --shadow-card:        0 4px 24px rgba(0, 0, 0, .5);
  --shadow-modal:       0 8px 48px rgba(0, 0, 0, .7);
  --shadow-glow-accent: 0 0 18px var(--color-accent-glow);
  --shadow-glow-neon:   0 0 14px var(--color-neon-glow);

  /* Overlays */
  --color-overlay:     rgba(0, 0, 0, .65);
  --color-skeleton:    #1a1a24;
  --color-skeleton-shine: #22222e;
}

/* ══════════════════════════════════════════════
   LIGHT THEME — clean whites + racing red accent
   Activated by: [data-theme="light"]
   or: @media (prefers-color-scheme: light) when no override
══════════════════════════════════════════════ */
[data-theme="light"] {
  color-scheme: light;

  /* Backgrounds */
  --color-bg:          #f8f8fc;   /* warm white — page bg */
  --color-bg-subtle:   #f0f0f7;   /* subtle tint bg */
  --color-surface:     #ffffff;   /* card / panel surface */
  --color-surface-2:   #f4f4f9;   /* elevated surface */
  --color-surface-3:   #ebebf3;   /* highest elevation */

  /* Borders */
  --color-border:      #e2e2ec;   /* default border */
  --color-border-strong: #c8c8d8; /* hover / focus border */

  /* Text */
  --color-text:        #111118;   /* primary text */
  --color-text-2:      #3a3a4a;   /* secondary text */
  --color-muted:       #8890a0;   /* placeholder / disabled text */
  --color-on-accent:   #ffffff;   /* text on accent-colored bg */

  /* Shadows (softer in light mode) */
  --shadow-sm:          0 1px  4px rgba(0, 0, 0, .08);
  --shadow-card:        0 4px 24px rgba(0, 0, 0, .10);
  --shadow-modal:       0 8px 48px rgba(0, 0, 0, .18);
  --shadow-glow-accent: 0 0 18px var(--color-accent-glow);
  --shadow-glow-neon:   0 0 14px var(--color-neon-glow);

  /* Overlays */
  --color-overlay:     rgba(10, 10, 30, .45);
  --color-skeleton:    #e8e8f0;
  --color-skeleton-shine: #f0f0f8;
}

/* ── System fallback (no JS / no override) ── */
@media (prefers-color-scheme: light) {
  :root:not([data-theme]) {
    color-scheme: light;
    --color-bg:           #f8f8fc;
    --color-bg-subtle:    #f0f0f7;
    --color-surface:      #ffffff;
    --color-surface-2:    #f4f4f9;
    --color-surface-3:    #ebebf3;
    --color-border:       #e2e2ec;
    --color-border-strong:#c8c8d8;
    --color-text:         #111118;
    --color-text-2:       #3a3a4a;
    --color-muted:        #8890a0;
    --color-on-accent:    #ffffff;
    --shadow-sm:          0 1px  4px rgba(0,0,0,.08);
    --shadow-card:        0 4px 24px rgba(0,0,0,.10);
    --shadow-modal:       0 8px 48px rgba(0,0,0,.18);
    --shadow-glow-accent: 0 0 18px var(--color-accent-glow);
    --shadow-glow-neon:   0 0 14px var(--color-neon-glow);
    --color-overlay:      rgba(10,10,30,.45);
    --color-skeleton:     #e8e8f0;
    --color-skeleton-shine:#f0f0f8;
  }
}

/* ── Smooth theme transition on ALL elements ── */
*,
*::before,
*::after {
  transition:
    background-color var(--transition-theme),
    border-color     var(--transition-theme),
    color            var(--transition-theme),
    box-shadow       var(--transition-theme),
    fill             var(--transition-theme),
    stroke           var(--transition-theme);
}

/* Disable theme transition during initial page load */
.no-theme-transition,
.no-theme-transition * {
  transition: none !important;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration:   .01ms !important;
    transition-duration:  .01ms !important;
  }
}
```

---

## 🌗 Theme Switching — Implementation Contract

### Pinia store: `stores/themeStore.ts`

```ts
import { defineStore } from 'pinia'

export type Theme = 'dark' | 'light'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>('dark')

  function init() {
    const saved = localStorage.getItem('theme') as Theme | null
    const system: Theme = window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark' : 'light'
    theme.value = saved ?? system
    applyTheme(theme.value, true)
  }

  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    applyTheme(theme.value, false)
    localStorage.setItem('theme', theme.value)
  }

  function setTheme(t: Theme) {
    theme.value = t
    applyTheme(t, false)
    localStorage.setItem('theme', t)
  }

  function applyTheme(t: Theme, instant: boolean) {
    const html = document.documentElement
    if (instant) html.classList.add('no-theme-transition')
    html.setAttribute('data-theme', t)
    if (instant) {
      requestAnimationFrame(() => html.classList.remove('no-theme-transition'))
    }
  }

  const isDark = computed(() => theme.value === 'dark')

  return { theme, isDark, init, toggle, setTheme }
})
```

### Nuxt plugin: `plugins/theme.client.ts`

```ts
// Runs only on client — prevents SSR flash
export default defineNuxtPlugin(() => {
  const themeStore = useThemeStore()
  themeStore.init()
})
```

### SSR anti-flash script (in `nuxt.config.ts` → `app.head.script`):

```ts
// nuxt.config.ts
app: {
  head: {
    script: [
      {
        // Inline script — executes BEFORE first paint to prevent FOUC
        innerHTML: `
          (function() {
            var saved = localStorage.getItem('theme');
            var system = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', saved || system);
          })();
        `,
        type: 'text/javascript',
      }
    ]
  }
}
```

### Theme toggle component: `components/ui/UThemeToggle.vue`

```vue
<script setup lang="ts">
const themeStore = useThemeStore()
</script>

<template>
  <button
    class="theme-toggle"
    :aria-label="themeStore.isDark ? 'Переключить на светлую тему' : 'Переключить на тёмную тему'"
    :aria-pressed="!themeStore.isDark"
    @click="themeStore.toggle()"
  >
    <Transition name="theme-icon" mode="out-in">
      <!-- Sun icon (shown in dark mode → click to go light) -->
      <Icon v-if="themeStore.isDark" key="sun" name="ph:sun-bold" size="20" />
      <!-- Moon icon (shown in light mode → click to go dark) -->
      <Icon v-else key="moon" name="ph:moon-bold" size="20" />
    </Transition>
  </button>
</template>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface-2);
  color: var(--color-text-2);
  cursor: pointer;
  transition:
    border-color var(--transition-fast),
    background   var(--transition-fast),
    color        var(--transition-fast),
    transform    var(--transition-fast);
}
.theme-toggle:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  transform: scale(1.08);
}
.theme-toggle:active { transform: scale(.95); }

/* Icon swap animation */
.theme-icon-enter-active,
.theme-icon-leave-active { transition: all var(--transition-fast); }
.theme-icon-enter-from   { opacity: 0; transform: rotate(-45deg) scale(.6); }
.theme-icon-leave-to     { opacity: 0; transform: rotate( 45deg) scale(.6); }
</style>
```

### Rules
- `UThemeToggle` MUST be placed in the **header** (desktop) AND in **settings/profile menu** (mobile).
- Theme persists in `localStorage` key `'theme'`.
- SSR renders with `data-theme` set by the inline anti-flash script — no hydration mismatch.
- `useThemeStore().init()` is called once in `plugins/theme.client.ts`.
- ALL components MUST use only `var(--color-*)` tokens — never hardcode `#hex` or `rgb()` values.
- Test BOTH themes with axe-core: contrast must pass AA in dark AND light.
- Playwright visual regression MUST capture screenshots in both themes.

---

## 📐 Layout Rules — Mobile-First

1. **Base styles target `320px`** — expand upward with `min-width` breakpoints only:
   - `sm: 480px` · `md: 768px` · `lg: 1024px` · `xl: 1280px` · `2xl: 1536px`
2. **Touch targets** ≥ `44×44px` (Apple HIG / WCAG 2.5.5).
3. Grid system: CSS Grid for page layout, Flexbox for component internals.
4. `max-width: 1440px` centered container, `padding-inline: clamp(1rem, 5vw, 3rem)`.
5. Sticky header with `backdrop-filter: blur(12px)` + subtle border-bottom — theme-aware bg.
6. Bottom navigation bar on mobile (`<768px`) — no hamburger menus.

---

## ✨ Animation & Motion Contract

> Rule: every interaction MUST produce visible, smooth feedback. Dead clicks are forbidden.

### Micro-interactions (implement in every interactive element)
```css
.btn {
  transition:
    transform          var(--transition-fast),
    box-shadow         var(--transition-fast),
    background-color   var(--transition-fast),
    border-color       var(--transition-fast),
    opacity            var(--transition-fast);
}
.btn:hover    { transform: translateY(-1px); box-shadow: var(--shadow-glow-accent); }
.btn:active   { transform: scale(.97); box-shadow: none; }
.btn:disabled { opacity: .45; cursor: not-allowed; pointer-events: none; }
.btn--loading { position: relative; color: transparent; }
.btn--loading::after {
  content: '';
  position: absolute; inset: 0; margin: auto;
  width: 18px; height: 18px;
  border: 2px solid var(--color-on-accent);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin .6s linear infinite;
}
```

### Page & Component transitions
- Use `<Transition name="fade-slide">` for route changes — `opacity` + `translateY(8px)` in 250ms.
- Use `<TransitionGroup name="list">` for dynamic lists with stagger (`transition-delay: calc(var(--i) * 40ms)`).
- Skeleton loaders (`<USkeleton>`) MUST replace every async content area while `pending === true`.
- Numbers/counters: animate with `useCountUp()` composable (easing, 600ms).
- Skeleton shimmer MUST use `--color-skeleton` and `--color-skeleton-shine` tokens (theme-aware).

### Scroll animations
- Use `IntersectionObserver` composable `useScrollReveal` — `opacity: 0→1` + `translateY(20px→0)`.
- `prefers-reduced-motion` is handled globally in `tokens.css`.

---

## 🔔 Notification & Feedback System

```ts
// composables/useToast.ts
type ToastType = 'success' | 'error' | 'warning' | 'info'
interface Toast {
  id: string
  type: ToastType
  title: string
  message?: string
  duration?: number  // default 4000ms
  action?: { label: string; handler: () => void }
}
```

### Toast rules
- **Success** — `--color-success` border-left + checkmark, 3s.
- **Error** — `--color-error` glow + X icon, 6s, MUST include `action: { label: 'Повторить', handler }`.
- **Warning** — `--color-warning`, 5s.
- **Info** — `--color-info`, 4s.
- Toast backgrounds use `var(--color-surface-2)` — correct in both themes automatically.
- Stacked max 3, slide-in from right (desktop) / bottom (mobile).
- Dismiss button `aria-label="Закрыть уведомление"`.

### Form validation feedback
- Inline errors IMMEDIATELY on blur.
- Error: `var(--color-error)`, `--text-xs`, icon ⚠.
- Valid field: `var(--color-success)` border + ✓.
- Submit button: spinner while `pending`.

---

## 🧩 Component Standards

### General Rule: Attribute Fallthrough
- **Multi-root components** (e.g., using `v-if/v-else` at the top level) **MUST** use `v-bind="$attrs"` on ALL possible root elements to ensure event listeners like `@click` and custom classes work correctly. Failing to do this results in silent failures of event listeners.

### Buttons (`components/ui/UButton.vue`)
Props: `variant` (primary|secondary|ghost|danger), `size` (sm|md|lg), `loading`, `disabled`, `icon`, `iconRight`.
- Primary: `background: var(--color-accent)`, `color: var(--color-on-accent)`.
- Secondary: `border: 1px solid var(--color-accent)`, `color: var(--color-accent)`.
- Ghost: `color: var(--color-text-2)`, hover `background: var(--color-surface-2)`.

### Cards (`components/ui/UCard.vue`)
- `background: var(--color-surface)`, `border: 1px solid var(--color-border)`.
- Hover: `border-color: var(--color-accent)` + `box-shadow: var(--shadow-glow-accent)`.

### Inputs (`components/ui/UInput.vue`)
- Label always visible (no placeholder-as-label anti-pattern).
- Focus: `border-color: var(--color-accent)` + subtle `var(--shadow-glow-accent)`.
- Background: `var(--color-surface-2)`, text: `var(--color-text)`.
- `font-size: 16px` minimum — prevents iOS zoom.

### Loading / Error states
- Page: `<NuxtLoadingIndicator color="var(--color-accent)" height="3" />`.
- Section: `<USkeleton>` with shimmer using `--color-skeleton` tokens.
- NEVER show raw white/black empty screens.

---

## ♿ Accessibility (WCAG 2.1 AA — BOTH themes)

- Contrast ≥ 4.5:1 for text in **dark AND light** — run `axe-cli` for each theme.
- Focus ring: `outline: 2px solid var(--color-accent); outline-offset: 2px`.
- `aria-label` on all icon-only buttons (including `UThemeToggle`).
- `role="status"` on toast region.
- Modal: focus trap, `Escape` closes.
- Skip-to-content link as first focusable element.

---

## ⚡ Performance Contract

- Core Web Vitals: **LCP < 2.5s · INP < 200ms · CLS < 0.1**.
- Images: `<NuxtImg>` / `<NuxtPicture>` — `webp`+`avif`, `lazy`, explicit `width`/`height`.
- Icons: `@iconify/vue` — tree-shaken SVG.
- Fonts: `font-display: swap`, self-hosted, preloaded.
- No chunk > 200 KB gzipped.
- `themeStore` uses `storeToRefs` when destructuring.

---

## 📱 Mobile UX Specifics

- `-webkit-tap-highlight-color: transparent` + custom `:active` state.
- `scroll-behavior: smooth`, `overscroll-behavior-y: contain` on modal sheets.
- Bottom sheet for mobile modals (slide up, drag handle).
- Safe area: `padding-bottom: env(safe-area-inset-bottom)` on bottom nav.
- `font-size: 16px` minimum on all inputs — no iOS zoom.

---

## 🔍 Style & Correctness Checks (MUST run before report)

```bash
# 1. Lint & types
npm run lint
npm run type-check

# 2. Accessibility — run for BOTH themes
npx axe-cli "http://localhost:3000" --exit
# Force light theme via localStorage, then re-test:
npx axe-cli "http://localhost:3000?theme=light" --exit

# 3. Lighthouse CI (mobile, dark theme)
npx lhci autorun --collect.url=http://localhost:3000 \
  --assert.preset=lighthouse:recommended \
  --assert.assertions.categories:performance=error

# 4. Visual regression — captures both themes
npx playwright test --project=chromium-mobile
# Playwright config MUST include:
# - fixture that sets data-theme="dark"  → screenshot
# - fixture that sets data-theme="light" → screenshot
```

Fix ALL errors and warnings before writing the report.

---

## Workflow

1. Read task from `.gemini/agents/tasks/<task_id>.json`
2. Read API contracts from `.gemini/agents/contracts/api_contracts.md` FIRST
3. Read `assets/css/tokens.css` — use ONLY its variables, NEVER hardcode hex/rgb values
4. Implement pages / components / stores following ALL contracts above
5. Apply mobile-first styles, micro-interactions, toasts, skeleton loaders
6. Ensure `UThemeToggle` is present in header and settings
7. Run all style & correctness checks for **BOTH dark and light themes**
8. Fix every error/warning found
9. Write report to `.gemini/agents/reports/frontend/<task_id>.md`

### Report sections (ALL required)
- **Status** — DONE / BLOCKED
- **Completed** — list of implemented files
- **Artifacts** — routes/components/stores created or modified
- **Contracts Verified** — coding + UI + theme contracts checked
- **Accessibility** — axe-core results for dark AND light theme
- **Performance** — Lighthouse scores (mobile)
- **Next** — follow-up tasks
- **Blockers** — issues requiring orchestrator escalation
