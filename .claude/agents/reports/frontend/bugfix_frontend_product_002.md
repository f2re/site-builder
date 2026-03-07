## Status: DONE

## Completed:
- BUG-FE-01: Added adminUploadProductImage, adminDeleteProductImage, adminSetProductCoverImage to return object in useProducts()
- BUG-FE-02: Replaced mock variants with real product.variants; selectedVariant is now ref<ProductVariant | null> initialized from product.variants[0]; price and stock derived from selectedVariant.value; switcher hidden when only 1 variant; variant buttons show real name + price badge
- BUG-FE-03: Created components/blog/TipTapViewer.vue (editable=false, StarterKit + Image extensions); [slug].vue now renders description_html first (v-html), falls back to TipTapViewer if content_json present, then plain text; description section hidden when all fields empty
- BUG-FE-04: Added null-safe categoriesData.value?.items guard on CategorySidebar v-if; fixed total.value = data.value.total ?? 0; ProductCategory interface updated with is_active?: boolean and optional parent_id
- BUG-FE-05: Added search?: string to getProducts() params; maps it to query param 'q' before passing to useFetch
- BUG-FE-06: Added data-testid="product-card" on NuxtLink, data-testid="product-title" on h3, data-testid="product-price" on price-value span, data-testid="product-stock" on stock badge in ProductCard.vue; added data-testid="add-to-cart-btn" on add button, data-testid="product-stock" on stock block in [slug].vue
- UX: Stock shows exact count ("В наличии: N шт."); when stock <= 5 shows warning color via --color-warning; "В корзину" button disabled + shows "Нет в наличии" when stock <= 0; breadcrumbs no longer show "..." when category not loaded; description section hidden when all content fields empty; sticky bar shows selected variant name and currentPrice from selectedVariant

## Artifacts:
- frontend/composables/useProducts.ts
- frontend/components/blog/TipTapViewer.vue (created)
- frontend/components/catalog/ProductCard.vue
- frontend/pages/products/[slug].vue (rewritten)
- frontend/pages/products/index.vue

## Contracts Verified:
- data-testid on all required elements: OK
- Only var(--color-*) tokens used, no hardcoded colors: OK
- Mobile-first breakpoints: OK
- npm run lint: OK (0 errors)
- npm run typecheck: OK (0 errors)

## Accessibility:
- axe-core: not run (no dev server in CI)
- All buttons have aria-label or visible text
- Focus ring via :focus-visible in tokens.css

## Next:
- testing-agent: e2e smoke tests for product page variants, stock display, TipTapViewer

## Blockers:
- none
