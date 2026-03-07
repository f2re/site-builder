## Status: DONE

## Completed:
- BlogCarousel.vue: заменён `<NuxtImg>` на `<img>` — IPX обходится полностью, изображения загружаются напрямую с /media/blog/...
- blog/[slug].vue: одиночная обложка (singleCover) также переведена с `<NuxtImg>` на `<img>` по той же причине
- blog/[slug].vue: секция share buttons обёрнута в `<ClientOnly>` — pageUrl теперь вычисляется только на клиенте, ссылки Telegram/VK содержат корректный URL

## Artifacts:
- frontend/components/blog/BlogCarousel.vue
- frontend/pages/blog/[slug].vue

## Contracts Verified:
- API shape matches api_contracts.md: N/A (только UI-фикс)
- npm run lint: OK (завершается без ошибок)
- npm run typecheck: OK (vue-tsc --noEmit, завершается без ошибок)
- Только var(--color-*) токены: OK (новые изменения не добавляют хардкода)
- data-testid сохранены на всех элементах share: OK

## Root Cause Analysis:
1. КАРУСЕЛЬ: `<NuxtImg>` передаёт src в IPX-обработчик (`/_ipx/fit_cover&s_800x450/...`). IPX пытается найти файл локально в `public/`, но изображения хранятся на медиасервере по пути `/media/blog/...` и доступны через devProxy. IPX не имеет доступа к этим файлам — отсюда IPX_FILE_NOT_FOUND 404. Решение: обычный `<img>` обращается напрямую через devProxy к медиасерверу.
2. SHARE BUTTONS: `pageUrl` вычисляется через `import.meta.client ? window.location.href : ''`. При SSR значение пустое, и ссылки рендерятся с `href=""`. `<ClientOnly>` гарантирует, что компонент рендерится только в браузере, где `window.location.href` доступен.

## Next:
- testing-agent: e2e тесты — проверить отображение изображений в карусели и клик по кнопкам шаринга

## Blockers:
- none
