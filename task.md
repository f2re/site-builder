@orchestrator
## 1. Дублирование страницы логина в админке

### Диагноз

`auth/login.vue` использует `layout: 'default'`. Layout `default.vue` — это **публичный** layout сайта (шапка, футер). Когда неавторизованный пользователь попадает на `/admin/*`, middleware редиректит на `/auth/login`, который рендерится внутри `default` layout. Если `default` layout содержит `<slot>` или `<NuxtPage>` где-то в теле — страница логина рендерится дважды: один раз как основной контент, второй раз внутри layout-слота.

Вероятная причина: `default.vue` содержит `<NuxtPage />` или `<slot />` в теле страницы (не только в `<main>`), либо layout рендерит дочерний контент дважды.

### Что НАДО сделать

#### frontend-agent:
- Проверить `frontend/layouts/default.vue` — убедиться что `<slot />` или `<NuxtPage />` встречается ровно **один раз**
- Страница `auth/login.vue` использует `layout: 'default'` — это корректно, но нужно убедиться что `default` layout не добавляет лишних оберток с `<slot>`
- Если `default` layout содержит header/footer с собственным `<slot>` для контента — убедиться что auth-страницы не получают двойной рендер
- Альтернативное решение: создать отдельный layout `auth.vue` (минимальный, без header/footer) и переключить все страницы в `pages/auth/*.vue` на `layout: 'auth'`

### Что НЕЛЬЗЯ делать
- Нельзя менять `definePageMeta` в admin-страницах — они уже используют `layout: false` корректно
- Нельзя убирать middleware `auth` с admin-страниц
- Нельзя делать layout `auth` с `layout: false` — это сломает SSR

### Граничные условия
- После фикса: `/auth/login` рендерится ровно один раз, без дублирования
- Авторизованный пользователь, заходящий на `/auth/login`, должен редиректиться на `/profile` (добавить guard в login.vue если его нет)

---

## 2. 500 на /admin/orders/[id] — TypeError: Cannot destructure property 'open'

### Диагноз

Ошибка в `frontend/pages/admin/orders/[id].vue:261`:
```
TypeError: Cannot destructure property 'open' of 'undefined' as it is undefined.
```

Причина: `USelectMenu` использует scoped slot `#default="{ open }"`:
```vue
<USelectMenu ...>
  <template #default="{ open }">   <!-- строка ~193 -->
    <UButton ...>
      <UIcon :class="{ 'rotate-180': open }" />
    </UButton>
  </template>
</USelectMenu>
```

`USelectMenu` — это компонент из **Nuxt UI**, который передаёт `{ open }` в default slot. Но в проекте используется **кастомный** `USelectMenu` или компонент не поддерживает этот slot API. При SSR slot вызывается с `undefined` вместо объекта `{ open }`.

### Что НАДО сделать

#### frontend-agent:
- В `frontend/pages/admin/orders/[id].vue` заменить `USelectMenu` на нативный `<select>` или кастомный компонент проекта (`USelect` из `~/components/U/USelect.vue`)
- Убрать scoped slot `#default="{ open }"` — он несовместим с кастомным компонентом
- Реализовать смену статуса через простой `<select>` + кнопку "Сохранить", либо через `USelect` (который уже используется в `admin/orders/index.vue`)
- Проверить что `USelect` из `~/components/U/USelect.vue` существует и поддерживает `v-model` + `options`

Минимальный фикс — заменить блок (строки ~184-205):
```vue
<!-- БЫЛО -->
<USelectMenu v-model="order.status" :options="statusOptions" ...>
  <template #default="{ open }">
    <UButton ...>{{ getStatusLabel(order.status) }}<UIcon :class="{ 'rotate-180': open }" /></UButton>
  </template>
</USelectMenu>

<!-- НАДО -->
<USelect
  v-model="order.status"
  :options="statusOptions"
  @update:model-value="updateStatus"
/>
```

### Что НЕЛЬЗЯ делать
- Нельзя использовать `USelectMenu` с scoped slot `#default="{ open }"` — он не работает в SSR с кастомными компонентами
- Нельзя оборачивать в `<ClientOnly>` — это скроет проблему, но сломает SEO и первый рендер
- Нельзя менять логику `updateStatus` — она корректна

### Граничные условия
- После фикса: `/admin/orders/{id}` открывается без 500
- Смена статуса работает: выбрал → сохранилось → toast → refresh
- При `pending=true` показывается skeleton, при `error` — кнопка retry

---

## 3. Работа с заказами в админке — фильтры, поиск, навигация, статусы, архивирование

### Текущее состояние (`admin/orders/index.vue`)

- Фильтр по статусу — есть, но не синхронизирован с URL при первой загрузке
- Фильтр по дате (`dateFilter`) — есть в URL, но **не передаётся в API** (не включён в `queryParams`)
- Поиск — **отсутствует**
- Глубокие ссылки — частично (page, status), но dateFilter теряется при refresh
- Архивирование — **отсутствует**
- Навигация к заказу — есть (клик по строке)
- Смена статуса из списка — есть через `updateStatus`, но вызывает `PATCH /admin/orders/{id}` вместо `PUT /admin/orders/{id}/status`

### Что НАДО сделать

#### backend-agent:
- Проверить эндпоинт `GET /api/v1/admin/orders`:
  - Добавить query param `search` — поиск по `order_id` (partial), `user_email`, `user_phone`, `tracking_number`
  - Добавить query param `date` — фильтр: `today`, `week`, `month`, `all` (конвертировать в `created_at >= X`)
  - Убедиться что `status` фильтр работает корректно
  - Ответ должен содержать `{ items: [...], total: int, page: int, per_page: int }`
- Проверить эндпоинт `PUT /api/v1/admin/orders/{id}/status`:
  - Принимает `{ new_status: string }`
  - Валидирует что статус из допустимого списка
  - Возвращает обновлённый заказ
- Добавить эндпоинт `POST /api/v1/admin/orders/{id}/archive`:
  - Устанавливает `is_archived = true` на заказе
  - Архивированные заказы не показываются в основном списке (если не передан `?include_archived=true`)
  - Возвращает 200 с обновлённым заказом

#### frontend-agent:
- `admin/orders/index.vue`:
  - Добавить поле поиска (debounce 400ms) — передавать в API как `search`
  - Исправить `queryParams` — добавить `date: dateFilter.value` если не `'all'`
  - Исправить инициализацию: `statusFilter` и `dateFilter` читать из `route.query` при монтировании (уже есть, проверить что работает)
  - Добавить кнопку "Архивировать" в действиях строки (с confirm dialog)
  - Добавить toggle "Показать архивные" (передаёт `include_archived=true` в API)
  - Исправить вызов смены статуса: использовать `PUT /admin/orders/{id}/status` с `{ new_status }`, не `PATCH /admin/orders/{id}`
  - Отображать `total` — "Показано X из Y заказов"

- `admin/orders/[id].vue`:
  - Исправить 500 (см. п.2)
  - Добавить кнопку "Архивировать заказ" в header actions (с confirm)
  - Кнопка "Назад" (`/admin/orders`) — уже есть, оставить

### Что НЕЛЬЗЯ делать
- Нельзя удалять заказы — только архивировать
- Нельзя менять статус на произвольную строку — только из фиксированного списка: `pending`, `awaiting_payment`, `paid`, `shipped`, `delivered`, `cancelled`
- Нельзя сбрасывать фильтры при навигации назад — URL должен сохранять состояние
- Нельзя делать бесконечный скролл — только пагинация
- Нельзя использовать `USelectMenu` с scoped slot `#default` — только `USelect`

### Граничные условия
- Поиск по пустой строке = нет фильтра (не передавать `search=` в API)
- Фильтр `date=all` = не передавать параметр в API
- Архивированный заказ исчезает из списка сразу после архивирования (optimistic update или refresh)
- При смене статуса на `cancelled` — показать дополнительный confirm: "Вы уверены? Это действие нельзя отменить"
- Пагинация сбрасывается на страницу 1 при изменении любого фильтра

---

## Порядок выполнения

```
1. frontend-agent: фикс 500 на /admin/orders/[id] (замена USelectMenu → USelect)
2. frontend-agent: фикс дублирования страницы логина (layout audit)
3. backend-agent: расширение GET /admin/orders (search, date filter, total)
4. backend-agent: POST /admin/orders/{id}/archive
5. frontend-agent: доработка admin/orders/index.vue (поиск, дата, архив, total)
6. frontend-agent: кнопка архивирования на /admin/orders/[id]
```

---

## Критерии приёмки

- [ ] `/admin/orders/{id}` открывается без 500 на prod
- [ ] Страница логина рендерится ровно один раз
- [ ] Поиск по заказам работает (email, телефон, трек-номер, ID)
- [ ] Фильтр по дате передаётся в API и работает
- [ ] URL сохраняет все фильтры (page, status, date, search)
- [ ] Заказ можно архивировать из списка и из детальной страницы
- [ ] Смена статуса работает через правильный эндпоинт
- [ ] Отображается общее количество заказов
