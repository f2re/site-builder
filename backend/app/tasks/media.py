"""Media processing tasks for Celery.

Handles image optimization, WebP conversion, thumbnail generation,
and dimension extraction for blog posts and product images.
"""
import asyncio
from io import BytesIO
from pathlib import Path
from typing import Literal, Any, cast

from PIL import Image
from sqlalchemy import select

from app.core.logging import logger
from app.db.celery_session import CelerySessionLocal
from app.integrations.local_storage import storage_client
from app.tasks.celery_app import celery_app


@celery_app.task(name="tasks.process_image", bind=True, max_retries=3)
def process_image(
    self,
    object_name: str,
    media_id: int,
    context: Literal["blog", "product"] = "blog",
):
    """
    Process uploaded image:
    1. Read original from local storage
    2. Extract real dimensions (width, height) via Pillow
    3. Convert to WebP (quality=85) for better compression
    4. Generate thumbnail (480px max dimension)
    5. Save WebP + thumbnail back to local storage
    6. Update database record with new URLs and dimensions
    7. Optionally delete original (configurable)

    Args:
        object_name: Path in storage (e.g., 'blog/2026/02/image.jpg')
        media_id: ID of BlogPostMedia or ProductImage record
        context: 'blog' or 'product' - determines which model to update
    """
    try:
        logger.info(
            "processing_image_start",
            object_name=object_name,
            media_id=media_id,
            context=context,
        )

        # Run async operation in sync context
        asyncio.run(_process_image_async(object_name, media_id, context))

        logger.info(
            "processing_image_complete",
            object_name=object_name,
            media_id=media_id,
        )

    except Exception as exc:
        logger.error(
            "processing_image_failed",
            object_name=object_name,
            media_id=media_id,
            error=str(exc),
            retry_count=self.request.retries,
        )
        # Exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


async def _process_image_async(
    object_name: str,
    media_id: int,
    context: Literal["blog", "product"],
):
    """Async implementation of image processing."""
    # 1. Read original from local storage
    logger.info("reading_original_file", object_name=object_name)
    image_data = await storage_client.read_file(object_name)

    # 2. Load image with Pillow and extract dimensions
    img_pillow = cast(Any, Image.open(BytesIO(image_data)))
    original_format = img_pillow.format
    width, height = img_pillow.size
    logger.info(
        "image_dimensions_extracted",
        width=width,
        height=height,
        format=original_format,
    )

    # Convert RGBA to RGB if needed (WebP with transparency requires special handling)
    if img_pillow.mode in ("RGBA", "LA", "P"):
        # Create white background
        background = cast(Any, Image.new("RGB", img_pillow.size, (255, 255, 255)))
        if img_pillow.mode == "P":
            img_pillow = img_pillow.convert("RGBA")
        background.paste(img_pillow, mask=img_pillow.split()[-1] if img_pillow.mode == "RGBA" else None)
        img_pillow = background

    # 3. Convert to WebP (quality=85 is optimal balance)
    webp_buffer = BytesIO()
    img_pillow.save(webp_buffer, format="WEBP", quality=85, method=6)
    webp_buffer.seek(0)
    webp_size = len(webp_buffer.getvalue())

    # Generate WebP filename
    path_obj = Path(object_name)
    webp_name = str(path_obj.with_suffix(".webp"))

    logger.info(
        "saving_webp",
        webp_name=webp_name,
        size_bytes=webp_size,
    )

    # Save WebP to local storage
    await storage_client.save_file(
        webp_name,
        webp_buffer.getvalue(),
        content_type="image/webp",
    )

    # 4. Create thumbnail (max 480px on longest side)
    img_pillow.thumbnail((480, 480), Image.Resampling.LANCZOS)
    thumb_buffer = BytesIO()
    img_pillow.save(thumb_buffer, format="WEBP", quality=85, method=6)
    thumb_buffer.seek(0)
    thumb_size = len(thumb_buffer.getvalue())
    thumb_width, thumb_height = img_pillow.size

    thumb_name = str(path_obj.with_name(f"{path_obj.stem}_thumb.webp"))

    logger.info(
        "saving_thumbnail",
        thumb_name=thumb_name,
        size_bytes=thumb_size,
        dimensions=f"{thumb_width}x{thumb_height}",
    )

    await storage_client.save_file(
        thumb_name,
        thumb_buffer.getvalue(),
        content_type="image/webp",
    )

    # 5. Update database record
    async with CelerySessionLocal() as db:
        if context == "blog":
            from app.db.models.blog import BlogPostMedia

            stmt_blog = select(BlogPostMedia).where(BlogPostMedia.id == media_id)
            result_blog = await db.execute(stmt_blog)
            media_blog = result_blog.scalar_one_or_none()

            if media_blog:
                media_blog.url = webp_name
                media_blog.width = width
                media_blog.height = height
                media_blog.mime_type = "image/webp"
                media_blog.size_bytes = webp_size
                await db.commit()
                logger.info("blog_media_updated", media_id=media_id)

        elif context == "product":
            from app.db.models.product import ProductImage

            stmt_prod = select(ProductImage).where(ProductImage.id == media_id)
            result_prod = await db.execute(stmt_prod)
            media_prod = result_prod.scalar_one_or_none()

            if media_prod:
                media_prod.url = webp_name
                media_prod.width = width
                media_prod.height = height
                await db.commit()
                logger.info("product_image_updated", media_id=media_id)


@celery_app.task(name="tasks.delete_media_from_storage")
def delete_media_from_storage(object_name: str):
    """
    Delete media file from storage.
    Called when BlogPostMedia or ProductImage is deleted from database.
    """
    try:
        asyncio.run(_delete_media_async(object_name))
        logger.info("media_deleted_from_storage", object_name=object_name)
    except Exception as exc:
        logger.error(
            "media_deletion_failed",
            object_name=object_name,
            error=str(exc),
        )


async def _delete_media_async(object_name: str):
    """Async deletion of media from storage."""
    await storage_client.delete_file(object_name)

    # Also delete thumbnail if exists
    path_obj = Path(object_name)
    thumb_name = str(path_obj.with_name(f"{path_obj.stem}_thumb.webp"))
    try:
        await storage_client.delete_file(thumb_name)
    except Exception:
        pass  # Thumbnail might not exist
