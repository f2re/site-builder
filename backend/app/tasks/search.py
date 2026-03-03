# Module: tasks/search.py | Agent: backend-agent | Task: phase11_backend_admin_blog_refinement
from meilisearch_python_sdk import AsyncClient
from app.tasks.celery_app import celery_app
from app.core.config import settings
from app.core.logging import logger
import asyncio

@celery_app.task(name="tasks.index_product")
def index_product_task(product_data: dict):
    """
    Index a single product in Meilisearch.
    """
    async def _index():
        async with AsyncClient(settings.MEILISEARCH_HOST, settings.MEILISEARCH_API_KEY) as client:
            index = client.index('products')
            await index.add_documents([product_data])
            
    try:
        asyncio.run(_index())
    except Exception as e:
        logger.error("meilisearch_indexing_failed", domain="products", error=str(e))
        raise

@celery_app.task(name="tasks.remove_product_from_index")
def remove_product_from_index_task(product_id: str):
    """
    Remove a product from Meilisearch index.
    """
    async def _remove():
        async with AsyncClient(settings.MEILISEARCH_HOST, settings.MEILISEARCH_API_KEY) as client:
            index = client.index('products')
            await index.delete_document(product_id)
            
    try:
        asyncio.run(_remove())
    except Exception as e:
        logger.error("meilisearch_removal_failed", domain="products", error=str(e))
        raise

@celery_app.task(name="tasks.index_blog_post")
def index_blog_post_task(post_data: dict):
    """
    Index a single blog post in Meilisearch.
    """
    async def _index():
        async with AsyncClient(settings.MEILISEARCH_HOST, settings.MEILISEARCH_API_KEY) as client:
            index = client.index('blog_posts')
            await index.add_documents([post_data])
            
    try:
        asyncio.run(_index())
    except Exception as e:
        logger.error("meilisearch_indexing_failed", domain="blog", error=str(e))
        raise

@celery_app.task(name="tasks.remove_blog_post_from_index")
def remove_blog_post_from_index_task(post_id: str):
    """
    Remove a blog post from Meilisearch index.
    """
    async def _remove():
        async with AsyncClient(settings.MEILISEARCH_HOST, settings.MEILISEARCH_API_KEY) as client:
            index = client.index('blog_posts')
            await index.delete_document(post_id)
            
    try:
        asyncio.run(_remove())
    except Exception as e:
        logger.error("meilisearch_removal_failed", domain="blog", error=str(e))
        raise
