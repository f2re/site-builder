## Status: DONE

## Completed:
- Added `doc_iframe_url?: string | null` to `BlogPost` interface in `useBlog.ts`
- Added `doc_iframe_url: ''` to `form` reactive in `admin/blog/create.vue`
- Added `doc_iframe_url` to save payload in `create.vue`
- Added `UInput` for `doc_iframe_url` after content editor in `create.vue` template
- Added `doc_iframe_url: ''` to `form` reactive in `admin/blog/[slug].vue`
- Added `doc_iframe_url?: string | null` to inline type in `useApi` call in `[slug].vue`
- Added prefill `form.doc_iframe_url = post.value.doc_iframe_url || ''` in `watchEffect` in `[slug].vue`
- Added `doc_iframe_url` to save payload in `[slug].vue`
- Added `UInput` for `doc_iframe_url` after content editor in `[slug].vue` template
- Added `import ProductDocIframe from '~/components/shop/ProductDocIframe.vue'` in `blog/[slug].vue`
- Added `<ProductDocIframe v-if="post!.doc_iframe_url" :url="post!.doc_iframe_url" data-testid="blog-doc-iframe" />` after `.post-content` div in `blog/[slug].vue`

## Artifacts:
- frontend/composables/useBlog.ts
- frontend/pages/admin/blog/create.vue
- frontend/pages/admin/blog/[slug].vue
- frontend/pages/blog/[slug].vue

## Contracts Verified:
- API shape: `doc_iframe_url` added as optional nullable string, consistent with product pattern
- No hardcoded colors or spacing in .vue files: OK
- data-testid on new input: `blog-doc-iframe-url-input` (admin), `blog-doc-iframe` (public)
- npm run lint: OK (no errors)
- npm run typecheck: OK (no errors)

## Next:
- backend-agent: ensure `doc_iframe_url` field is persisted in `BlogPost` model and included in API response schema
- testing-agent: e2e tests for blog doc iframe field in admin and public pages

## Blockers:
- none
