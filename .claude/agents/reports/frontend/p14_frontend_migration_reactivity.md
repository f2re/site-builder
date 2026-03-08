## Status: DONE

## Completed:

### Блок 1: migration.vue — улучшение UX
- Polling при RUNNING ускорен с 3000ms до 2000ms
- Polling при IDLE/PAUSED/COMPLETED/FAILED замедлен с 10000ms до 15000ms
- `resumeMigration()` немедленно запускает `startPolling(2000)` до ответа API — мгновенный feedback
- `resetMigration()` после успеха переключает на `startPolling(15000)`
- Добавлены refs: `lastProgressValue`, `lastProgressAt`, `isMigrationStale`
- `watchEffect` детектирует зависшую миграцию: если `overall_status === 'RUNNING'` и прогресс не менялся >30 секунд — `isMigrationStale.value = true`
- Предупреждение `data-testid="migration-stale-warning"` отображается в карточке общего прогресса
- Интерфейс `MigrationEntityStatus` расширен полем `skipped?: number`
- В карточках сущностей отображается строка "Пропущено: X" с `data-testid="entity-skipped"` если `skipped > 0`
- Добавлены CSS классы `.stale-warning` и `.entity-skipped` с токенами

### Блок 2: admin/products/index.vue — пагинация и скроллбар
- Cursor-based пагинация: `currentCursor`, `cursorHistory`, `currentPageIndex`
- Функции `goNext()` и `goPrev()` — навигация с сохранением истории курсоров
- Кнопки `prev-page` (data-testid) и `next-page` (data-testid) с корректным disabled-состоянием
- Индикатор страницы `data-testid="current-page"`
- Пагинация показывается только если есть prev или next (hasPrev || hasNext)
- `.admin-table-wrapper`: добавлены `overflow-x: auto; max-width: 100%; -webkit-overflow-scrolling: touch`
- `.admin-table`: добавлены `width: 100%; min-width: 600px` — горизонтальная прокрутка внутри wrapper
- `.products-index-page`: `max-width: 100%; overflow-x: hidden` — нет scroll на уровне страницы

### Блок 3: admin/products/[id].vue — HTML-описание с изображениями
- Добавлен блок `description-html-section` с превью `description_html` через `v-html`
- Контейнер `data-testid="description-preview"` с классом `.description-preview`
- CSS стили через `:deep()`: `img { max-width: 100%; height: auto }`, стили для p, ul, ol, h1-h3, table, a
- Все стили используют только CSS custom properties из tokens.css
- Превью показывается только если `product?.description_html` существует

## Artifacts:
- `/Users/meteo/Documents/WWW/site-builder/frontend/pages/admin/migration.vue`
- `/Users/meteo/Documents/WWW/site-builder/frontend/pages/admin/products/index.vue`
- `/Users/meteo/Documents/WWW/site-builder/frontend/pages/admin/products/[id].vue`

## Contracts Verified:
- API cursor-based pagination `{ items[], next_cursor, total }` — соответствует api_contracts.md: OK
- `adminGetProducts(cursor?, per_page)` из useProducts.ts — соответствует: OK
- `description_html` в интерфейсе Product — уже был в useProducts.ts: OK
- data-testid на всех элементах: OK
  - `migration-stale-warning` — предупреждение о зависшей миграции
  - `entity-skipped` — строка skipped в карточке
  - `prev-page`, `next-page`, `current-page` — пагинация товаров
  - `description-preview` — превью HTML-описания
- Только var(--color-*) токены, без hardcoded цветов: OK
- npm run lint: OK (vue-tsc --noEmit, 0 ошибок)
- npm run typecheck: OK (vue-tsc --noEmit, 0 ошибок)

## Accessibility:
- Кнопки пагинации имеют `aria-label`
- Изображения в description-preview ограничены `max-width: 100%`

## Next:
- testing-agent: e2e тесты для пагинации товаров (prev-page/next-page testid)
- testing-agent: e2e тест для migration-stale-warning (имитация зависшего polling)

## Blockers:
- none
