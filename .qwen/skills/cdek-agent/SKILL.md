# WifiOBD Site — CDEK Integration Agent Skill

## Role
Integration agent for external services: **СДЭК v2**, **ЮKassa**, **ЦБ РФ**.

## Integrations

### СДЭК v2 API
**Purpose:** Delivery calculation and order registration

#### Endpoints
- `POST /api/v1/delivery/cdek/calculate` — calculate delivery cost
- `POST /api/v1/delivery/cdek/create` — create order
- `GET /api/v1/delivery/cdek/track/{order_id}` — track order
- `GET /api/v1/delivery/cdek/points` — pickup points list

#### Implementation
```python
# backend/app/integrations/cdek.py
from tenacity import retry, stop_after_attempt, wait_exponential

class CDEKClient:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def get_token(self) -> str:
        # OAuth2 token request
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def calculate(self, from_location: str, to_location: str, weight: float) -> dict:
        # Calculate delivery cost
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def create_order(self, order_data: dict) -> dict:
        # Create order in CDEK
```

#### Environment Variables
```bash
CDEK_API_KEY=your-api-key
CDEK_API_SECRET=your-api-secret
CDEK_BASE_URL=https://api.cdek.ru/v2
CDEK_TEST_MODE=false
```

### ЮKassa
**Purpose:** Payment processing

#### Endpoints
- `POST /api/v1/payments/yookassa/create` — create payment
- `POST /api/v1/payments/yookassa/webhook` — webhook for payment status
- `GET /api/v1/payments/yookassa/status/{payment_id}` — payment status

#### Implementation
```python
# backend/app/integrations/yoomoney.py
import hmac
import hashlib

class YooKassaClient:
    def __init__(self, shop_id: str, api_key: str):
        self.shop_id = shop_id
        self.api_key = api_key
    
    async def create_payment(self, amount: float, order_id: str, return_url: str) -> dict:
        # Create payment link
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        # Verify HMAC-SHA256 signature
    
    async def get_payment_status(self, payment_id: str) -> str:
        # Get payment status
```

#### Webhook Security
```python
# Verify webhook signature
def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

#### Environment Variables
```bash
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_API_KEY=your-api-key
YOOKASSA_WEBHOOK_SECRET=your-webhook-secret
```

### ЦБ РФ (Central Bank of Russia)
**Purpose:** Currency exchange rates (USD, EUR, CNY)

#### Implementation
```python
# backend/app/integrations/cbr_rates.py
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

class CBRRatesClient:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def get_rates(self, date: datetime = None) -> dict:
        # Fetch rates from cbr.ru
        # Returns: {'USD': 92.5, 'EUR': 99.8, 'CNY': 12.7}
    
    def parse_xml(self, xml_content: str) -> dict:
        # Parse XML response from CBR
```

#### Celery Task (Daily Update)
```python
# backend/app/tasks/currency_rates.py
from celery.schedules import crontab

@celery_app.task
@retry(stop=stop_after_attempt(3))
def update_cbr_rates():
    """Daily task to fetch and store CBR rates"""
    rates = cbr_client.get_rates()
    # Store in database
```

#### Environment Variables
```bash
CBR_API_URL=http://www.cbr.ru/scripts/XML_daily.asp
```

## Common Patterns

### Retry Policy (ALL external calls)
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=10),
    reraise=True
)
async def external_api_call():
    ...
```

### Error Handling
```python
from app.core.exceptions import IntegrationError

class CDEKError(IntegrationError):
    """CDEK API error"""
    pass

class YooKassaError(IntegrationError):
    """YooKassa API error"""
    pass
```

### Celery Tasks
```python
# backend/app/tasks/cdek_tasks.py
@celery_app.task(bind=True, max_retries=3)
def calculate_delivery_task(self, order_id: int):
    try:
        # Calculate delivery
        pass
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

## Testing

### Integration Tests
```python
# tests/integration/test_cdek.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_calculate_delivery():
    with patch('app.integrations.cdek.CDEKClient.get_token') as mock_token:
        mock_token.return_value = 'test-token'
        # Test calculation
```

## Report Format
Save reports to `.qwen/agents/reports/cdek/<task_id>.md`

```markdown
## Status: DONE

## Completed:
- implemented CDEK v2 integration
- added YooKassa payment processing
- created Celery tasks for daily rates

## Artifacts:
- backend/app/integrations/cdek.py
- backend/app/integrations/yoomoney.py
- backend/app/integrations/cbr_rates.py
- backend/app/tasks/currency_rates.py

## Contracts Verified:
- Retry policy (tenacity): ✅
- Error handling: ✅
- Webhook signature verification: ✅
- Celery tasks: ✅

## Tests:
- integration/test_cdek.py: PASSED
- integration/test_yookassa.py: PASSED

## Next:
- backend-agent: integrate delivery into order flow
- frontend-agent: add delivery calculator UI

## Blockers:
- none
```
