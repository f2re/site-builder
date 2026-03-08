## Status: DONE

## Completed:
- Replaced `Math.random()` ID generation in `UInput.vue` with Vue 3's `useId()` composable
- Added `useId()` stable ID generation to `UTextarea.vue` (previously used bare `:id="name"` which was `undefined` when `name` not provided)
- Added optional `id` prop to `UTextarea.vue` for caller override (matching existing `UInput.vue` API)
- Both components now use the pattern: `props.id || props.name || useId()` — stable across SSR and client

## Root Cause:
`UInput.vue` line 33 used `Math.random().toString(36).slice(2, 9)` as fallback when neither `props.id` nor `props.name` was provided. This generated different random values on SSR vs client hydration, causing Vue hydration attribute mismatch warnings.

`UTextarea.vue` used `:id="name"` and `:for="name"` directly — producing `undefined` attributes when `name` prop was absent, also causing hydration mismatches.

## Artifacts:
- `frontend/components/U/UInput.vue`
- `frontend/components/U/UTextarea.vue`

## Contracts Verified:
- API shape matches api_contracts.md: N/A (UI-only fix)
- No hardcoded colors or spacing: OK (no styling changes)
- npm run lint: OK (exit 0)
- npm run typecheck: OK (exit 0, no errors)

## Next:
- testing-agent: verify no hydration warnings in e2e tests for admin forms

## Blockers:
- none
