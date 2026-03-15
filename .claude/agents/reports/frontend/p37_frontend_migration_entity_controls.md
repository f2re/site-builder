## Status: DONE

## Completed:
- Added `entityPending` reactive ref (`Record<string, { starting: boolean; resetting: boolean }>`) in script setup
- Added `getEntityPending(key: string)` helper returning defaults `{ starting: false, resetting: false }`
- Added `startEntityMigration(entityKey: MigrationEntityKey)` — POST `/admin/migration/start` with body `{ entity: entityKey }`, toast success/error, calls `fetchStatus()`
- Added `resetEntityMigration(entityKey: MigrationEntityKey)` — confirm dialog then DELETE `/admin/migration/reset/${entityKey}`, toast success/error, calls `fetchStatus()`
- Added entity controls block inside `.entity-card-footer` with `v-if="entity.status !== 'RUNNING'"`
- Two UButtons per entity card: "Запустить" (variant secondary) and "Сбросить" (variant ghost + CSS class `btn-entity-reset` for error color)
- Dynamic `data-testid` on all interactive elements and container
- CSS styles for `.entity-card-actions`, `.btn-entity-reset`, `.btn-entity-reset:hover` using only `var(--color-*)` tokens

## Artifacts:
- frontend/pages/admin/migration.vue

## Contracts Verified:
- API endpoint: POST `/admin/migration/start` with body `{ entity: entityKey }` — matches task context
- API endpoint: DELETE `/admin/migration/reset/${entityKey}` — matches task context (p37_backend_migration_entity_reset)
- data-testid on all elements: OK
  - `entity-controls-{key}` on container
  - `entity-start-btn-{key}` on start button
  - `entity-reset-btn-{key}` on reset button
- Only var(--color-*) tokens in styles: OK
- No hardcoded colors or spacing: OK
- npm run lint (vue-tsc --noEmit): OK (0 errors)
- npm run typecheck (vue-tsc --noEmit): OK (0 errors)

## Button behavior:
- "Запустить" disabled when `status.overall_status === 'RUNNING'`
- "Сбросить" disabled when `status.overall_status === 'RUNNING'` OR `entity.status === 'PENDING'`
- Both buttons hidden when `entity.status === 'RUNNING'`
- Loading spinner on each button independently via `entityPending[key].starting` / `entityPending[key].resetting`
- Confirm dialog before reset with variant 'danger'

## Next:
- testing-agent: e2e tests for entity-level migration controls (entity-start-btn-users, entity-reset-btn-users, etc.)

## Blockers:
- none
