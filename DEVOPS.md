# DEVOPS — Production Deployment Guide

> Актуально для стека: GitLab CI/CD · Docker Compose · Apache 2 · Ubuntu 18.04+

---

## Оглавление

1. [Требования к серверу](#1-требования-к-серверу)
2. [Первоначальная настройка сервера](#2-первоначальная-настройка-сервера)
3. [GitLab CI/CD — переменные](#3-gitlab-cicd--переменные)
4. [SSH-ключ для деплоя](#4-ssh-ключ-для-деплоя)
5. [Файл .env.prod на сервере](#5-файл-envprod-на-сервере)
6. [MeiliSearch — search-only ключ](#6-meilisearch--search-only-ключ)
7. [Apache — настройка reverse proxy](#7-apache--настройка-reverse-proxy)
8. [SSL-сертификат Let's Encrypt](#8-ssl-сертификат-lets-encrypt)
9. [Первый запуск](#9-первый-запуск)
10. [Схема маршрутизации URL](#10-схема-маршрутизации-url)
11. [Управление контейнерами](#11-управление-контейнерами)
12. [Обновление через пайплайн](#12-обновление-через-пайплайн)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Требования к серверу

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| CPU | 2 vCPU | 4 vCPU |
| RAM | 2 GB | 4 GB |
| Диск | 20 GB | 40 GB SSD |
| ОС | Ubuntu 18.04 | Ubuntu 22.04 |
| Docker | 24+ | latest |
| Docker Compose | v2 | latest |
| Apache | 2.4 | 2.4 |

```bash
# Установить Docker (если не установлен)
curl -fsSL https://get.docker.com | sh

# Установить Apache и модули
apt install apache2 -y
a2enmod proxy proxy_http proxy_wstunnel ssl rewrite headers
systemctl enable apache2
```

---

## 2. Первоначальная настройка сервера

```bash
# Создать директории проекта
mkdir -p /srv/site-builder/data/{postgres,redis,meilisearch}
mkdir -p /srv/site-builder/deploy

# Права для Docker-контейнеров
chown -R 999:999 /srv/site-builder/data/postgres
chown -R 999:999 /srv/site-builder/data/redis
chown -R 1000:1000 /srv/site-builder/data/meilisearch

# Webroot для Let's Encrypt
mkdir -p /var/www/letsencrypt/.well-known/acme-challenge
```

---

## 3. GitLab CI/CD — переменные

Перейти: **GitLab → Project → Settings → CI/CD → Variables**

| Переменная | Тип | Описание |
|------------|-----|----------|
| `SSH_PRIVATE_KEY` | **File** | Приватный SSH-ключ для деплоя (см. раздел 4) |
| `STAGING_HOST` | Variable | IP или hostname staging-сервера |
| `PROD_HOST` | Variable | IP или hostname prod-сервера |
| `DEPLOY_USER` | Variable | Пользователь SSH на сервере (например `root`) |
| `DEPLOY_TOKEN_USER` | Variable (masked) | Username GitLab Deploy Token |
| `DEPLOY_TOKEN_PASS` | Variable (masked) | Password GitLab Deploy Token |

### Создать Deploy Token

**GitLab → Project → Settings → Repository → Deploy tokens**

```
Name:   ci-registry-deploy
Scopes: ✅ read_registry
        ✅ write_registry  (нужен для push образов из build-джобов)
```

> ⚠️ Токен показывается только один раз — сразу скопировать в переменные CI/CD.

---

## 4. SSH-ключ для деплоя

```bash
# Сгенерировать ключ (ed25519 — обязательно, OpenSSH >= 8.7)
ssh-keygen -t ed25519 -C "gitlab-ci-deploy" -f ~/.ssh/gitlab_deploy -N ""

# Добавить публичный ключ на сервер
cat ~/.ssh/gitlab_deploy.pub >> /root/.ssh/authorized_keys
# (или для другого пользователя: /home/DEPLOY_USER/.ssh/authorized_keys)

# Добавить приватный ключ в GitLab CI/CD Variables:
# Тип: File, Имя: SSH_PRIVATE_KEY
cat ~/.ssh/gitlab_deploy
```

> ⚠️ Важно: при вставке в GitLab убедиться, что после последней строки
> `-----END OPENSSH PRIVATE KEY-----` есть **пустая строка** (Enter).
> Без неё возникает ошибка `error in libcrypto`.

---

## 5. Файл .env.prod на сервере

```bash
# Скопировать шаблон
cp deploy/.env.prod.example /srv/site-builder/.env.prod

# Заполнить реальными значениями
nano /srv/site-builder/.env.prod

# Защитить от чтения
chmod 600 /srv/site-builder/.env.prod
```

См. полный список переменных в [`deploy/.env.prod.example`](deploy/.env.prod.example).

> ⚠️ **Ключевая особенность Docker Compose:**
> `env_file:` в compose-файле загружает переменные внутрь контейнера,
> но `${VAR}` в самом YAML подставляются только через флаг `--env-file`.
> Скрипт `deploy.sh` передаёт его автоматически.

---

## 6. MeiliSearch — search-only ключ

Мастер-ключ нельзя выставлять в браузер. Создать ограниченный ключ:

```bash
# Создать search-only ключ
curl -s -X POST http://localhost:7700/keys \
  -H "Authorization: Bearer ВАШ_MEILI_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Frontend search key",
    "actions": ["search"],
    "indexes": ["*"],
    "expiresAt": null
  }' | python3 -m json.tool

# Скопировать поле "key" из ответа
# Вставить в .env.prod как NUXT_PUBLIC_MEILI_API_KEY
```

---

## 7. Apache — настройка reverse proxy

Готовый конфиг: [`deploy/apache/m.wifiobd.ru.conf`](deploy/apache/m.wifiobd.ru.conf)

```bash
# Скопировать конфиг
cp deploy/apache/m.wifiobd.ru.conf /etc/apache2/sites-available/

# Включить (сначала только HTTP — до получения SSL):
# В файле закомментировать блок <VirtualHost *:443> до получения сертификата
a2ensite m.wifiobd.ru.conf
apache2ctl configtest && systemctl reload apache2
```

---

## 8. SSL-сертификат Let's Encrypt

```bash
# Убедиться что DNS m.wifiobd.ru → IP этого сервера
dig +short m.wifiobd.ru

# Проверить доступность ACME endpoint:
echo "ok" > /var/www/letsencrypt/.well-known/acme-challenge/test.txt
curl -s http://m.wifiobd.ru/.well-known/acme-challenge/test.txt  # должно вернуть: ok
rm /var/www/letsencrypt/.well-known/acme-challenge/test.txt

# Получить сертификат
certbot certonly --webroot \
  -w /var/www/letsencrypt \
  -d m.wifiobd.ru \
  --email admin@wifiobd.ru \
  --agree-tos \
  --non-interactive

# После получения — раскомментировать блок <VirtualHost *:443> в конфиге Apache
apache2ctl configtest && systemctl reload apache2

# Автообновление (certbot cron уже настроен автоматически)
certbot renew --dry-run
```

---

## 9. Первый запуск

```bash
cd /srv/site-builder

# Подтянуть образы (нужно залогиниться вручную первый раз)
docker login registry.gitlab.wifiobd.ru -u DEPLOY_TOKEN_USER

# Запустить все сервисы
IMAGE_TAG=v1.0.0 \
CI_REGISTRY_IMAGE=registry.gitlab.wifiobd.ru/f2re/wifiobd2-site-modern \
docker compose -f deploy/docker-compose.prod.yml --env-file .env.prod up -d

# Проверить статус
watch -n 3 'docker compose -f deploy/docker-compose.prod.yml --env-file .env.prod ps'
```

Ожидаемый результат через ~60 секунд:

```
NAME             STATUS
sb_postgres      Up X seconds (healthy)
sb_redis         Up X seconds (healthy)
sb_meilisearch   Up X seconds (healthy)
sb_backend       Up X seconds (healthy)
sb_celery        Up X seconds
sb_frontend      Up X minutes (healthy)
```

---

## 10. Схема маршрутизации URL

```
Браузер пользователя
  │
  ├── https://m.wifiobd.ru/          → Apache → sb_frontend:3000   (Nuxt SSR)
  ├── https://m.wifiobd.ru/api/      → Apache → sb_backend:8000    (FastAPI)
  ├── https://m.wifiobd.ru/media/    → Apache → sb_backend:8000    (статика)
  ├── wss://m.wifiobd.ru/ws/         → Apache → sb_backend:8000    (WebSocket)
  └── https://m.wifiobd.ru/search/   → Apache → sb_meilisearch:7700 (поиск)

Nuxt SSR (сервер → Docker-сеть, без TLS)
  └── http://sb_backend:8000/api/v1  → контейнер sb_backend напрямую
```

### Переменные окружения Nuxt

| Переменная | Значение | Где используется |
|-----------|----------|------------------|
| `NUXT_PUBLIC_API_BASE` | `https://m.wifiobd.ru/api/v1` | Браузер + SSR |
| `NUXT_PUBLIC_SITE_URL` | `https://m.wifiobd.ru` | SEO, canonical |
| `NUXT_PUBLIC_WS_BASE` | `wss://m.wifiobd.ru/ws/` | WebSocket браузер |
| `NUXT_PUBLIC_MEILI_URL` | `https://m.wifiobd.ru/search` | MeiliSearch браузер |
| `NUXT_PUBLIC_MEILI_API_KEY` | search-only key | Поиск (не мастер!) |

---

## 11. Управление контейнерами

```bash
cd /srv/site-builder
DC="docker compose -f deploy/docker-compose.prod.yml --env-file .env.prod"

# Статус
$DC ps

# Логи (все)
$DC logs --tail=100 -f

# Логи конкретного сервиса
$DC logs --tail=50 -f backend
$DC logs --tail=50 -f frontend
$DC logs --tail=50 -f postgres

# Перезапуск одного сервиса
$DC restart backend

# Полная остановка
$DC down

# Полная остановка с удалением volumes (ОСТОРОЖНО — удалит данные!)
$DC down -v

# Healthcheck конкретного контейнера
docker inspect sb_redis | python3 -c "import sys,json; h=json.load(sys.stdin)[0]['State']['Health']; print(h['Status']); [print(l['Output']) for l in h['Log'][-3:]]"
```

---

## 12. Обновление через пайплайн

```bash
# Создать тег для деплоя
git tag v1.2.3
git push origin v1.2.3

# GitLab CI автоматически:
# 1. lint → test → build (автоматически)
# 2. deploy:staging → ручной запуск в GitLab UI
# 3. deploy:production → ручной запуск в GitLab UI
```

Пайплайн запускается **только при пуше тега** вида `v1.2.3`.

---

## 13. Troubleshooting

### `error in libcrypto` при ssh-add
```bash
# Проверить что ключ заканчивается переносом строки:
cat -A /path/to/key | tail -3  # последняя строка должна заканчиваться на $
# Исправить: открыть переменную в GitLab и добавить Enter в конце значения
```

### Docker login: `access forbidden`
```bash
# Проверить JWT endpoint:
curl -u "TOKEN_USER:TOKEN_PASS" "https://gitlab.wifiobd.ru/jwt/auth?service=container_registry&scope=repository:f2re/wifiobd2-site-modern/backend:pull"
# Ответ 200 = токен валидный, ответ 403 = нет scope read_registry
```

### Переменные пустые в docker-compose
```bash
# ВСЕГДА передавать --env-file при ручном запуске:
docker compose -f deploy/docker-compose.prod.yml --env-file /srv/site-builder/.env.prod ps
# БЕЗ --env-file переменные ${VAR} в YAML будут пустыми!
```

### `sb_redis is unhealthy`
```bash
docker logs sb_redis
# Если REDIS_PASSWORD пустой в .env.prod — дополнить файл и перезапустить:
docker compose -f deploy/docker-compose.prod.yml --env-file .env.prod up -d --force-recreate redis
```

### `stat /srv/site-builder/deploy/docker-compose.prod.yml: no such file or directory`
```bash
# deploy.sh копирует себя, но не compose-файл автоматически.
# Либо пайплайн копирует compose через scp (см. .gitlab-ci.yml),
# либо скопировать вручную:
cd /srv/site-builder
git clone https://gitlab.wifiobd.ru/f2re/wifiobd2-site-modern.git .
# или scp с машины разработки
```

### Apache reload failure: `SSLCertificateFile does not exist`
```bash
# Сначала получить сертификат, потом добавлять HTTPS VirtualHost в конфиг
# Временно держать только HTTP VirtualHost до выполнения certbot
```

### CORS: браузер обращается к `localhost:8000`
```bash
# Убедиться что в .env.prod заданы публичные URL:
grep NUXT_PUBLIC /srv/site-builder/.env.prod
# NUXT_PUBLIC_API_BASE должен быть https://m.wifiobd.ru/api/v1, НЕ localhost

# Перезапустить фронтенд после изменения .env.prod:
docker compose -f deploy/docker-compose.prod.yml --env-file .env.prod up -d --force-recreate frontend
```
