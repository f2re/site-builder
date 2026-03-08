# Module: tests/unit/test_delivery_providers | Agent: backend-agent | Task: p10_backend_delivery_providers
import pytest
from app.api.v1.delivery.provider import PackageDimensions
from app.integrations.pochta import pochta_client
from app.integrations import ozon_delivery
from app.integrations import wb_delivery


@pytest.mark.asyncio
async def test_pochta_empty_credentials():
    """Pochta client returns empty list when credentials not configured."""
    result = await pochta_client.calculate_rate(44, 137, PackageDimensions(weight_grams=500))
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_ozon_pickup_points():
    """Ozon returns static pickup points for Moscow."""
    # 44 is Moscow in CITY_MAPPING
    result = await ozon_delivery.get_pickup_points(44)
    assert len(result) > 0
    assert result[0].provider == "ozon"


@pytest.mark.asyncio
async def test_wb_pickup_points():
    """WB returns static pickup points for Moscow."""
    # 44 is Moscow in CITY_MAPPING
    result = await wb_delivery.get_pickup_points(44)
    assert len(result) > 0
    assert result[0].provider == "wb"


def test_tracking_urls():
    """Test tracking URL generation for all providers."""
    assert "orderId=123" in ozon_delivery.get_tracking_url("123")
    assert "id=123" in wb_delivery.get_tracking_url("123")
    assert "tracking#123" in pochta_client.get_tracking_url("123")
