# Module: tests/unit/api/delivery/test_service | Agent: backend-agent | Task: BE-03_cart_orders_payments (refined)

import pytest
from unittest.mock import AsyncMock, patch
from app.api.v1.delivery.service import DeliveryService

@pytest.mark.anyio
async def test_get_pickup_points_cleans_data():
    service = DeliveryService()
    
    # Mock data from CDEK
    mock_raw_points = [
        {
            "code": "PVZ1",
            "name": "Point 1",
            "location": {
                "address": "Street 1",
                "latitude": 55.75,
                "longitude": 37.61
            },
            "work_time": "09:00-18:00",
            "phones": [{"number": "+79001112233"}],
            "note": "Bring ID"
        },
        {
            "code": "PVZ2",
            "name": "Point 2",
            "location": {
                "address": "Street 2",
                "latitude": 55.80,
                "longitude": 37.70
            },
            "work_time": "10:00-19:00",
            "phones": [],
            "address_comment": "Blue door"
        }
    ]
    
    with patch("app.api.v1.delivery.service.cdek_client.get_pickup_points", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_raw_points
        
        # Ensure redis is mocked or doesn't interfere
        with patch("app.api.v1.delivery.service.get_redis_client") as mock_get_redis:
            mock_get_redis.return_value.get = AsyncMock(return_value=None)
            mock_get_redis.return_value.set = AsyncMock()
                
            result = await service.get_pickup_points(44)
            
            assert len(result) == 2
            assert result[0].code == "PVZ1"
            assert result[0].phone == "+79001112233"
            assert result[0].note == "Bring ID"
            assert result[0].latitude == 55.75
            
            assert result[1].code == "PVZ2"
            assert result[1].phone == ""
            assert result[1].note == "Blue door"
            assert result[1].latitude == 55.80

@pytest.mark.anyio
async def test_get_pickup_points_uses_cache():
    service = DeliveryService()
    cached_data = [
        {
            "code": "CACHED",
            "name": "Cached Point",
            "address": "Cached St",
            "latitude": 1.0,
            "longitude": 1.0,
            "work_time": "24h",
            "phone": "123",
            "note": "N/A"
        }
    ]
    
    import json
    with patch("app.api.v1.delivery.service.get_redis_client") as mock_get_redis:
        mock_get_redis.return_value.get = AsyncMock(return_value=json.dumps(cached_data).encode())
        
        result = await service.get_pickup_points(44)
        
        assert len(result) == 1
        assert result[0].code == "CACHED"
        # Ensure cdek_client was NOT called
        with patch("app.api.v1.delivery.service.cdek_client.get_pickup_points", new_callable=AsyncMock) as mock_cdek:
            assert not mock_cdek.called
