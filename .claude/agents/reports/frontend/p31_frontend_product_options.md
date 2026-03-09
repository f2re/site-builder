## Status: DONE

## Completed:
- Created `frontend/composables/useProductOptions.ts` — composable encapsulating selection state, default auto-selection, debounced price calculation via `POST /products/calculate-price`, `allRequiredSelected` validation, and `selectedValueIds` computed array
- Created `frontend/components/product/ProductOptionSelector.vue` — pill/chip radio-style selector component; shows `+X ₽` / `Без доплаты` / `-X ₽` modifiers; highlights selected option with accent; shows validation error "Выберите вариант" with red border when `showValidation=true` and group is unselected-required; mobile-responsive with `flex-wrap`
- Created `frontend/stores/productOptions.ts` — Pinia store with `groups` state keyed by `productId`; all 6 actions: `createGroup`, `updateGroup`, `deleteGroup`, `createValue`, `updateValue`, `deleteValue`; `setGroups()` to initialize from product data without extra API call; `isLoading()` per-product loading state
- Created `frontend/components/admin/ProductOptionGroupsEditor.vue` — full CRUD admin editor for option groups and values; inline group edit forms (name, is_required toggle, sort_order); inline value edit forms (name, price_modifier, is_default, sku_suffix); confirm dialogs via `useConfirm()` before deletion; toast notifications via `useToast()` on success/error; loading overlay with spinner; all interactive elements have `data-testid` attributes
- Updated `frontend/pages/products/[slug].vue`: replaced inline option group rendering with `<ProductOptionSelector>` component; integrated `useProductOptions` composable; added price breakdown section with skeleton loading; add-to-cart button disabled when required options not selected; shows "Выберите опции" label and triggers validation on click attempt; passes `selectedOptionValueIds` to cart
- Updated `frontend/pages/admin/products/[id].vue`: replaced `ProductOptionsManager` with `ProductOptionGroupsEditor`; section titled "Комплектации (опции товара)"

## Artifacts:
- frontend/composables/useProductOptions.ts
- frontend/components/product/ProductOptionSelector.vue
- frontend/stores/productOptions.ts
- frontend/components/admin/ProductOptionGroupsEditor.vue
- frontend/pages/products/[slug].vue (updated)
- frontend/pages/admin/products/[id].vue (updated)

## Contracts Verified:
- API shape matches api_contracts.md: OK (`POST /products/calculate-price` body/response shape)
- TypeScript types `ProductOptionGroup`, `ProductOptionValue`, `ProductPriceCalculationResponse` reused from `useProducts.ts` — no duplication
- `Product` type already includes `option_groups: ProductOptionGroup[]` — no change needed
- Only `var(--color-*)` tokens used — no hardcoded colors
- All interactive elements have `data-testid` attributes
- Mobile-first responsive (flex-wrap on chips, column layout on 480px breakpoint)
- npm run lint: OK
- npm run typecheck: OK

## Accessibility:
- Required group indicator: asterisk with `aria-label="Обязательное поле"`
- Option chip buttons: `aria-pressed` state, `aria-label` with name + modifier
- Price breakdown: `aria-live="polite"` region
- Admin loading overlay: `aria-live="polite"` + `aria-label="Загрузка"`
- Validation error: `role="alert"` on error message div
- All icon-only admin buttons have `title` + `aria-label`

## Next:
- testing-agent: e2e tests for product option selection, price calculation flow, and add-to-cart validation
- testing-agent: integration tests for admin ProductOptionGroupsEditor CRUD

## Blockers:
- none
