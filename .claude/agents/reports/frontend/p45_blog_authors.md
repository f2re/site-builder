## Status: DONE

## Completed:
- Added `BlogAuthor` interface to `useBlog.ts`
- Added `adminGetAuthors()`, `adminGetMyAuthorProfile()`, `adminUpdateMyAuthorProfile()` to `useBlog.ts`
- Added `author_id` field to create form in `pages/admin/blog/create.vue`
- Added author `<select>` with `data-testid="blog-author-select"` to create form (after Category)
- Added `author_id` to POST payload in create.vue
- Added `author_id` field to edit form in `pages/admin/blog/[slug].vue`
- Added author `<select>` with `data-testid="blog-author-select"` to edit form (after Category)
- Pre-fill `form.author_id` from `post.value.author?.id` in `watchEffect`
- Added `author_id` to PUT payload in [slug].vue
- Created `pages/admin/author-profile.vue` — profile page with display_name, bio, avatar_url fields
- Added `data-testid` attributes: `author-profile-name`, `author-profile-bio`, `author-profile-avatar`, `author-profile-save`
- Added avatar preview with `<img>` when `avatar_url` is set, placeholder icon otherwise
- Added "Профиль автора" (icon: `ph:user-circle-bold`) to admin layout `navItems` (both desktop sidebar and mobile drawer share same array)

## Artifacts:
- frontend/composables/useBlog.ts
- frontend/pages/admin/blog/create.vue
- frontend/pages/admin/blog/[slug].vue
- frontend/pages/admin/author-profile.vue
- frontend/layouts/admin.vue

## Contracts Verified:
- API shape matches task spec: `GET /blog/admin/authors`, `GET /blog/admin/authors/me`, `PUT /blog/admin/authors/me`
- `BlogPostCreate` now accepts `author_id?: string` passed in payload
- data-testid on all interactive elements: OK
- Only var(--color-*) tokens used, no hardcoded colors: OK
- npm run lint: OK (no errors)
- npm run typecheck: OK (no errors)

## Next:
- testing-agent: e2e tests for author select in blog create/edit, author-profile page CRUD

## Blockers:
- none
