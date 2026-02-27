---
id: BE-05
status: TODO
agent: backend-agent
stage: 6 (Уведомления)
priority: MEDIUM
depends_on: [BE-03]
blocks: []
---

# BE-05 — Уведомления (Email, Telegram, In-App WebSocket)

## Цель

Реализовать систему уведомлений: Event → Celery chord → параллельная рассылка по каналам.

## ⚠️ Перед началом

```bash
read_file backend/app/db/models/notification.py  # уже есть
list_directory backend/app/tasks/
read_file backend/app/core/config.py  # проверить MAIL_*, TELEGRAM_* vars
```

## Задачи

### 1. Добавить в requirements.txt (если не добавлены)

```
fastapi-mail==1.4.1
jinja2==3.1.3
premailer==3.10.0
aiogram==3.9.0
```

### 2. Email-шаблоны (`backend/app/templates/email/`)

Создать директорию и базовые шаблоны:
```
base.html              # layout + inline CSS (premailer)
order_created.html
order_paid.html
order_shipped.html     # включает трек-номер СДЭК
order_delivered.html
order_cancelled.html
welcome.html
password_reset.html
comment_approved.html
```

Все шаблоны наследуют `base.html`. Стили инлайнятся через `premailer` (Gmail-совместимость).

### 3. Celery dispatcher (`backend/app/tasks/notifications.py`)

Проверить наличие, создать/дополнить:

```python
@celery_app.task(name="tasks.notify_order_status_changed", bind=True, max_retries=3)
def notify_order_status_changed(self, order_id: int, new_status: str, user_id: int):
    chord(
        send_email_notification.s(order_id, new_status, user_id),
        send_telegram_notification.s(order_id, new_status, user_id),
        send_inapp_notification.s(order_id, new_status, user_id),
    )(log_notification_result.s(order_id=order_id))
```

### 4. In-App модель — проверить `notification.py`

Должны быть поля:
```python
id: int, user_id: int, title: str, body: str
link: str | None   # /orders/{id}
is_read: bool = False
created_at: datetime
```

API:
```
GET    /api/v1/notifications          (current_user)
PATCH  /api/v1/notifications/{id}/read
DELETE /api/v1/notifications/read-all
```

Real-time push через WebSocket `/ws/notifications/{user_id}` — переиспользует ConnectionManager из BE-04.

### 5. Telegram (aiogram 3)

`backend/app/integrations/telegram.py`:
```python
async def send_order_notification(chat_id: str, order_id: int, status: str) -> None:
    # Использовать Bot(token=settings.TELEGRAM_BOT_TOKEN)
    # Если TELEGRAM_BOT_TOKEN не задан — пропускать без ошибки (заглушка)
```

## Контракты

- Email: НИКОГДА не логировать `author_email` (152-ФЗ)
- SMS-канал (`smsc.ru`) — реализовывать как заглушку, `SMSC_LOGIN` не заполнять
- Если внешний канал недоступен — `tenacity` retry × 3, потом log и продолжить
- `password_reset` email: токен TTL 1 час, одноразовый

## Критерии готовности

- [ ] Order PAID → email отправляется через Celery
- [ ] Telegram отправляется если токен задан, пропускается если нет
- [ ] In-app уведомление создаётся в БД + WebSocket push
- [ ] `is_read` обновляется через PATCH эндпоинт
- [ ] Никаких персданных в логах structlog

## Отчёт

`.gemini/agents/reports/backend/BE-05.md`
