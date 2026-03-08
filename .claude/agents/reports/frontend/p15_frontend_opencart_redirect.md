## Status: DONE

## Completed:
- Создан `frontend/middleware/opencart-redirect.global.ts` — глобальный Nuxt 3 middleware
- Middleware перехватывает URL вида `/index.php?route=...` (проверка `to.path.startsWith('/index.php')`)
- Вызывает `GET /api/v1/redirects/lookup?old_path=<encoded>` через `$fetch` с `baseURL: apiBase`
- При ответе 200 и `is_active === true` делает `navigateTo(new_path, { redirectCode: 301|302 })`
- При 404 — пропускает навигацию без ошибки
- При сетевой/5xx ошибке — `console.warn` и пропускает навигацию
- Аналогичная логика в middleware/ и plugins/ отсутствовала — дублирования нет
- TypeScript strict: интерфейс `RedirectRecord`, нет `any`, обработка `unknown` через type narrowing

## Artifacts:
- /Users/meteo/Documents/WWW/site-builder/frontend/middleware/opencart-redirect.global.ts

## Contracts Verified:
- API shape matches api_contracts.md: OK (endpoint `/redirects/lookup` использует `apiBase` из `runtimeConfig.public`)
- `useRuntimeConfig().public.apiBase` — без хардкода URL: OK
- TypeScript strict, no `any`: OK
- npm run lint (vue-tsc --noEmit): OK (0 errors)
- npm run typecheck (vue-tsc --noEmit): OK (0 errors)

## API Contract Note:
Endpoint `GET /api/v1/redirects/lookup?old_path=...` не задокументирован в `api_contracts.md` v2.0.
Backend-agent добавил его как часть задачи `p15_backend_redirect_fix`. Интерфейс ответа:
```typescript
interface RedirectRecord {
  id: string
  old_path: string
  new_path: string
  redirect_code: number  // 301 | 302
  is_active: boolean
}
```

## Next:
- testing-agent: e2e тесты для OpenCart redirect middleware
  - тест: `/index.php?route=product/category&path=61_67` → 301 на `/catalog/<slug>`
  - тест: `/index.php?route=product/product&product_id=123` → 301 на `/shop/<slug>`
  - тест: неизвестный OpenCart URL → навигация проходит без краша
  - тест: обычный URL (не `/index.php`) → middleware не вызывает API

## Blockers:
- none
