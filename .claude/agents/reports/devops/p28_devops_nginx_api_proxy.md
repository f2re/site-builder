## Status: DONE

## Completed:
- Исправлен `.env.example` строка 105: добавлен суффикс `/api/v1` к `NUXT_PUBLIC_API_BASE`
- Добавлен обязательный комментарий выше переменной: пример для продакшена (`https://m.wifiobd.ru/api/v1`)
- Проверен `deploy/nginx/nginx.conf`: блок `location /api/` корректно проксирует на `http://backend` (upstream backend:8000) — изменений не потребовалось
- Проверен `deploy/docker-compose.prod.yml`: frontend читает env из `env_file: /srv/site-builder/.env.prod` — переменная подхватывается оттуда, изменений не потребовалось
- Проверен `frontend/nuxt.config.ts`: fallback уже корректный — `http://localhost:8000/api/v1` — изменений не потребовалось

## Root Cause Analysis:
Если на сервере в `/srv/site-builder/.env.prod` была установлена переменная `NUXT_PUBLIC_API_BASE=https://m.wifiobd.ru` (без `/api/v1`), то все API-запросы из nuxt.config.ts `runtimeConfig.public.apiBase` указывали на корень сайта, а не на API. Nginx не мог проксировать `/blog/posts` на backend — он проксирует только `/api/` префикс.

## Artifacts:
- `.env.example` — исправлена строка 105, добавлен комментарий

## Files Verified (no changes needed):
- `deploy/nginx/nginx.conf` — `location /api/` proxy_pass http://backend — OK
- `deploy/docker-compose.prod.yml` — frontend env_file из .env.prod — OK
- `frontend/nuxt.config.ts` — fallback `http://localhost:8000/api/v1` — OK

## Nginx Contract Verified:
- `location /api/` → proxy_pass `http://backend` (upstream backend:8000): OK
- `location /api/v1/auth/` → rate limit zone=auth: OK
- `location /ws/` → WebSocket upgrade headers: OK
- HTTPS redirect (301): OK
- Security headers (HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy): OK
- Gzip enabled: OK

## Action Required on Production Server:
В файле `/srv/site-builder/.env.prod` на сервере НЕОБХОДИМО проверить и установить:
```
NUXT_PUBLIC_API_BASE=https://m.wifiobd.ru/api/v1
```
Без этого изменения на сервере проблема DNS-ошибки сохранится. После редактирования — перезапустить frontend контейнер:
```bash
docker compose -f /srv/site-builder/deploy/docker-compose.prod.yml up -d frontend
```

## Contracts Verified:
- docker compose config dev: не выполнено (docker compose plugin недоступен в среде агента)
- docker compose config prod: не выполнено (docker compose plugin недоступен в среде агента)
- hadolint: не применимо (Dockerfile не изменялись)
- nginx.conf синтаксис: проверен вручную, структура корректна

## Next:
- Пользователь должен обновить `/srv/site-builder/.env.prod` на продакшн-сервере
- После обновления .env.prod — перезапустить frontend контейнер

## Blockers:
- none (docker compose config не выполнен из-за ограничений среды — не критично, т.к. compose-файлы не изменялись)
