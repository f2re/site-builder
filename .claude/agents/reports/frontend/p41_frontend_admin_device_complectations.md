## Status: DONE

## Completed:
- Added `AdminDeviceComplectation` interface and `complectations` field to `AdminDeviceRead` in `useUser.ts`
- Added `adminUpdateDeviceComplectations(deviceId, complectationIds)` method to `useUser.ts` — calls `PUT /admin/devices/{device_id}/complectations`
- Imported `useFirmware` and `Complectation` type in `pages/admin/devices/index.vue`
- Added reactive state: `allComplectations: Complectation[]` and `selectedComplectationIds: string[]`
- `onMounted`: loads all complectations via `fetchAllComplectations()` from `GET /admin/firmware/complectations`
- `openAddModal`: resets `selectedComplectationIds` to `[]`
- `openEditModal`: pre-fills `selectedComplectationIds` from `device.complectations?.map(c => c.id)`
- Added `toggleComplectation(id)` helper for chip toggle
- Added complectation chips section to both Add and Edit modals (after comment field)
- Chips: Race-Style UI with `var(--color-surface-2)` bg, `var(--color-border)` border; selected state: `var(--color-accent-glow)` bg + `var(--color-accent)` border + glow shadow
- Grid: 3 columns desktop, 2 columns mobile (`max-width: 768px`)
- `data-testid="admin-device-complectation-{code}"` on every chip
- `handleCreate`: after device creation calls `adminUpdateDeviceComplectations` if complectations selected
- `handleUpdate`: always calls `adminUpdateDeviceComplectations` to sync selected complectations

## Artifacts:
- `/Users/meteo/Documents/WWW/site-builder/frontend/composables/useUser.ts`
- `/Users/meteo/Documents/WWW/site-builder/frontend/pages/admin/devices/index.vue`

## Contracts Verified:
- API shape matches task spec: `GET /admin/firmware/complectations` via `useFirmware.fetchAllComplectations()`, `PUT /admin/devices/{id}/complectations` via new `adminUpdateDeviceComplectations()`
- `AdminDeviceRead.complectations: AdminDeviceComplectation[]` added
- data-testid on all complectation chips: `admin-device-complectation-{code}`
- Only `var(--color-*)` tokens used — no hardcoded colors
- Mobile-first: 3-col → 2-col breakpoint at 768px
- npm run lint: OK (0 errors)
- npm run typecheck: OK (0 errors)

## Accessibility:
- Chips are `<button type="button">` — keyboard accessible
- Focus ring from global `tokens.css` `:focus-visible` rule applies
- Semantic structure with `<label>` above chip grid

## Next:
- testing-agent: e2e tests for complectation chip selection in admin device modal

## Blockers:
- none
