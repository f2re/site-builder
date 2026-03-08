# Module: tests/unit/test_celery_poll_delivery | Agent: testing-agent | Task: p11_testing_addresses_tracking
import pytest
from unittest.mock import AsyncMock, patch
from app.tasks.delivery import _poll_delivery_statuses
from app.db.models.order import Order, OrderStatus
import uuid


@pytest.mark.asyncio
async def test_poll_delivery_statuses_cdek(db_session):
    """Poll delivery statuses updates CDEK orders."""
    order_id = uuid.uuid4()
    order = Order(
        id=order_id,
        user_id=uuid.uuid4(),
        status=OrderStatus.PAID,
        total_amount=1000,
        currency="RUB",
        delivery_provider="cdek",
        cdek_order_uuid="CDEK-123",
        delivery_status="CREATED"
    )
    db_session.add(order)
    await db_session.commit()

    mock_cdek_response = {
        "entity": {
            "statuses": [{"code": "IN_TRANSIT", "name": "В пути"}]
        }
    }

    with patch("app.tasks.delivery.AsyncSessionLocal") as mock_session:
        mock_session.return_value.__aenter__.return_value = db_session
        with patch("app.integrations.cdek.cdek_client.get_order_status", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_cdek_response
            with patch("app.api.v1.orders.repository.OrderRepository.get_orders_in_transit", new_callable=AsyncMock) as mock_orders:
                mock_orders.return_value = [order]

                await _poll_delivery_statuses()

    await db_session.refresh(order)
    assert order.delivery_status == "IN_TRANSIT"


@pytest.mark.asyncio
async def test_poll_delivery_statuses_pochta(db_session):
    """Poll delivery statuses updates Pochta orders."""
    order_id = uuid.uuid4()
    order = Order(
        id=order_id,
        user_id=uuid.uuid4(),
        status=OrderStatus.PAID,
        total_amount=1000,
        currency="RUB",
        delivery_provider="pochta",
        tracking_number="12345678901234",
        delivery_status="CREATED"
    )
    db_session.add(order)
    await db_session.commit()

    mock_pochta_response = {
        "status": "ARRIVED",
        "status_text": "Прибыло"
    }

    with patch("app.tasks.delivery.AsyncSessionLocal") as mock_session:
        mock_session.return_value.__aenter__.return_value = db_session
        with patch("app.integrations.pochta.pochta_client.get_shipment_status", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_pochta_response
            with patch("app.api.v1.orders.repository.OrderRepository.get_orders_in_transit", new_callable=AsyncMock) as mock_orders:
                mock_orders.return_value = [order]

                await _poll_delivery_statuses()

    await db_session.refresh(order)
    assert order.delivery_status == "ARRIVED"


@pytest.mark.asyncio
async def test_poll_delivery_statuses_handles_errors(db_session):
    """Poll delivery statuses handles provider errors gracefully."""
    order = Order(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        status=OrderStatus.PAID,
        total_amount=1000,
        currency="RUB",
        delivery_provider="cdek",
        cdek_order_uuid="CDEK-ERROR",
        delivery_status="CREATED"
    )
    db_session.add(order)
    await db_session.commit()

    with patch("app.tasks.delivery.AsyncSessionLocal") as mock_session:
        mock_session.return_value.__aenter__.return_value = db_session
        with patch("app.integrations.cdek.cdek_client.get_order_status", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("API Error")
            with patch("app.api.v1.orders.repository.OrderRepository.get_orders_in_transit", new_callable=AsyncMock) as mock_orders:
                mock_orders.return_value = [order]

                await _poll_delivery_statuses()  # Should not raise

    await db_session.refresh(order)
    assert order.delivery_status == "CREATED"  # Unchanged
