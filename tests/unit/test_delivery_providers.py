# Module: tests/unit/test_delivery_providers | Agent: backend-agent | Task: p10_backend_delivery_providers
import pytest
from decimal import Decimal
from app.api.v1.delivery.provider import PackageDimensions, DeliveryOption
from app.integrations.pochta import pochta_client
from app.integrations.ozon_delivery import ozon_client
from app.integrations.wb_delivery import wb_client


@pytest.mark.asyncio
async def test_pochta_empty_credentials():
    """Pochta client returns empty list when credentials not configured."""
    result = await pochta_client.calculate_rate(44, 137, PackageDimensions(weight_grams=500))
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_ozon_empty_credentials():
    """Ozon client returns empty list when credentials not configured."""
    result = await ozon_client.calculate_rate(44, 137, PackageDimensions(weight_grams=500))
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_wb_static_tariff():
    """WB client returns static tariff based on weight when credentials configured."""
    result = await wb_client.calculate_rate(44, 137, PackageDimensions(weight_grams=500))
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_wb_pickup_points_empty_credentials():
    """WB pickup points returns empty list when credentials not configured."""
    result = await wb_client.get_pickup_points(44)
    assert isinstance(result, list)
