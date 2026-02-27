# Module: tasks/inventory.py | Agent: backend-agent | Task: BE-01
"""Celery tasks for inventory management."""
from app.tasks.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.integrations.redis_inventory import inventory
from app.api.v1.products.repository import ProductRepository
import asyncio


@celery_app.task(name="tasks.sync_stock_to_redis", bind=True, max_retries=3)
def sync_stock_to_redis(self, variant_id: str, quantity: int) -> None:
    """
    Sync product variant stock from DB to Redis.
    Called after stock changes in DB to keep Redis cache in sync.
    """
    async def _sync():
        async with AsyncSessionLocal() as session:
            repo = ProductRepository(session)
            variant = await repo.get_variant_by_id(variant_id)
            if variant is not None:
                await inventory.set_stock(variant.id, variant.stock)

    try:
        asyncio.get_event_loop().run_until_complete(_sync())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)


@celery_app.task(name="tasks.release_reserved_stock", bind=True, max_retries=3)
def release_reserved_stock(self, variant_id: str, quantity: int) -> None:
    """
    Release previously reserved stock back to Redis.
    Called when an order is cancelled or payment fails.
    """
    async def _release():
        from uuid import UUID
        await inventory.release_stock(UUID(variant_id), quantity)

    try:
        asyncio.get_event_loop().run_until_complete(_release())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
