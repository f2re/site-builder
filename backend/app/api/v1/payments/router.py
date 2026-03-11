# Module: api/v1/payments/router.py | Agent: backend-agent | Task: BE-03
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json
from datetime import datetime, timezone

from app.core.config import settings
from app.core.logging import logger
from app.db.session import get_db
from app.db.redis import get_redis_client
from app.integrations.yoomoney import yoomoney_client
from app.api.v1.orders.repository import OrderRepository
from app.db.models.order import OrderStatus
from app.tasks.notifications.dispatcher import send_email_task


router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/webhook")
async def yoomoney_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    body_bytes = await request.body()
    # YooKassa might use X-Kassa-Signature or X-Signature
    signature = request.headers.get("X-YooKassa-Signature") or request.headers.get("X-Signature")
    
    if signature and not yoomoney_client.verify_webhook_signature(settings.YOOMONEY_SECRET, body_bytes, signature):
        logger.warning("invalid_payment_signature", signature=signature)
        # In production we might return 200 even for invalid signature to avoid probing
        # but here we follow the instruction to verify.
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        data = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event = data.get("event")
    payment_obj = data.get("object", {})
    payment_id = payment_obj.get("id")
    if not payment_id:
        return {"status": "ignored"}

    # Idempotency: avoid processing same payment_id twice
    idempotency_key = f"payments:processed:{payment_id}"
    is_new = await get_redis_client().set(idempotency_key, "1", nx=True, ex=86400)
    if not is_new:
        logger.info("payment_already_processed", payment_id=payment_id)
        return {"status": "already_processed"}

    if event == "payment.succeeded":
        order_id = payment_obj.get("metadata", {}).get("order_id")
        if not order_id:
            logger.error("payment_succeeded_missing_order_id", payment_id=payment_id)
            return {"status": "error", "message": "missing order_id"}

        order_repo = OrderRepository(db)
        order = await order_repo.get_by_id(order_id)
        if not order:
            logger.error("order_not_found_for_payment", order_id=order_id, payment_id=payment_id)
            return {"status": "error", "message": "order not found"}

        if order.status == OrderStatus.PAID:
            logger.info("order_already_paid", order_id=order_id)
            return {"status": "ok"}

        # Update order status
        order.status = OrderStatus.PAID
        order.payment_id = payment_id
        order.paid_at = datetime.now(timezone.utc)
        
        await order_repo.update(order)
        await db.commit()
        logger.info("payment_processed_successfully", order_id=order_id, payment_id=payment_id)

        # Trigger notifications or other downstream processes
        if order.user:
            send_email_task.delay(
                recipient=order.user.email,
                subject=f"Заказ #{order.id} оплачен",
                template_name="order_paid.html",
                context={
                    "full_name": order.user.full_name or order.user.email,
                    "order_id": str(order.id),
                    "total_amount": str(order.total_amount)
                }
            )
            
    elif event == "payment.canceled":
        # Optional: handle cancellation, release stock?
        logger.info("payment_canceled", payment_id=payment_id)

    return {"status": "ok"}
