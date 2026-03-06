# Эталонный unit-тест
import pytest
from unittest.mock import AsyncMock, patch
from fakeredis.aioredis import FakeRedis
from app.api.v1.cart.service import CartService

@pytest.fixture
def redis():
    return FakeRedis()

@pytest.mark.asyncio
async def test_add_to_cart_success(redis):
    service = CartService(redis=redis)
    result = await service.add_item(
        user_id=1, product_id=42, quantity=2
    )
    assert result.total_items == 2
    # Проверить TTL резервирования
    ttl = await redis.ttl("cart:user:1")
    assert ttl > 0