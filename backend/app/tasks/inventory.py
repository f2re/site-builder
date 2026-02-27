from datetime import datetime, timedelta, timezone
import asyncio
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.db.session import async_session_factory
from app.db.models.order import Order, OrderStatus
from app.integrations.redis_inventory import release_stock
from app.core.logging import logger

@celery_app.task(name="tasks.release_stale_reservations")
def release_stale_reservations_task():
    """
    Find orders in PENDING status older than 30 minutes,
    release their stock in Redis and mark them as CANCELLED.
    """
    async def _process():
        async with async_session_factory() as session:
            # Query pending orders older than 30 minutes
            threshold = datetime.now(timezone.utc) - timedelta(minutes=30)
            stmt = (
                select(Order)
                .where(Order.status == OrderStatus.PENDING)
                .where(Order.created_at < threshold)
            )
            result = await session.execute(stmt)
            stale_orders = result.scalars().all()
            
            for order in stale_orders:
                logger.info("releasing_stale_order", order_id=str(order.id))
                
                # Release stock for each item in order
                for item in order.items:
                    await release_stock(item.product_variant_id, item.quantity)
                
                # Mark as cancelled
                order.status = OrderStatus.CANCELLED
            
            await session.commit()
            return len(stale_orders)

    loop = asyncio.get_event_loop()
    try:
        return loop.run_until_complete(_process())
    except Exception as e:
        logger.error("release_stale_reservations_failed", error=str(e))
        raise
