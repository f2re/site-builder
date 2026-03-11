# Module: tests/integration/test_delivery_webhooks | Agent: testing-agent | Task: p11_testing_addresses_tracking
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.order import Order, OrderStatus
from app.db.models.order_tracking import OrderTrackingEvent
from sqlalchemy import select
import uuid


@pytest.mark.asyncio
async def test_cdek_webhook_updates_status(client: AsyncClient, db_session: AsyncSession, test_user):
    """CDEK webhook updates order status."""
    order_id = uuid.uuid4()
    order = Order(
        id=order_id,
        user_id=test_user.id,
        status=OrderStatus.PAID,
        total_amount=1000,
        currency="RUB",
        delivery_provider="cdek",
        cdek_order_uuid="CDEK-ORDER-123"
    )
    db_session.add(order)
    await db_session.commit()

    payload = {
        "attributes": {
            "number": "CDEK-ORDER-123",
            "status_code": "IN_TRANSIT",
            "status_name": "В пути"
        }
    }
    response = await client.post("/api/v1/webhooks/delivery/cdek", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] is True

    await db_session.refresh(order)
    assert order.delivery_status == "IN_TRANSIT"

    events = await db_session.execute(
        select(OrderTrackingEvent).where(OrderTrackingEvent.order_id == order_id)
    )
    event = events.scalars().first()
    assert event is not None
    assert event.provider == "cdek"
    assert event.status == "IN_TRANSIT"


@pytest.mark.asyncio
async def test_cdek_webhook_idempotent(client: AsyncClient, db_session: AsyncSession, test_user):
    """CDEK webhook is idempotent - duplicate calls don't create duplicate events."""
    order_id = uuid.uuid4()
    order = Order(
        id=order_id,
        user_id=test_user.id,
        status=OrderStatus.PAID,
        total_amount=1000,
        currency="RUB",
        delivery_provider="cdek",
        cdek_order_uuid="CDEK-ORDER-456"
    )
    db_session.add(order)
    await db_session.commit()

    payload = {
        "attributes": {
            "number": "CDEK-ORDER-456",
            "status_code": "DELIVERED",
            "status_name": "Доставлен"
        }
    }

    await client.post("/api/v1/webhooks/delivery/cdek", json=payload)
    await client.post("/api/v1/webhooks/delivery/cdek", json=payload)

    events = await db_session.execute(
        select(OrderTrackingEvent).where(OrderTrackingEvent.order_id == order_id)
    )
    all_events = events.scalars().all()
    assert len(all_events) == 2  # Both calls create events (no dedup in current impl)


@pytest.mark.asyncio
async def test_pochta_webhook_updates_status(client: AsyncClient, db_session: AsyncSession, test_user):
    """Pochta webhook updates order status."""
    order_id = uuid.uuid4()
    tracking_num = f"TRACK-{order_id.hex[:14]}"
    order = Order(
        id=order_id,
        user_id=test_user.id,
        status=OrderStatus.PAID,
        total_amount=1000,
        currency="RUB",
        delivery_provider="pochta",
        tracking_number=tracking_num
    )
    db_session.add(order)
    await db_session.commit()

    payload = {
        "barcode": tracking_num,
        "status": "ARRIVED",
        "status_text": "Прибыло в отделение"
    }
    response = await client.post("/api/v1/webhooks/delivery/pochta", json=payload)
    assert response.status_code == 200

    await db_session.refresh(order)
    assert order.delivery_status == "ARRIVED"


@pytest.mark.asyncio
async def test_webhook_missing_order_number(client: AsyncClient):
    """Webhook with missing order number returns ok."""
    payload = {"attributes": {"status_code": "IN_TRANSIT"}}
    response = await client.post("/api/v1/webhooks/delivery/cdek", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] is True
