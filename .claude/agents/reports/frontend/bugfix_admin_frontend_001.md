## Status: DONE

## Completed:
- BUG-ADM-FE-01: admin/products/index.vue — span.product-name заменён на NuxtLink.product-name--link, вся строка tr кликабельна через @click + router.push, кнопки действий имеют @click.stop
- BUG-ADM-FE-02: admin/blog/index.vue — span.post-title заменён на NuxtLink.post-title--link, вся строка tr кликабельна через @click + router.push, ячейка actions имеет @click.stop
- BUG-ADM-FE-03: admin/pages/index.vue — обёрнут в NuxtLayout name="admin", добавлен #header-title слот "Страницы", добавлен middleware: 'auth' в definePageMeta
- BUG-ADM-FE-03: admin/pages/[id].vue — обёрнут в NuxtLayout name="admin", добавлен #header-title слот с динамическим текстом (создание/редактирование)
- BUG-ADM-FE-04: admin/products/index.vue — product.category?.name заменён на product.category_name; useProducts.ts — добавлен category_name?: string в интерфейс ProductShort
- BUG-ADM-FE-05: создан composables/useFormatters.ts с функцией formatPrice; применён в ProductCard.vue, products/[slug].vue, admin/products/index.vue, cart.vue

## Artifacts:
- frontend/composables/useFormatters.ts (новый файл)
- frontend/composables/useProducts.ts (добавлен category_name в ProductShort)
- frontend/pages/admin/products/index.vue
- frontend/pages/admin/blog/index.vue
- frontend/pages/admin/pages/index.vue
- frontend/pages/admin/pages/[id].vue
- frontend/components/catalog/ProductCard.vue
- frontend/pages/products/[slug].vue
- frontend/pages/cart.vue

## Contracts Verified:
- data-testid на всех элементах: OK (существующие testid сохранены)
- Только var(--color-*) токены: OK
- Mobile-first breakpoints: OK (не затронуты)
- npm run lint: OK (0 errors)
- npm run typecheck: OK (0 errors)

## Accessibility:
- NuxtLink вместо span — улучшена семантика и навигация с клавиатуры

## Next:
- testing-agent: e2e тесты — клик по строке таблицы в admin/products и admin/blog
- testing-agent: проверить что /admin/pages и /admin/pages/{id} рендерят admin layout

## Blockers:
- none
