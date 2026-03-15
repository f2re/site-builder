## Status: DONE

## Problem
Product option groups showed headers but no interactive elements for selection. Checkbox-type option groups had no rendering at all. Selected options were not displayed in order detail pages (admin and profile).

## Root Causes Found
1. **ProductOptionSelector.vue** had `<template v-if="group.type !== 'checkbox'">` for radio groups but NO corresponding `<template v-else>` block for checkbox groups -- checkbox values were silently hidden
2. **useProductOptions.ts** typed `selectedOptions` as `Record<string, string>` -- cannot hold arrays needed for checkbox multi-select
3. **Admin order detail** (`admin/orders/[id].vue`) -- `OrderItem` interface lacked `selected_options` field; options not rendered in items table
4. **Profile order detail** (`profile/orders/[id].vue`) -- `OrderItem` in `useOrders.ts` lacked `selected_options`; options not rendered
5. **addToCart in [slug].vue** -- only handled string values from `selectedOptions`, not string arrays from checkbox groups
6. **QuickBuyModal selected-options prop** -- same issue with string-only mapping

## Completed
- Added checkbox multi-select rendering in ProductOptionSelector.vue (checkbox chips with checkmark icon)
- Updated `useProductOptions.ts` to use `Record<string, string | string[]>` for selectedOptions
- Updated `allRequiredSelected` computed to validate checkbox groups (array length > 0)
- Updated `selectedValueIds` computed to flatten both string and string[] values
- Updated `addToCart` in [slug].vue to iterate over array values for checkbox groups
- Updated QuickBuyModal selected-options prop to use `flatMap` for both types
- Added `selected_options` to OrderItem in useOrders.ts
- Added options display in profile/orders/[id].vue with data-testid
- Added `selected_options` to OrderItem interface in admin/orders/[id].vue
- Added options display in admin order items table with data-testid
- Validation for checkbox required groups now works (shows error if none selected)

## Artifacts
- frontend/components/product/ProductOptionSelector.vue
- frontend/composables/useProductOptions.ts
- frontend/composables/useOrders.ts
- frontend/pages/products/[slug].vue
- frontend/pages/profile/orders/[id].vue
- frontend/pages/admin/orders/[id].vue

## Contracts Verified
- data-testid on all new interactive elements: OK
- Only var(--color-*) tokens used: OK
- API shape (selected_options on OrderItem): OK
- vue-tsc --noEmit: OK (zero errors)

## Option Chain Flow (verified)
1. Product page: options render as interactive chips (radio: single-select, checkbox: multi-select) -- FIXED
2. Price recalculation: debounced via calculate-price API on option change -- was working, still works
3. Add to cart: selectedOptionValueIds + option snapshots passed to cartStore -- FIXED for checkbox
4. Cart page: selectedOptions displayed per item -- was working
5. Checkout: options sent to backend via server-side cart (addToCart API sends selected_option_value_ids) -- was working
6. Admin order detail: selected_options displayed in items table -- ADDED
7. Profile order detail: selected_options displayed per item -- ADDED

## Next
- testing-agent: e2e tests for product options selection, cart with options, order detail options display

## Blockers
- none
