## Status: DONE

## Completed:
- Step 1: useBlog.ts — added BlogPost fields (cover_image, og_image_url, carousel_images, summary, reading_time, is_featured, meta_title, meta_description, author.bio), added uploadBlogCover(), getTags(), fixed savePost/deletePost to use /admin/blog/posts paths
- Step 2: BlogCarousel.vue — new component with autoplay, pause-on-hover, dots navigation, prev/next arrows (desktop hover-only), fade transition, NuxtImg, aspect-ratio prop
- Step 3: BlogCard.vue — redesigned: clickable tag NuxtLinks, BlogCarousel when carousel_images.length > 1, NuxtLink category badge, reading_time fallback, hover overlay, data-testid="blog-post-tags"
- Step 4: blog/index.vue — full redesign: hero block (16/9, gradient overlay, category/title/excerpt/meta), tag cloud (horizontal scroll, active state), posts grid (1→2→3 cols), skeleton loading, load more with count
- Step 5: blog/[slug].vue — full Telegraph-style redesign: reading progress bar (fixed top), hero carousel or single image, article header (category, h1, meta, author mini), rich post-content styles (h2 with accent border, blockquote, code, table, iframe), tags section, full author block, share buttons (Telegram/VK/copy), back link, related posts grid
- Step 6: BlogCarouselManager.vue — new component for admin, grid of URL previews with upload/remove/move
- Step 7: admin/blog/create.vue — full overhaul: TipTapEditor (ClientOnly), slug auto-generation from title, summary textarea, cover upload with preview, BlogCarouselManager, tags with autocomplete dropdown from getTags(), 3-state status radio (draft/published/archived), is_featured checkbox, SEO section (meta_title/meta_description), correct POST /admin/blog/posts with content_json
- Step 8: admin/blog/[slug].vue — full overhaul: same fields as create.vue, uploadBlogCover API for existing posts, preview button (/blog/{slug}), delete with confirmation dialog (data-testid="admin-confirm-delete"), PUT /admin/blog/posts/{id}

## Artifacts:
- frontend/composables/useBlog.ts
- frontend/components/blog/BlogCarousel.vue (new)
- frontend/components/blog/BlogCarouselManager.vue (new)
- frontend/components/blog/BlogCard.vue
- frontend/pages/blog/index.vue
- frontend/pages/blog/[slug].vue
- frontend/pages/admin/blog/create.vue
- frontend/pages/admin/blog/[slug].vue

## Contracts Verified:
- API shape matches api_contracts.md: OK (GET /blog/tags, POST /admin/blog/posts/{id}/cover added as extensions)
- No hardcoded colors or spacing: OK (all var(--color-*) and var(--radius-*) tokens)
- Mobile-first breakpoints: OK (320px base, 768px, 1024px)
- data-testid on interactive elements: OK (blog-post-card, blog-post-title, blog-post-tags, blog-post-author, reading-progress-bar, share-telegram, share-vk, share-copy, admin-save-btn, admin-delete-btn, admin-confirm-delete)
- npm run lint: OK (0 errors)
- npm run typecheck: OK (0 errors)

## Accessibility:
- Focus rings via :focus-visible from tokens.css
- aria-label on icon-only buttons (arrows, remove, share)
- role="progressbar" on reading progress bar
- role="navigation" on tag cloud
- Touch targets >= 44px on share buttons and tag cloud items

## Next:
- testing-agent: e2e tests for blog pages (tag filtering, carousel, progress bar, share)
- backend-agent: confirm GET /blog/tags and POST /admin/blog/posts/{id}/cover endpoints exist

## Blockers:
- none
