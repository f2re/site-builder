## Status: DONE

## Completed:
- Проблема 1 (SmartCaptcha): убран `useHead({ script: [...] })` из корня `<script setup>`. Загрузка скрипта SmartCaptcha перенесена в `onMounted` через `document.createElement('script')`. Скрипт добавляется в `<head>` динамически только на клиенте, после чего вызывается `initSmartCaptcha()` через `script.onload`. Это устраняет проблему SSR, где `window.smartCaptcha` недоступен.
- Проблема 2 (текст настроек): URL `${apiBase}/contact/settings` в `useContact.ts` корректен. В `contact.vue` добавлен `data-testid="contact-greeting-text"` на блок отображения. `v-if="settings.contact_page_text"` правильно проверяет наличие текста.
- Проблема 3 (layout на десктопе): добавлен враппер `.contact-main` вокруг `.contact-greeting` и `.contact-card`. Grid `.contact-layout` теперь имеет два прямых дочерних элемента: `.contact-main` (левая колонка, flex column) и `aside.contact-info` (правая колонка, sticky). Sidebar больше не зависит от наличия greeting — всегда отображается справа на десктопе.

## Artifacts:
- /Users/meteo/Documents/WWW/site-builder/frontend/pages/contact.vue

## Contracts Verified:
- Только var(--color-*) токены: OK — hardcoded значений нет
- data-testid добавлен на greeting-text: OK
- npm run lint: OK (vue-tsc --noEmit, 0 errors)
- npm run typecheck: OK (vue-tsc --noEmit, 0 errors)

## Changes Summary:

### SmartCaptcha (Проблема 1)
Было: `if (config.public.smartCaptchaSiteKey) { useHead({ script: [...] }) }` в корне setup — выполняется на SSR.
Стало: в `onMounted` — `document.createElement('script')` с `script.onload = () => initSmartCaptcha()`.

### Layout (Проблема 3)
Было: `.contact-layout` — grid с 3 прямыми дочерними элементами (greeting, card, aside). При скрытом greeting `grid-row: 2` у sidebar ломал layout.
Стало: `.contact-layout` — grid с 2 прямыми дочерними элементами: `.contact-main` (flex column: greeting + card) и `aside.contact-info` (sticky). Grid всегда `1fr 320px` на десктопе.

### CSS новые классы:
- `.contact-main` — flex column, gap 24px, min-width 0
- `.contact-info` — position sticky top 100px (сбрасывается на < 1024px)

## Next:
- testing-agent: e2e тесты для /contact (форма, captcha dev mode, greeting text)

## Blockers:
- none
