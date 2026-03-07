## Status: DONE

## Completed:
- Диагностика: все страницы `/admin/` используют `layout: false` в `definePageMeta` + `<NuxtLayout name="admin">` в шаблоне
- `migration.vue` не имел обёртки `<NuxtLayout name="admin">` — страница рендерилась без навигации
- Обёрнул содержимое шаблона в `<NuxtLayout name="admin">`
- Перенёс кнопки управления (запуск/пауза/возобновление) в слот `#header-actions` admin layout
- Перенёс заголовок "Миграция данных" в слот `#header-title` admin layout
- Удалил ставшие избыточными блок `.migration-header` и соответствующие CSS-стили
- Добавил `data-testid` на кнопки управления миграцией
- `npm run lint` (vue-tsc --noEmit) — ошибок нет

## Artifacts:
- frontend/pages/admin/migration.vue

## Contracts Verified:
- data-testid на интерактивных элементах: OK (migration-start-btn, migration-pause-btn, migration-resume-btn)
- Только var(--color-*) токены: OK (никаких изменений цветовых токенов не вносилось)
- Структура соответствует паттерну других admin-страниц: OK
- npm run lint (vue-tsc --noEmit): OK — 0 ошибок
- npm run type-check: OK (lint-скрипт в проекте запускает vue-tsc --noEmit)

## Root Cause:
Страница `migration.vue` была создана с `layout: false` и самостоятельным `<div class="migration-page">` в корне шаблона — без обёртки `<NuxtLayout name="admin">`. Все остальные admin-страницы (index, products, blog, orders, users, pages) используют паттерн: `definePageMeta({ layout: false })` + `<NuxtLayout name="admin">` в template.

## Next:
- testing-agent: e2e smoke тест для /admin/migration (проверить видимость sidebar, nav-item "Миграция" в активном состоянии)

## Blockers:
- none
