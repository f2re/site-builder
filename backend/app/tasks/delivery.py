# Module: tasks/delivery.py | Agent: cdek-agent | Task: p11_cdek_order_tracking
from app.tasks.celery_app import celery_app
from app.db.celery_session import CelerySessionLocal
from app.api.v1.orders.repository import OrderRepository
from app.db.models.order import OrderStatus
from app.db.models.order_tracking import OrderTrackingEvent
from app.integrations.cdek import cdek_client
from app.integrations.pochta import pochta_client
from app.core.logging import logger
from app.core.utils import run_async
from datetime import datetime, timezone


async def _poll_delivery_statuses():
    """Poll delivery statuses for in-transit orders."""
    async with CelerySessionLocal() as session:
        order_repo = OrderRepository(session)
        orders = await order_repo.get_orders_in_transit()

        for order in orders:
            try:
                if order.delivery_provider == "cdek" and order.cdek_order_uuid:
                    data = await cdek_client.get_order_status(order.cdek_order_uuid)
                    status_code = data.get("entity", {}).get("statuses", [{}])[-1].get("code")

                    if status_code and status_code != order.delivery_status:
                        event = OrderTrackingEvent(
                            order_id=order.id,
                            provider="cdek",
                            status=status_code,
                            message=data.get("entity", {}).get("statuses", [{}])[-1].get("name"),
                            timestamp=datetime.now(timezone.utc)
                        )
                        session.add(event)
                        order.delivery_status = status_code

                        if status_code == "DELIVERED":
                            order.status = OrderStatus.DELIVERED

                elif order.delivery_provider == "pochta" and order.tracking_number:
                    data = await pochta_client.get_shipment_status(order.tracking_number)
                    status_code = data.get("status")

                    if status_code and status_code != order.delivery_status:
                        event = OrderTrackingEvent(
                            order_id=order.id,
                            provider="pochta",
                            status=status_code,
                            message=data.get("status_text"),
                            timestamp=datetime.now(timezone.utc)
                        )
                        session.add(event)
                        order.delivery_status = status_code

            except Exception as e:
                logger.error("poll_status_error", order_id=str(order.id), error=str(e))

        await session.commit()


@celery_app.task(name="tasks.delivery.poll_delivery_statuses")
def poll_delivery_statuses():
    """Celery task: poll delivery statuses every 6 hours."""
    run_async(_poll_delivery_statuses())
