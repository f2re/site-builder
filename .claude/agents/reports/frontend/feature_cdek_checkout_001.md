## Status: DONE

## Backend Endpoints Status
Backend `/delivery/*` endpoints EXIST in `backend/app/api/v1/delivery/router.py`:
- `GET /delivery/cities?query=&country_codes=` — city search
- `GET /delivery/pickup-points?city_code=` — PVZ list
- `GET /delivery/calculate?from_city_code=&to_city_code=&weight_grams=&tariff_code=` — delivery cost

Note: Backend uses `GET` for calculate (not `POST` as in api_contracts.md). Frontend `useCdek.ts` uses GET accordingly.
Backend response schema for `CityRead.code` is `int` (not `str`). Frontend types match this exactly.

## Completed:
- Created `frontend/composables/useCdek.ts` — typed composable for all 3 CDEK API calls with graceful fallback to 10 mock cities on backend error
- Created `frontend/stores/deliveryStore.ts` — full Pinia store with deliveryType, selectedCity, selectedPickupPoint, courierAddress, calcResult; persists to localStorage
- Rewrote `frontend/pages/checkout/index.vue` — full checkout page with:
  - City search input with 300ms debounce, dropdown autocomplete
  - Delivery type toggle (pickup / courier) with data-testid
  - PVZ list with selection, loading/empty states
  - Courier address form (street, building, apartment, comment)
  - Real-time delivery cost calculation
  - Order summary with items, delivery cost, total
  - "Оформить заказ" button — disabled until delivery ready
  - POST /orders/ on submit → redirect to payment_url
  - State restored from localStorage on mount

## Artifacts:
- `frontend/composables/useCdek.ts` (created)
- `frontend/stores/deliveryStore.ts` (created)
- `frontend/pages/checkout/index.vue` (rewritten)

## Contracts Verified:
- API shape matches api_contracts.md: OK (with noted GET vs POST discrepancy for /delivery/calculate — backend is GET)
- City code type: `number` (matches backend `int`)
- PVZ schema: `{ code: str, name, address, latitude, longitude, work_time, phone, note? }` — matches backend `PickupPointRead`
- Order POST `/orders/` body: `{ delivery_type, pvz_code?, address?, payment_method }` — matches api_contracts.md
- data-testid on all elements: OK
  - city-input, city-search-results, city-option
  - delivery-type-pickup, delivery-type-courier
  - pvz-list, pvz-item, pvz-select-btn
  - courier-street, courier-building
  - delivery-cost, order-total, checkout-btn, delivery-form
- Only var(--color-*) tokens: OK — no hardcoded colors
- Mobile-first breakpoints: OK — 1024px grid breakpoint
- npm run lint: OK (0 errors)
- npm run typecheck: OK (0 errors)

## Accessibility:
- All form inputs have labels (no placeholder-as-label)
- aria-label on icon-only clear button
- Touch targets >= 44px
- Focus rings via tokens.css :focus-visible

## Next:
- testing-agent: e2e tests for checkout flow (city search, PVZ selection, order submission)
- backend-agent: verify `/delivery/calculate` contract discrepancy (GET vs POST in api_contracts.md)

## Blockers:
- None — all backend endpoints exist and are functional
