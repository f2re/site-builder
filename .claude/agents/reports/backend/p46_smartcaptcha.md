## Status: DONE

## Completed:
- Заменён `TURNSTILE_SECRET_KEY` на `SMARTCAPTCHA_SECRET_KEY` в `backend/app/core/config.py`
- Заменено поле `turnstile_token` на `captcha_token` в `ContactFormRequest` (`schemas.py`)
- Заменён метод `verify_turnstile` на `verify_captcha` в `ContactService` (`service.py`)
  - Новый URL: `https://smartcaptcha.yandexcloud.net/validate`
  - Параметры запроса: `secret`, `token`, `ip`
  - Проверка ответа: `result.get("status") == "ok"`
- Обновлён вызов в `submit_contact`: `data.captcha_token`, сообщение об ошибке обновлено

## Artifacts:
- `backend/app/core/config.py` — `SMARTCAPTCHA_SECRET_KEY: str = ""`
- `backend/app/api/v1/contact/schemas.py` — `captcha_token: str` в `ContactFormRequest`
- `backend/app/api/v1/contact/service.py` — метод `verify_captcha`

## Инструкция по получению ключей Яндекс SmartCaptcha:

1. Перейти на https://console.yandex.cloud
2. Выбрать сервис SmartCaptcha
3. Нажать "Создать капчу", заполнить параметры (домены сайта и т.п.)
4. После создания капчи будут доступны два ключа:
   - **Client key** (публичный) — для фронтенда (Nuxt)
   - **Server key** (секретный) — для бэкенда

5. Добавить в `.env` бэкенда:
   ```
   SMARTCAPTCHA_SECRET_KEY=<server_key>
   ```

6. Добавить в `.env` фронтенда (или `frontend/.env`):
   ```
   NUXT_PUBLIC_SMARTCAPTCHA_SITE_KEY=<client_key>
   ```

Примечание: если `SMARTCAPTCHA_SECRET_KEY` пустой, верификация пропускается (dev-режим).

## Contracts Verified:
- Pydantic schemas: OK
- DI via Depends: OK
- ruff: OK
- mypy: OK

## Next:
- frontend-agent: обновить виджет SmartCaptcha — заменить Cloudflare Turnstile на Яндекс SmartCaptcha
  - Поле формы: `captcha_token` (вместо `turnstile_token`)
  - Ключ окружения: `NUXT_PUBLIC_SMARTCAPTCHA_SITE_KEY`
  - Документация виджета: https://yandex.cloud/ru/docs/smartcaptcha/quickstart

## Blockers:
- none
