## Status: DONE

## Completed:
- Added `id: v.id` to the variant mapping in `watch(product, ...)` in the admin product edit page
- Added optional `id?: string` field to the `variants` array type in the `ProductCreate` interface in `useProducts.ts`

## Problem:
When editing a product in the admin panel, the variant mapping in `watch(product, ...)` did not include the `id` field. This meant that on save (`updateProduct`), the server received variants without `id`, making it impossible to distinguish existing variants from new ones — causing the backend to create duplicates instead of updating existing variants.

## Root cause:
`frontend/pages/admin/products/[id].vue` lines 58–64: the `.map()` call omitted `id: v.id`.
`frontend/composables/useProducts.ts` line 91: the `ProductCreate.variants` array type had no `id` field, which would have caused a TypeScript error if `id` were added without updating the type.

## Artifacts:
- `frontend/pages/admin/products/[id].vue` — added `id: v.id` to variant mapping
- `frontend/composables/useProducts.ts` — added `id?: string` to `ProductCreate.variants` array item type

## Contracts Verified:
- No hardcoded colors or spacing: OK (no styling changes)
- npm run lint (vue-tsc --noEmit): OK (no errors)
- npm run typecheck (vue-tsc --noEmit): OK (no errors)

## Next:
- testing-agent: e2e test for admin product edit — verify that saving a product with existing variants sends variant `id` in the request payload

## Blockers:
- none
