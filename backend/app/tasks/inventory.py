from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.db.celery_session import CelerySessionLocal
from app.db.models.order import Order, OrderStatus
from app.integrations.redis_inventory import get_inventory_for_celery
from app.core.logging import logger
from app.core.utils import run_async
from app.api.v1.products.repository import ProductRepository


@celery_app.task(name="tasks.release_stale_reservations")
def release_stale_reservations_task():
    """
    Find orders in PENDING status older than 30 minutes,
    release their stock in Redis and mark them as CANCELLED.
    """
    async def _process():
        inventory = get_inventory_for_celery()
        async with CelerySessionLocal() as session:
            # Query pending orders older than 30 minutes
            threshold = datetime.now(timezone.utc) - timedelta(minutes=30)
            stmt = (
                select(Order)
                .where(Order.status == OrderStatus.PENDING.value)
                .where(Order.created_at < threshold)
            )
            result = await session.execute(stmt)
            stale_orders = result.scalars().all()

            for order in stale_orders:
                logger.info("releasing_stale_order", order_id=str(order.id))

                # Release stock for each item in order
                for item in order.items:
                    await inventory.release_stock(item.product_variant_id, item.quantity)

                # Mark as cancelled
                order.status = OrderStatus.CANCELLED

            await session.commit()
            return len(stale_orders)

    try:
        return run_async(_process())
    except Exception as e:
        logger.error("release_stale_reservations_failed", error=str(e))
        raise



@celery_app.task(name="tasks.sync_stock_to_redis", bind=True, max_retries=3)
def sync_stock_to_redis(self, variant_id: str, quantity: int) -> None:
    """
    Sync product variant stock from DB to Redis.
    Called after stock changes in DB to keep Redis cache in sync.
    """
    async def _sync():
        inventory = get_inventory_for_celery()
        async with CelerySessionLocal() as session:
            repo = ProductRepository(session)
            variant = await repo.get_variant_by_id(variant_id)
            if variant is not None:
                await inventory.set_stock(variant.id, variant.stock)

    try:
        run_async(_sync())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)


@celery_app.task(name="tasks.release_reserved_stock", bind=True, max_retries=3)
def release_reserved_stock(self, variant_id: str, quantity: int) -> None:
    """
    Release previously reserved stock back to Redis.
    Called when an order is cancelled or payment fails.
    """
    async def _release():
        inventory = get_inventory_for_celery()
        from uuid import UUID
        await inventory.release_stock(UUID(variant_id), quantity)

    try:
        run_async(_release())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
