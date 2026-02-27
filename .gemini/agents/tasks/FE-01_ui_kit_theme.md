---
id: FE-01
status: TODO
agent: frontend-agent
stage: Frontend base
priority: HIGH
depends_on: []
blocks: [FE-02, FE-03, FE-04]
---

# FE-01 — UI-кит и система токенов

## Цель

Создать базовый UI-кит компонентов и систему design tokens для Race-Style Dark-theme.

## ⚠️ Перед началом

```bash
list_directory frontend/components/U/
read_file frontend/assets/css/tokens.css
read_file frontend/nuxt.config.ts
```

## Задачи

### 1. Design Tokens (`frontend/assets/css/tokens.css`)

Если файл существует — read_file и дополнить, не перезаписывать.
Должны присутствовать переменные:
```css
:root {
  /* Colors — Race Dark */
  --color-bg: #0d0d0d;
  --color-surface: #1a1a1a;
  --color-accent: #e63946;
  --color-accent-hover: #c1121f;
  --color-text-primary: #f8f9fa;
  --color-text-secondary: #adb5bd;
  --color-border: #2d2d2d;
  --color-success: #2a9d8f;
  --color-warning: #e9c46a;
  --color-error: #e63946;

  /* Typography */
  --font-sans: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Spacing (4px grid) */
  --space-1: 4px; --space-2: 8px; --space-3: 12px;
  --space-4: 16px; --space-6: 24px; --space-8: 32px;

  /* Radius */
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 16px;

  /* Shadows */
  --shadow-card: 0 2px 8px rgba(0,0,0,0.4);
}
```

### 2. UI-компоненты (`frontend/components/U/`)

Проверить наличие, создать отсутствующие:
- `UButton.vue` — props: `variant (primary|secondary|ghost)`, `size (sm|md|lg)`, `loading`, `disabled`
- `UCard.vue` — slot: default, header, footer
- `UInput.vue` — props: `label`, `error`, `hint`, `type`
- `UBadge.vue` — props: `color`, `size`
- `USpinner.vue` — size prop
- `UModal.vue` — teleport to body, trap focus, ESC-закрытие
- `UThemeToggle.vue` — переключает `themeStore.isDark`
- `UBreadcrumbs.vue` — emits Schema.org BreadcrumbList, props: `crumbs: {label, href}[]`

**Правило:** все цвета только через CSS переменные из `tokens.css`. НИКАКИХ Tailwind-цветов или hardcoded hex.

### 3. Pinia stores (`frontend/stores/`)

Проверить наличие:
- `themeStore.ts` — `isDark: boolean`, toggle, persist в localStorage
- `authStore.ts` — `user`, `token`, `refresh`, `login()`, `logout()`, `refreshToken()`
- `cartStore.ts` — items, total, `addItem()`, `removeItem()`, `clear()`
- `notificationStore.ts` — WebSocket уведомления

### 4. Базовые composables (`frontend/composables/`)

- `useApi.ts` — обёртка `useFetch` с base URL из `useRuntimeConfig`, обработка 401
- `useToast.ts` — toast-уведомления
- `useIntersection.ts` — для lazy-loading

## Контракты

- NO hardcoded URLs — только `useRuntimeConfig().public.apiBase`
- NO hardcoded colors — только CSS переменные
- Все компоненты `U/` — `defineOptions({ name: 'U<Name>' })`
- `UBreadcrumbs` — обязательно эмитит Schema.org JSON-LD

## Критерии готовности

- [ ] `tokens.css` — все переменные на месте
- [ ] `UButton` рендерится во всех 3 вариантах без ошибок типизации
- [ ] `themeStore` переключает тему, состояние сохраняется в localStorage
- [ ] `useApi` перехватывает 401 и вызывает `authStore.refreshToken()`
- [ ] `vue-tsc --noEmit` — 0 ошибок

## Отчёт

`.gemini/agents/reports/frontend/FE-01.md`
