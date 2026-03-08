# Module: api/v1/webhooks/delivery.py | Agent: cdek-agent | Task: p11_cdek_order_tracking
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.orders.repository import OrderRepository
from app.db.models.order_tracking import OrderTrackingEvent
from app.core.logging import logger
from datetime import datetime, timezone

router = APIRouter()


@router.post("/cdek")
async def cdek_webhook(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    """CDEK delivery status webhook."""
    try:
        payload = await request.json()
        order_uuid = payload.get("attributes", {}).get("number")
        status_code = payload.get("attributes", {}).get("status_code")

        if not order_uuid:
            return {"ok": True, "error": "Missing order number"}

        order_repo = OrderRepository(session)
        order = await order_repo.get_by_cdek_uuid(order_uuid)

        if order:
            event = OrderTrackingEvent(
                order_id=order.id,
                provider="cdek",
                status=status_code,
                message=payload.get("attributes", {}).get("status_name"),
                timestamp=datetime.now(timezone.utc)
            )
            session.add(event)
            order.delivery_status = status_code
            await session.commit()

        return {"ok": True}
    except Exception as e:
        logger.error("cdek_webhook_error", error=str(e))
        return {"ok": True}


@router.post("/pochta")
async def pochta_webhook(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    """Pochta Russia delivery status webhook."""
    try:
        payload = await request.json()
        tracking_number = payload.get("barcode")
        status_code = payload.get("status")

        if not tracking_number:
            return {"ok": True}

        order_repo = OrderRepository(session)
        order = await order_repo.get_by_tracking_number(tracking_number)

        if order:
            event = OrderTrackingEvent(
                order_id=order.id,
                provider="pochta",
                status=status_code,
                message=payload.get("status_text"),
                timestamp=datetime.now(timezone.utc)
            )
            session.add(event)
            order.delivery_status = status_code
            await session.commit()

        return {"ok": True}
    except Exception as e:
        logger.error("pochta_webhook_error", error=str(e))
        return {"ok": True}
