## Status: DONE

## Completed:
- BUG 1 fixed: renamed `page_cursor` → `after` in `useBlog.ts` getPosts() params; `hasMore` logic already correct (`!!next_cursor`)
- BUG 2 fixed: replaced `<NuxtImg>` with `<img>` in `BlogCard.vue` for blog cover images (IPX bypass)
- FEATURE 1: Section tabs added to `blog/index.vue` — "Все" / "Новости" / "Инструкции" with route query `section=`, reset cursor on tab switch, breadcrumbs updated
- FEATURE 2: `useBlog.ts` updated — `section?` added to `BlogCategory` interface, `getPosts()` params, `adminCreateCategory()` and `adminUpdateCategory()` signatures
- FEATURE 3: `admin/blog/create.vue` and `admin/blog/[slug].vue` — added `category_id` field to form, fetching categories via `adminGetCategories()`, grouped `<select>` by section (Новости / Инструкции / Без секции), `data-testid="blog-category-select"`, category pre-populated from existing post data in edit form
- FEATURE 4: `admin/blog/categories.vue` — section `<select>` in create/edit modal, section badges in table (Новости=info color, Инструкции=success color), `data-testid="admin-blog-category-section-select"`

## Artifacts:
- `frontend/composables/useBlog.ts`
- `frontend/components/blog/BlogCard.vue`
- `frontend/pages/blog/index.vue`
- `frontend/pages/admin/blog/create.vue`
- `frontend/pages/admin/blog/[slug].vue`
- `frontend/pages/admin/blog/categories.vue`

## Contracts Verified:
- API shape matches api_contracts.md: OK (GET /blog/posts uses `after` cursor param as documented)
- data-testid on all required elements: OK (`blog-section-tabs`, `blog-section-tab-all`, `blog-section-tab-news`, `blog-section-tab-instructions`, `blog-category-select`, `admin-blog-category-section-select`)
- Only var(--color-*) tokens in CSS: OK
- Mobile-first, touch targets >= 44px: OK (section tabs and category selects have min-height: 44px)
- npm run lint (vue-tsc --noEmit): OK, 0 errors
- npm run typecheck (vue-tsc --noEmit): OK, 0 errors

## Accessibility:
- Section tabs use role="tablist" / role="tab" / aria-selected
- Category selects have associated <label> via htmlFor/id
- All interactive elements have data-testid attributes

## Next:
- testing-agent: e2e tests for section tab navigation, pagination load-more, category select in admin forms

## Blockers:
- none
