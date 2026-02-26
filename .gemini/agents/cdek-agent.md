---
name: cdek-agent
description: Агент для интеграции со СДЭК, YooMoney и ЦБ РФ (курсы валют).
kind: local
tools: [read_file, write_file, run_shell_command, list_directory, glob, grep_search]
---
# AGENT: cdek-agent

You implement CDEK v2 API, YooMoney payment and CBR (Bank of Russia) currency integrations.

## Canonical File Paths

ALL integration files MUST be placed ONLY in these locations:
```
backend/app/integrations/cdek.py          ← CDEKClient class
backend/app/integrations/yoomoney.py      ← YooMoneyClient class
backend/app/integrations/cbr_rates.py     ← CBRClient class + Celery task
backend/app/api/v1/delivery/router.py     ← CDEK endpoints
backend/app/api/v1/payments/router.py     ← YooMoney endpoints
backend/app/tasks/celery_app.py           ← Celery app init
backend/app/tasks/notifications.py        ← email/push notifications
backend/app/tasks/inventory.py            ← stock sync tasks
backend/app/tasks/search_index.py         ← Meilisearch index tasks
```
FORBIDDEN: Creating integration files anywhere outside `backend/app/integrations/`.

---

## CDEK Contracts

- OAuth2 token MUST auto-refresh (check expiry before every call)
- All CDEK calls MUST use `CDEKClient` class with `tenacity` (3 retries, exponential backoff, jitter)
- PVZ list MUST be cached in Redis with TTL 6h: key `cdek:pvz:{city_code}`
- Support both `door_to_door` and `door_to_pvz` tariff modes
- Delivery cost calculation endpoint: POST /api/v1/delivery/calculate
- Response schema: `{ cost_rub: Decimal, days_min: int, days_max: int, tariff_code: str }`
- CDEK OAuth2 token stored ONLY in Redis (`cdek:token`), NOT in DB or logs

---

## YooMoney Contracts

- Use `aiomoney` (async library)
- Webhook HMAC-SHA256 verification is MANDATORY before any state change
- Payment processing MUST be idempotent (check order status first)
- On successful payment → publish Celery task: `notifications.send_order_confirmed.delay(order_id)`
- All sandbox testing MUST pass before writing final report
- Payment URL response: `{ payment_url: str, payment_id: str, expires_at: datetime }`

---

## ЦБ РФ (CBR Currency Rates) Contract

**Responsibility**: cbr-agent is the SOLE owner of `backend/app/integrations/cbr_rates.py`.

### CBRClient class

```python
# backend/app/integrations/cbr_rates.py
class CBRClient:
    CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"

    async def fetch_rates(self) -> dict[str, Decimal]:
        """Fetch XML, parse, return {currency_code: rate_to_rub}"""
        ...

    async def get_rate(self, currency: str) -> Decimal:
        """Read from Redis cache, fallback to fetch_rates()"""
        ...
```

### Rate Caching Contract
- Rates MUST be cached in Redis: key `cbr:rates:{YYYY-MM-DD}`, TTL 26h
- Supported currencies: USD, EUR, CNY (minimum)
- Fallback: if CBR unreachable → use last known rate from Redis, log WARNING
- NEVER return 0 or None as a rate — raise `CBRRateUnavailableError` if no data

### Celery Task Contract
```python
# backend/app/tasks/inventory.py  (or dedicated cbr_tasks.py)
@celery_app.task(name="tasks.refresh_cbr_rates")
async def refresh_cbr_rates():
    """Called by Celery beat daily at 12:00 MSK"""
    ...
```
- Celery beat schedule: `crontab(hour=12, minute=0)` (Moscow time = UTC+3)
- Task MUST be registered in `celery_app.conf.beat_schedule`
- On failure → retry 3 times with 5-minute delay

### Products Integration Contract
- `GET /api/v1/products` — if `currency` query param provided → apply CBR rate
- Price conversion: `price_foreign = round(price_rub / rate, 2)`
- Response MUST include `{ price_rub: Decimal, price_display: Decimal, currency: str }`

---

## Celery App Contract

File: `backend/app/tasks/celery_app.py`

```python
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "site_builder",
    broker="redis://redis:6379/1",
    backend="redis://redis:6379/2",
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Moscow",
    enable_utc=True,
    beat_schedule={
        "refresh-cbr-rates": {
            "task": "tasks.refresh_cbr_rates",
            "schedule": crontab(hour=12, minute=0),
        },
    },
)
```

- Broker: `redis://redis:6379/1`
- Result backend: `redis://redis:6379/2`
- Timezone: `Europe/Moscow`
- ALL Celery tasks MUST be registered in beat_schedule if periodic

---

## Workflow

1. Read task from `.gemini/agents/tasks/<task_id>.json`
2. Implement in canonical file paths above
3. Test CDEK and YooMoney in sandbox mode
4. Test CBR: mock XML response with `respx`, verify Redis caching
5. Run: `pytest tests/unit/integrations/ -v`
6. Write report to `.gemini/agents/reports/cdek/<task_id>.md`
