## Status: DONE

## Completed:
- Updated `frontend/components/AppFooter.vue`: added "Обратная связь" → /contact to "Информация" section; replaced /privacy with full set of legal links in "Поддержка" section (Гарантийные обязательства, Доставка, Политика конфиденциальности, Условия соглашения)
- Updated `frontend/components/AppHeader.vue`: added "Контакты" → /contact to navLinks (renders in both desktop nav and mobile menu drawer)
- Created `frontend/pages/dostavka.vue` — stub page
- Created `frontend/pages/garantiynye-obyazatelstva.vue` — stub page
- Created `frontend/pages/politika-konfidentsialnosti.vue` — stub page
- Created `frontend/pages/usloviya-soglasheniya.vue` — stub page
- Created `frontend/pages/contact.vue` — stub page (required since /contact is now linked from header)

## Artifacts:
- frontend/components/AppFooter.vue
- frontend/components/AppHeader.vue
- frontend/pages/dostavka.vue
- frontend/pages/garantiynye-obyazatelstva.vue
- frontend/pages/politika-konfidentsialnosti.vue
- frontend/pages/usloviya-soglasheniya.vue
- frontend/pages/contact.vue

## Contracts Verified:
- All links use NuxtLink: OK
- Only var(--color-*) tokens used in stub pages: OK
- Footer link styles unchanged (only footerLinks array modified): OK
- Header navLinks parity between desktop and mobile menu: OK (both use same navLinks array)
- npm run lint: OK (exit 0)
- npm run typecheck: OK (exit 0)

## Accessibility:
- Stub pages use semantic `<main>` and `<h1>` elements
- Link contrast via var(--color-text-2) → var(--color-accent) on hover matches existing footer link pattern

## Next:
- Content team: replace placeholder text in stub pages with actual legal/info content
- testing-agent: e2e smoke tests for footer links and stub pages

## Blockers:
- none
