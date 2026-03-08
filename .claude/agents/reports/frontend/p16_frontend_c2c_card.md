## Status: DONE

## Completed:
- Создан composable `useC2CShipment.ts` для загрузки данных C2C отправки
- Создана страница `pages/admin/orders/[id].vue` с детальным просмотром заказа
- Реализован блок C2CShipmentCard с условным рендерингом для ozon/wb провайдеров
- Добавлены ссылки на детальную страницу в `pages/admin/orders/index.vue`
- Реализована функция копирования данных через Clipboard API с toast-уведомлениями
- Реализована кнопка deeplink для открытия мобильного приложения провайдера

## Artifacts:
- `/Users/meteo/Documents/WWW/site-builder/frontend/composables/useC2CShipment.ts`
- `/Users/meteo/Documents/WWW/site-builder/frontend/pages/admin/orders/[id].vue`
- `/Users/meteo/Documents/WWW/site-builder/frontend/pages/admin/orders/index.vue` (обновлён)

## Implementation Details:

### useC2CShipment.ts
- Типизация `C2CShipmentResponse` согласно API контракту
- Экспорт composable функции для вызова endpoint `/delivery/orders/{orderId}/c2c-shipment`

### pages/admin/orders/[id].vue
- Загрузка данных заказа через `useApi('/admin/orders/{id}')`
- Условный рендеринг C2C блока только для `delivery_provider === 'ozon' || 'wb'`
- Отображение полей: получатель, телефон, ПВЗ, объявленная ценность, вес, комментарий (если есть)
- Нумерованный список инструкций с акцентной нумерацией
- Кнопка deeplink открывает URL в новой вкладке
- Кнопка копирования формирует текстовый блок и использует `navigator.clipboard.writeText()`
- Toast-уведомления через `useToast().success()` / `.error()`
- Skeleton loaders для состояния загрузки
- Обработка ошибок загрузки C2C данных

### pages/admin/orders/index.vue
- Добавлен `NuxtLink` вокруг ID заказа с `data-testid="order-detail-link"`
- Добавлен `data-testid="order-card"` на строку таблицы
- Стили для ссылки с hover-эффектом через `var(--color-accent)`

## Contracts Verified:
- API shape matches api_contracts.md: ✅ (GET /api/v1/delivery/orders/{order_id}/c2c-shipment)
- npm run lint: ✅ (0 errors)
- npm run typecheck: ✅ (0 errors)
- Только var(--color-*) токены: ✅ (accent, text, text-2, surface, surface-2, border, error)
- Mobile-first: ✅ (кнопки полной ширины на <768px через flex-direction: column)
- data-testid обязательные: ✅ (все 13 testid присутствуют)

## data-testid Coverage:
- `order-detail-page` — корневой div страницы [id].vue
- `order-back-link` — ссылка "Назад к списку"
- `order-detail-status` — бейдж статуса заказа
- `order-detail-total` — сумма заказа
- `c2c-shipment-card` — UCard блока C2C
- `c2c-recipient` — поле имени получателя
- `c2c-phone` — телефон получателя
- `c2c-pvz` — поле ПВЗ (код + адрес)
- `c2c-value` — объявленная ценность
- `c2c-instructions` — блок инструкции
- `c2c-open-app-btn` — кнопка deeplink
- `c2c-copy-btn` — кнопка копирования
- `order-card` — строка таблицы в index.vue
- `order-detail-link` — ссылка на детальную страницу

## Design Tokens Used:
- Colors: `--color-accent`, `--color-accent-hover`, `--color-text`, `--color-text-2`, `--color-surface`, `--color-surface-2`, `--color-border`, `--color-error`
- Transitions: `--transition-fast`
- Typography: `--text-xs`, `--text-sm`, `--text-base`, `--text-lg`, `--text-xl`
- Radius: `--radius-md`

## Next:
- testing-agent: e2e тесты для страницы детального просмотра заказа и функционала C2C карточки

## Blockers:
- none
