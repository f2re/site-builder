# WifiOBD Site — Testing Agent Skill

## Role
Testing agent for **WifiOBD Site** — pytest, integration tests, load tests.

## Stack
- **pytest** — unit and integration tests
- **pytest-asyncio** — async test support
- **httpx** — async HTTP client for API tests
- **Locust** — load testing
- **coverage.py** — code coverage

## Test Structure

```
tests/
├── conftest.py              # Fixtures and config
├── unit/
│   ├── test_auth.py
│   ├── test_products.py
│   ├── test_cart.py
│   └── test_orders.py
├── integration/
│   ├── test_api.py
│   ├── test_cdek.py
│   ├── test_yookassa.py
│   └── test_websocket.py
├── load/
│   └── locustfile.py
└── e2e/
    └── test_checkout_flow.py
```

## Unit Tests

### Pattern
```python
# tests/unit/test_cart.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.api.v1.cart.service import CartService
from app.api.v1.cart.repository import CartRepository

@pytest.fixture
def mock_cart_repo():
    return MagicMock(spec=CartRepository)

@pytest.fixture
def cart_service(mock_cart_repo):
    return CartService(cart_repo=mock_cart_repo)

@pytest.mark.asyncio
async def test_add_to_cart(cart_service, mock_cart_repo):
    # Arrange
    mock_cart_repo.get_by_user_id = AsyncMock(return_value=None)
    mock_cart_repo.create = AsyncMock(return_value=MagicMock(id=1))
    
    # Act
    result = await cart_service.add_item(user_id=1, product_id=42, quantity=2)
    
    # Assert
    assert result.id == 1
    mock_cart_repo.create.assert_called_once()
```

### Coverage Targets
- **Services:** > 80%
- **API endpoints:** > 70%
- **Repositories:** > 60%

## Integration Tests

### API Tests
```python
# tests/integration/test_api.py
import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_products_list(client: AsyncClient):
    response = await client.get("/api/v1/products/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "next_cursor" in data

@pytest.mark.asyncio
async def test_create_order_authenticated(client: AsyncClient, auth_headers):
    payload = {
        "items": [{"product_id": 1, "quantity": 2}],
        "delivery_address": "Test Address"
    }
    
    response = await client.post(
        "/api/v1/orders/",
        json=payload,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    assert "order_id" in response.json()
```

### WebSocket Tests
```python
# tests/integration/test_websocket.py
import pytest
from fastapi.testclient import TestClient

def test_iot_websocket_connection():
    client = TestClient(app)
    
    with client.websocket_connect("/ws/iot/test-device?token=test-token") as ws:
        ws.send_json({"device_id": "test-device", "data": {"rpm": 3000}})
        response = ws.receive_json()
        assert response["status"] == "received"
```

### External Integration Tests
```python
# tests/integration/test_cdek.py
import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_cdek_calculate():
    with patch('app.integrations.cdek.CDEKClient.get_token') as mock_token:
        mock_token.return_value = 'test-token'
        
        from app.api.v1.delivery.cdek import calculate_delivery
        
        result = await calculate_delivery(
            from_location="Moscow",
            to_location="Saint Petersburg",
            weight=1.0
        )
        
        assert "cost" in result
        assert "delivery_time" in result
```

## Load Tests (Locust)

### Pattern
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between
import random

class ShopUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_products(self):
        self.client.get("/api/v1/products/")
    
    @task(2)
    def view_product_detail(self):
        product_id = random.randint(1, 100)
        self.client.get(f"/api/v1/products/{product_id}")
    
    @task(1)
    def add_to_cart(self):
        product_id = random.randint(1, 100)
        self.client.post(
            "/api/v1/cart/add",
            json={"product_id": product_id, "quantity": 1}
        )

class CheckoutUser(HttpUser):
    wait_time = between(5, 10)
    
    @task
    def complete_checkout(self):
        # Simulate full checkout flow
        self.client.post("/api/v1/orders/", json={...})
```

### Run Load Test
```bash
# 100 users, 10 users/sec spawn rate, 5 minutes
locust -f tests/load/locustfile.py --users 100 --spawn-rate 10 --run-time 5m --headless
```

## Fixtures

### conftest.py
```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_async_session

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_headers(client: AsyncClient):
    # Login and get token
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_db_session():
    # Create test database session
    session = ...
    yield session
    # Cleanup
    session.close()
```

## Pre-Commit Checklist

```bash
# Run all tests
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

# Check coverage targets
coverage report --fail-under=70

# Run specific test category
pytest tests/unit/ -v
pytest tests/integration/ -v -m "not slow"
pytest tests/load/locustfile.py --users 50 --spawn-rate 5 --run-time 1m --headless
```

## Test Markers

```python
# Mark slow tests (load tests, external API)
@pytest.mark.slow

# Mark tests requiring external services
@pytest.mark.external

# Mark database tests
@pytest.mark.db

# Run specific markers
pytest -v -m "not slow"  # Skip slow tests
pytest -v -m "db"        # Run only DB tests
```

## Report Format
Save reports to `.qwen/agents/reports/testing/<task_id>.md`

```markdown
## Status: DONE

## Completed:
- wrote unit tests for cart service
- wrote integration tests for products API
- created load test scenarios

## Artifacts:
- tests/unit/test_cart.py
- tests/integration/test_products.py
- tests/load/locustfile.py

## Test Results:
- Unit tests: 45 passed, 0 failed
- Integration tests: 12 passed, 0 failed
- Load test: 100 users, avg response 120ms

## Coverage:
- services/cart.py: 84%
- api/v1/cart/: 71%
- Overall: 76%

## Contracts Verified:
- All tests pass: ✅
- Coverage targets met: ✅
- Load test successful: ✅

## Next:
- security-agent: ready for security audit

## Blockers:
- none
```
