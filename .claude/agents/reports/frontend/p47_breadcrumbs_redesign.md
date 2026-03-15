## Status: DONE

## Completed:
- AppBreadcrumbs.vue — полная переработка: BEM-классы, иконка-разделитель `ph:caret-right-bold`, hover с фоном, truncate для текущего элемента, Schema.org разметка сохранена
- UBreadcrumbs.vue — переделан в pass-through обёртку над AppBreadcrumbs (обратная совместимость)
- pages/cart.vue — исправлен с `:items="breadcrumbItems"` на `:crumbs=[...]`, переменная `breadcrumbItems` удалена, добавлен элемент "Главная" с иконкой
- pages/checkout/index.vue — аналогично cart.vue, переменная `breadcrumbItems` удалена, добавлен полный путь с 4 элементами
- pages/blog/[slug].vue — иконка первого элемента исправлена с `ph:house` на `ph:house-bold`
- pages/products/[slug].vue — добавлен первый элемент `{ label: 'Главная', to: '/', icon: 'ph:house-bold' }` перед "Каталогом"

## Artifacts:
- frontend/components/AppBreadcrumbs.vue
- frontend/components/U/UBreadcrumbs.vue
- frontend/pages/cart.vue
- frontend/pages/checkout/index.vue
- frontend/pages/blog/[slug].vue
- frontend/pages/products/[slug].vue

## Contracts Verified:
- data-testid на всех элементах: OK
  - `data-testid="breadcrumbs-nav"` на `<nav>`
  - `data-testid="breadcrumb-link-{i}"` на каждой ссылке
  - `data-testid="breadcrumb-current"` на текущем элементе
- Только var(--color-*) токены: OK (нет хардкода, `--color-accent-bg` отсутствует в tokens.css — заменён на `--color-surface-2`)
- Schema.org (itemprop, itemscope, itemtype, meta position): OK — сохранена полностью
- `useBreadcrumbSchema` вызов в script setup: OK — не тронут
- npm run lint (vue-tsc --noEmit): OK
- npm run typecheck (vue-tsc --noEmit): OK

## Accessibility:
- `aria-label="Навигация"` на `<nav>`
- `aria-hidden="true"` на всех иконках-разделителях и декоративных иконках
- `:title="crumb.label"` на усечённом текущем элементе (доступность при overflow)
- `focus-visible` ring: `2px solid var(--color-accent)` на ссылках

## Next:
- testing-agent: e2e smoke тесты по `data-testid="breadcrumbs-nav"`, `breadcrumb-link-0`, `breadcrumb-current`

## Blockers:
- none
