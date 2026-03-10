## Status: DONE

## Completed:
- Удалена строка 'Блог / Категории' из навигации админки
- Переименован пункт 'Блог / Посты' в 'Блог'
- Страница /admin/blog/categories.vue остается доступной по прямому URL

## Artifacts:
- /Users/meteo/Documents/WWW/site-builder/frontend/layouts/admin.vue

## Changes Made:
В файле `frontend/layouts/admin.vue` (строки 8-20):
- Удален элемент массива `{ label: 'Блог / Категории', icon: 'ph:tag-bold', to: '/admin/blog/categories' }`
- Изменен label с `'Блог / Посты'` на `'Блог'` для элемента с `to: '/admin/blog'`

## Contracts Verified:
- data-testid на всех элементах: ✅ (используется `data-testid="admin-nav-item"`)
- Только var(--color-*) токены: ✅ (без изменений в стилях)
- Mobile-first breakpoints: ✅ (без изменений в стилях)
- npm run lint: ✅ (vue-tsc --noEmit прошел без ошибок)
- npm run typecheck: ✅ (прошел без ошибок)

## Accessibility:
- Без изменений (только текст навигации)

## Performance:
- Без изменений (удален один элемент массива)

## Next:
- Страница /admin/blog/categories доступна для прямого использования
- Категории блога управляются через форму поста или прямой URL

## Blockers:
- none
