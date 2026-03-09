## Status: DONE

## Completed:
- Добавлен пункт "Устройства" (`ph:cpu-bold`, `/admin/devices`) в `navItems` в `frontend/layouts/admin.vue` перед пунктом "Миграция"
- Создана страница `frontend/pages/admin/devices/index.vue` с полной функциональностью
- Добавлены типы `AdminDeviceRead` и методы `adminGetUserDevices`, `adminGetDevices`, `adminPatchDevice`, `adminDeleteDevice` в `frontend/composables/useUser.ts`
- Исправлена вкладка "Устройства" в `frontend/pages/admin/users/[id].vue` — теперь загружает данные через `GET /admin/users/{id}/devices` с типом `AdminDeviceRead`

## Artifacts:
- `/Users/meteo/Documents/WWW/site-builder/frontend/layouts/admin.vue` — добавлен пункт навигации
- `/Users/meteo/Documents/WWW/site-builder/frontend/pages/admin/devices/index.vue` — новая страница
- `/Users/meteo/Documents/WWW/site-builder/frontend/composables/useUser.ts` — новые типы и методы
- `/Users/meteo/Documents/WWW/site-builder/frontend/pages/admin/users/[id].vue` — исправлена вкладка Devices

## Страница /admin/devices реализует:
- Таблица с 8 колонками: device_uid, name, model, пользователь (ссылка на /admin/users/{user_id}), статус (badge), зарегистрировано, активность, комментарий
- Поиск с debounce 400ms через параметр `search`
- Фильтр is_active: Все / Активные / Неактивные
- Кнопка "Сбросить фильтры"
- PATCH toggle is_active без перезагрузки страницы (optimistic UI через refresh)
- DELETE с диалогом подтверждения через `useConfirm()`
- Пагинация Prev/Next с отображением "Страница X из Y" (per_page=50)
- Состояния: skeleton при загрузке, сообщение об ошибке, empty state
- Индикатор загрузки per-device при PATCH/DELETE операциях
- Mobile-friendly: скрытые колонки на мобильных, мета-информация в первой колонке
- Только `var(--color-*)` токены — без хардкодных цветов

## Вкладка Devices в /admin/users/[id].vue:
- Загружает данные через `GET /admin/users/{id}/devices` (отдельный endpoint)
- Отображает: device_uid, name, model, is_active, registered_at
- Тип `AdminDeviceRead` соответствует API-ответу
- Автоматически обновляется при переключении на вкладку

## Contracts Verified:
- API shape matches api_contracts.md: OK (AdminDeviceRead соответствует ответу endpoint)
- data-testid на всех интерактивных элементах: OK
- Только var(--color-*) токены: OK
- Mobile-first breakpoints: OK
- npm run lint (vue-tsc --noEmit): OK — 0 ошибок
- npm run typecheck (vue-tsc --noEmit): OK — 0 ошибок

## Next:
- testing-agent: e2e тесты для /admin/devices (поиск, фильтрация, toggle, delete)

## Blockers:
- none
