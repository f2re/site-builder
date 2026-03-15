## Status: DONE

## Completed:
- Заменена Cloudflare Turnstile на Яндекс SmartCaptcha во всех затронутых файлах
- `nuxt.config.ts`: переменная `turnstileSiteKey` переименована в `smartCaptchaSiteKey`, env-переменная `NUXT_PUBLIC_TURNSTILE_SITE_KEY` заменена на `NUXT_PUBLIC_SMARTCAPTCHA_SITE_KEY`
- `composables/useContact.ts`: поле `turnstile_token` переименовано в `captcha_token` в интерфейсе `ContactFormData`
- `pages/contact.vue`: полностью заменена логика Turnstile на SmartCaptcha — новый скрипт, инициализация виджета через `window.smartCaptcha.render()`, сброс через `window.smartCaptcha.reset()`, CSS-классы переименованы (`.turnstile-wrapper` → `.captcha-wrapper`, `.turnstile-dev-note` → `.captcha-dev-note`), поле payload переименовано в `captcha_token`, сообщение об ошибке 422 обновлено

## Artifacts:
- /Users/meteo/Documents/WWW/site-builder/frontend/nuxt.config.ts
- /Users/meteo/Documents/WWW/site-builder/frontend/composables/useContact.ts
- /Users/meteo/Documents/WWW/site-builder/frontend/pages/contact.vue

## Contracts Verified:
- Только var(--color-*) токены в .vue файлах: OK
- data-testid="contact-captcha" сохранён на обёртке виджета: OK
- API поле captcha_token совпадает с useContact.ts ContactFormData: OK
- npm run lint (vue-tsc --noEmit): OK (нет ошибок)
- npm run typecheck (vue-tsc --noEmit): OK (нет ошибок)

## Next:
- backend-agent: переименовать поле `turnstile_token` → `captcha_token` в схеме ContactFormCreate и заменить верификацию Turnstile на Яндекс SmartCaptcha API (POST https://smartcaptcha.yandexcloud.net/waf/v1/validate)
- testing-agent: обновить e2e-тесты для `data-testid="contact-captcha"` (новый id виджета `smartcaptcha-widget`)

## Blockers:
- none
