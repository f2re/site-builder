## Status: DONE

## Completed:
- BUG-CART-01 step 1 (cartStore.ts): Added maxStock?: number to StoreCartItem; addItem() now accepts Omit<StoreCartItem, 'quantity'> and returns boolean; checks existing.quantity >= (existing.maxStock ?? Infinity) before incrementing — returns false if limit reached; updateQuantity() clamps with Math.min(quantity, item.maxStock ?? quantity)
- BUG-CART-01 step 2 ([slug].vue): addItem called with maxStock: currentStock.value (from selectedVariant.stock_quantity); if addItem returns false → toast.warning shown with stock count
- BUG-CART-01 step 3 (ProductCard.vue): addItem called with maxStock: product.stock; same false-return toast.warning pattern
- BUG-CART-01 step 4 (cart.vue): "+" button :disabled when item.quantity >= (item.maxStock ?? Infinity); updateQuantity() checks limit before calling store and shows toast.warning; "макс. N шт." hint displayed below stepper when maxStock is set; data-testid added: cart-item, cart-item-qty, cart-qty-increase, cart-qty-decrease, cart-remove-btn, cart-total, checkout-btn
- FEAT-CART-01: Created components/shop/QuickBuyModal.vue with full implementation:
  - Props: isOpen, productName, productImage, variantName, price
  - Emits: close, submitted
  - Phone input with pure JS mask (+7 (___) ___-__-__)
  - Client-side validation (name required, phone >= 11 digits)
  - POST /api/v1/orders/quick-buy with fallback setTimeout(1000) on 404/500
  - Loading state with spinner on submit button
  - Transition: fade+scale on desktop, bottom-sheet (translateY) on mobile (max-width: 768px)
  - ESC closes, click on backdrop closes
  - Focus trap (Tab/Shift+Tab cycle within modal)
  - Focus on first input on open
  - role="dialog" aria-modal="true" aria-label="Быстрый заказ"
  - All data-testid: quick-buy-modal, quick-buy-name, quick-buy-phone, quick-buy-comment, quick-buy-submit, quick-buy-close
  - Only var(--color-*) tokens, no hardcoded colors
- [slug].vue: QuickBuyModal integrated; btn-one-click opens modal with current product/variant data; submitted event triggers toast.success('Заявка принята!', ...); data-testid="btn-one-click" on trigger button

## Artifacts:
- frontend/stores/cartStore.ts
- frontend/pages/cart.vue
- frontend/pages/products/[slug].vue
- frontend/components/catalog/ProductCard.vue
- frontend/components/shop/QuickBuyModal.vue (created)

## Contracts Verified:
- data-testid on all required elements: OK
- Only var(--color-*) tokens: OK
- Mobile-first breakpoints: OK
- npm run lint: OK (0 errors)
- npm run typecheck: OK (0 errors)

## Accessibility:
- Modal: role="dialog", aria-modal, aria-label, focus trap, ESC closes
- Focus on first input on modal open
- All icon buttons have aria-label

## Next:
- testing-agent: e2e tests for cart stock enforcement, QuickBuyModal flow (open, fill, submit, ESC close)

## Blockers:
- none
