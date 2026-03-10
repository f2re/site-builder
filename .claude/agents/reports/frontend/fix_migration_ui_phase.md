## Status: DONE

## Completed:
- Добавлены CSS-стили для `.entity-phase` и `.entity-phase-count` в `frontend/pages/admin/migration.vue`
- Интерфейс `MigrationEntityStatus` уже содержал поля `phase?: string | null` и `phase_processed?: number | null` (строки 23-24)
- Шаблон уже содержал элемент с `data-testid="entity-phase"` (строки 340-346)
- Единственным недостающим элементом были CSS-стили для отображения фазы

## Artifacts:
- frontend/pages/admin/migration.vue

## Изменения (строки):
- Добавлены строки 568-578 (после `.entity-skipped`):
  - `.entity-phase`: `display: flex`, `gap: 0.25rem`, `color: var(--color-accent)`, `font-size: var(--text-xs)`, `font-family: var(--font-mono)`, `margin-bottom: 0.5rem`
  - `.entity-phase-count`: `color: var(--color-text-2)`

## Contracts Verified:
- data-testid на элементе фазы: OK (уже был `data-testid="entity-phase"`)
- Только var(--color-*) токены: OK (использованы `--color-accent`, `--color-text-2`)
- Нет хардкода цветов/отступов: OK
- npm run lint: OK (0 ошибок)
- npm run typecheck: OK (0 ошибок)

## Next:
- testing-agent: e2e тест для отображения entity-phase при status=RUNNING

## Blockers:
- none
