# Module: tasks/search.py | Agent: backend-agent | Task: p11_backend_002
import asyncio
from decimal import Decimal
from typing import Any, Dict

from meilisearch_python_sdk import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.logging import logger
from app.db.models.product import Product
from app.db.session import AsyncSessionLocal
from app.tasks.celery_app import celery_app


def _sanitize_for_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Decimal values to float so Meilisearch can serialize the document."""
    return {k: float(v) if isinstance(v, Decimal) else v for k, v in data.items()}


@celery_app.task(name="tasks.index_product")
def index_product_task(product_data: Dict[str, Any]) -> None:
    """
    Index a single product in Meilisearch.
    """
    safe_data = _sanitize_for_json(product_data)

    async def _index() -> None:
        async with AsyncClient(settings.MEILISEARCH_HOST, settings.MEILISEARCH_API_KEY) as client:
            index = client.index("products")
            await index.add_documents([safe_data])

    try:
        asyncio.run(_index())
    except Exception as e:
        logger.error("meilisearch_indexing_failed", domain="products", error=str(e))
        raise


@celery_app.task(name="tasks.remove_product_from_index")
def remove_product_from_index_task(product_id: str) -> None:
    """
    Remove a product from Meilisearch index.
    """

    async def _remove() -> None:
        async with AsyncClient(settings.MEILISEARCH_HOST, settings.MEILISEARCH_API_KEY) as client:
            index = client.index("products")
            await index.delete_document(product_id)

    try:
        asyncio.run(_remove())
    except Exception as e:
        logger.error("meilisearch_removal_failed", domain="products", error=str(e))
        raise


@celery_app.task(name="tasks.index_blog_post")
def index_blog_post_task(post_data: Dict[str, Any]) -> None:
    """
    Index a single blog post in Meilisearch.
    """

    async def _index() -> None:
        async with AsyncClient(settings.MEILISEARCH_HOST, settings.MEILISEARCH_API_KEY) as client:
            index = client.index("blog_posts")
            await index.add_documents([post_data])

    try:
        asyncio.run(_index())
    except Exception as e:
        logger.error("meilisearch_indexing_failed", domain="blog", error=str(e))
        raise


@celery_app.task(name="tasks.remove_blog_post_from_index")
def remove_blog_post_from_index_task(post_id: str) -> None:
    """
    Remove a blog post from Meilisearch index.
    """

    async def _remove() -> None:
        async with AsyncClient(settings.MEILISEARCH_HOST, settings.MEILISEARCH_API_KEY) as client:
            index = client.index("blog_posts")
            await index.delete_document(post_id)

    try:
        asyncio.run(_remove())
    except Exception as e:
        logger.error("meilisearch_removal_failed", domain="blog", error=str(e))
        raise


@celery_app.task(name="tasks.sync_products_to_meilisearch")
def sync_products_to_meilisearch_task() -> None:
    """
    Bulk sync all active products to Meilisearch.
    """

    async def _sync() -> None:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(Product)
                .where(Product.is_active == True)  # noqa: E712
                .options(selectinload(Product.variants), selectinload(Product.category))
            )
            result = await session.execute(stmt)
            products = result.scalars().all()

            documents = []
            for p in products:
                # Basic document structure
                doc = {
                    "id": str(p.id),
                    "name": p.name,
                    "slug": p.slug,
                    "description": p.description,
                    "category": p.category.name if p.category else None,
                    "price": float(min([v.price for v in p.variants])) if p.variants else 0,
                    "in_stock": any(v.stock_quantity > 0 for v in p.variants),
                }
                documents.append(doc)

            if documents:
                async with AsyncClient(settings.MEILISEARCH_HOST, settings.MEILISEARCH_API_KEY) as client:
                    index = client.index("products")
                    await index.add_documents(documents)

    try:
        asyncio.run(_sync())
    except Exception as e:
        logger.error("meilisearch_bulk_sync_failed", domain="products", error=str(e))
        raise
