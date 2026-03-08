# Module: tests/unit/test_tracking_urls | Agent: testing-agent | Task: p11_testing_addresses_tracking
from app.integrations.cdek import cdek_client
from app.integrations.pochta import pochta_client
from app.integrations.ozon_delivery import get_tracking_url as ozon_tracking
from app.integrations.wb_delivery import get_tracking_url as wb_tracking


def test_cdek_tracking_url():
    """CDEK tracking URL generation."""
    url = cdek_client.get_tracking_url("ORDER123")
    assert url == "https://www.cdek.ru/ru/tracking?order_id=ORDER123"


def test_pochta_tracking_url():
    """Pochta Russia tracking URL generation."""
    url = pochta_client.get_tracking_url("12345678901234")
    assert url == "https://www.pochta.ru/tracking#12345678901234"


def test_ozon_tracking_url():
    """Ozon tracking URL generation."""
    url = ozon_tracking("98765432")
    assert url == "https://www.ozon.ru/my/orderdetails?orderId=98765432"


def test_wb_tracking_url():
    """Wildberries tracking URL generation."""
    url = wb_tracking("WB123456")
    assert url == "https://www.wildberries.ru/lk/myorders/delivery?id=WB123456"
