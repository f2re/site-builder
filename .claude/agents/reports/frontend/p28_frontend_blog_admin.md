## Status: DONE

## Completed:
- Fixed `frontend/pages/admin/blog/index.vue`: replaced `limit: 100` param with `per_page: 20` and added `status: 'all'` to show drafts to admin. Added proper cursor-based pagination (Prev/Next buttons), using `after` param per API contract. "Далее" button is disabled when `next_cursor === null`.
- Added `getCategories`, `adminGetCategories`, `adminCreateCategory`, `adminUpdateCategory`, `adminDeleteCategory` methods to `frontend/composables/useBlog.ts`. Also added `BlogCategoryListResponse` interface and updated `BlogCategory` to include `posts_count` and `description` fields. Added optional `created_at` to `BlogPost` to match actual backend response.
- Created `frontend/pages/admin/blog/categories.vue`: table listing blog categories (name, slug, posts_count), modal form for create/edit with name/slug/description fields, delete with `useConfirm()`, all elements have `data-testid` attributes.
- Updated `frontend/layouts/admin.vue`: split "Блог" nav item into "Блог / Посты" (`/admin/blog`) and "Блог / Категории" (`/admin/blog/categories`) in both desktop sidebar and mobile drawer nav arrays.
- Verified `frontend/pages/blog/index.vue`: public blog pagination already correct — `hasMore` uses `!!next_cursor`, `loadMore` only fires on button click (no IntersectionObserver), guard `if (!cursor.value || loadingMore.value) return` prevents extra requests.

## Artifacts:
- frontend/pages/admin/blog/index.vue
- frontend/pages/admin/blog/categories.vue (new)
- frontend/composables/useBlog.ts
- frontend/layouts/admin.vue

## Contracts Verified:
- API shape matches api_contracts.md: OK
  - `GET /api/v1/blog/posts` uses `per_page` and `after` params, response `{ items, next_cursor, total }`
  - `GET /api/v1/blog/admin/categories` returns `BlogCategory[]`
  - `POST /api/v1/blog/admin/categories` accepts `{ name, slug, description? }`
  - `PUT /api/v1/blog/admin/categories/{id}` partial update
  - `DELETE /api/v1/blog/admin/categories/{id}` 204 No Content
- data-testid on all interactive elements: OK
- Only var(--color-*) CSS tokens used: OK
- npm run lint: OK (exit 0)
- npm run type-check: OK (exit 0)

## Accessibility:
- All icon-only buttons have aria-label
- Modal uses UModal component (existing accessible implementation)

## Next:
- testing-agent: e2e tests for /admin/blog and /admin/blog/categories pages

## Blockers:
- none
