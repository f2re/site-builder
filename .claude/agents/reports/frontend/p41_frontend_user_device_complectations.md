## Status: DONE

## Completed:
- Добавлен интерфейс `ComplectationItem` в `composables/useIoT.ts`
- Добавлено поле `complectations?: ComplectationItem[]` к интерфейсу `IoTDevice`
- Добавлена функция `fetchAllComplectations()` в `useIoT` — GET `/users/complectations` (auth required)
- Исправлен существующий баг: `token` → `accessToken` в `useIoT.ts` (поле из `useAuth` называется `accessToken`, а не `token`)
- В `pages/profile/devices/[id].vue`:
  - Загрузка всех комплектаций через `fetchAllComplectations()` при монтировании
  - Секция "Комплектации устройства" под основным контентом с иконкой `ph:puzzle-piece-bold`
  - Активные карточки: `border: 2px solid var(--color-accent)`, background акцентный, иконка `ph:check-circle-bold`
  - Неактивные карточки: `border: 1px dashed var(--color-border)`, opacity 0.6, иконка `ph:lock-bold`, ссылка "Подключить"
  - Skeleton-лоадеры во время загрузки
  - `data-testid="device-complectations-section"` на секции
  - `data-testid="device-complectation-{code}"` на каждой карточке
  - `TransitionGroup name="complect-list"` с анимацией появления
  - Stagger-анимация через CSS custom property `--card-index`
  - Убраны хардкоженные цвета (#000, #1a1a1a, #00ff41, #888, #eee) из terminal-card — заменены на var(--color-*)
  - Сетка: 3 колонки на десктопе, 2 на планшете (max-width: 1024px), 1 на мобиле (max-width: 480px)
  - Fallback: если `/users/complectations` недоступен — показываются только `device.complectations`
  - Кнопка "Подключить" ведёт на `/shop?complectation={code}`

## Artifacts:
- `frontend/composables/useIoT.ts`
- `frontend/pages/profile/devices/[id].vue`

## Contracts Verified:
- API GET `/users/complectations` → `ComplectationItem[]` — соответствует задаче
- `IoTDevice.complectations` из `DeviceResponse` — поле добавлено в тип
- data-testid на всех элементах: OK
- Только var(--color-*) токены: OK (удалены хардкод-цвета из terminal-card)
- Mobile-first breakpoints: OK (480px, 1024px)
- npm run lint: OK (0 ошибок)
- npm run typecheck: OK (0 ошибок)

## Accessibility:
- aria-label на каждой карточке комплектации (указывает имя и статус активации)
- aria-hidden на иконках (декоративные)
- focus-visible наследуется из tokens.css

## Next:
- testing-agent: e2e тесты для страницы `/profile/devices/{id}` — проверить `data-testid="device-complectations-section"`, активные/неактивные карточки

## Blockers:
- none
