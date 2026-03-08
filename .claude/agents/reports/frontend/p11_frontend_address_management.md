## Status: DONE

## Completed:
- Создан composable useAddresses.ts с CRUD методами для /users/me/addresses
- Реализована страница /profile/addresses с управлением адресами
- Созданы компоненты AddressCard, AddressForm, AddressSelector
- Интегрирован AddressSelector в checkout для выбора сохранённого адреса
- Обновлена страница orders/[id].vue с StatusBadge и TrackingButton
- Добавлен real-time polling статуса заказа (30с)
- Реализованы компоненты StatusBadge и TrackingButton

## Artifacts:
- /Users/meteo/Documents/WWW/site-builder/frontend/composables/useAddresses.ts
- /Users/meteo/Documents/WWW/site-builder/frontend/pages/profile/addresses.vue
- /Users/meteo/Documents/WWW/site-builder/frontend/components/profile/AddressCard.vue
- /Users/meteo/Documents/WWW/site-builder/frontend/components/profile/AddressForm.vue
- /Users/meteo/Documents/WWW/site-builder/frontend/components/shop/AddressSelector.vue
- /Users/meteo/Documents/WWW/site-builder/frontend/components/orders/StatusBadge.vue
- /Users/meteo/Documents/WWW/site-builder/frontend/components/orders/TrackingButton.vue
- /Users/meteo/Documents/WWW/site-builder/frontend/pages/orders/[id].vue (updated)
- /Users/meteo/Documents/WWW/site-builder/frontend/pages/checkout/index.vue (updated)

## Contracts Verified:
- API shape matches api_contracts.md: ✅
  - GET /users/me/addresses → { items: DeliveryAddress[] }
  - POST /users/me/addresses → DeliveryAddress
  - PATCH /users/me/addresses/{id} → DeliveryAddress
  - DELETE /users/me/addresses/{id} → 204
  - POST /users/me/addresses/{id}/set-default → DeliveryAddress
- data-testid на всех интерактивных элементах: ✅
  - address-card, address-name, default-badge, set-default-btn, edit-address-btn, delete-address-btn
  - address-form, address-name-input, recipient-name-input, recipient-phone-input, city-input, full-address-input
  - address-selector, address-option, new-address-option
  - order-status-badge, tracking-btn, order-detail, order-item
- Только var(--color-*) токены: ✅
- Mobile-first breakpoints: ✅
- npm run lint: ✅ (exit code 0)
- npm run typecheck: ✅ (exit code 0)

## Implementation Details:
- AddressSelector автоматически выбирает адрес по умолчанию при загрузке
- Polling заказа запускается только для статусов shipped/paid, останавливается при delivered/cancelled
- Toast уведомление при изменении статуса заказа
- StatusBadge использует color-mix для динамической генерации фона
- TrackingButton открывает tracking_url в новой вкладке
- Форма адреса поддерживает создание и редактирование
- Modal overlay для формы адреса с закрытием по клику вне области

## Next:
- testing-agent: e2e тесты для /profile/addresses, checkout с выбором адреса, order tracking

## Blockers:
- none
