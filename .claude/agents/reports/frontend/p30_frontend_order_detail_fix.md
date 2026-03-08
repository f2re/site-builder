## Status: DONE

## Completed:
- Исправлена главная причина краша (строки 55-57): удалён условный вызов `useC2CShipment` через `isC2CProvider.value`. Теперь `useC2CShipment(orderId)` вызывается безусловно — корректно для `script setup` с `await`. Шаблон уже содержал `v-if="isC2CProvider && !c2cPending && !c2cError && c2cData"` — этого достаточно для условного отображения C2C-карточки.
- Исправлена типизация `OrderRead.user_id`: `string` → `string | null`
- Исправлена ссылка на пользователя: при `user_id === null` вместо `<NuxtLink :to="/admin/users/null">` отображается `<span>` с текстом `'Гость'`
- Добавлено пустое состояние для таблицы товаров: при `order.items.length === 0` показывается строка "Нет товаров в заказе" вместо пустого tbody

## Artifacts:
- `/Users/meteo/Documents/WWW/site-builder/frontend/pages/admin/orders/[id].vue`

## Contracts Verified:
- API shape matches api_contracts.md: OK (useC2CShipment использует `/delivery/orders/${orderId}/c2c-shipment`)
- npm run lint: OK (0 ошибок)
- npm run typecheck: OK (0 ошибок)
- Только var(--color-*) токены: OK (новые элементы используют только существующие классы с токенами)
- data-testid на всех элементах: OK (customer-link сохранён на обоих ветках v-if/v-else)

## Changes Summary:

### 1. Безусловный вызов useC2CShipment (критический фикс)
**До:**
```js
const { data: c2cData, pending: c2cPending, error: c2cError } = isC2CProvider.value
  ? await useC2CShipment(orderId)
  : { data: ref(null), pending: ref(false), error: ref(null) }
```
**После:**
```js
const { data: c2cData, pending: c2cPending, error: c2cError } = await useC2CShipment(orderId)
```

### 2. Типизация user_id
**До:** `user_id: string`
**После:** `user_id: string | null`

### 3. NuxtLink при user_id=null
**До:** `<NuxtLink :to="/admin/users/${order.user_id}">` (генерировал `/admin/users/null`)
**После:** `v-if="order.user_id"` показывает NuxtLink, `v-else` показывает span

### 4. Пустое состояние items
Добавлена строка `<tr v-if="!order.items || order.items.length === 0">` с сообщением "Нет товаров в заказе"

## Next:
- testing-agent: e2e тесты для /admin/orders/[id] с order.user_id=null и order.items=[]

## Blockers:
- none
