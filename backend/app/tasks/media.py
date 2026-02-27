"""Media processing tasks for Celery.

Handles image optimization, WebP conversion, thumbnail generation,
and dimension extraction for blog posts and product images.
"""
import asyncio
from io import BytesIO
from pathlib import Path
from typing import Literal

from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logging import logger
from app.integrations.minio import minio_client
from app.tasks.celery_app import celery_app


@celery_app.task(name="tasks.process_image", bind=True, max_retries=3)
def process_image(
    self,
    object_name: str,
    media_id: int,
    context: Literal["blog", "product"],
):
    """
    Process uploaded image:
    1. Download original from MinIO
    2. Extract real dimensions (width, height) via Pillow
    3. Convert to WebP (quality=85) for better compression
    4. Generate thumbnail (480px max dimension)
    5. Upload WebP + thumbnail back to MinIO
    6. Update database record with new URLs and dimensions
    7. Optionally delete original (configurable)
    
    Args:
        object_name: Path in MinIO bucket (e.g., 'blog/2026/02/image.jpg')
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
    bucket = settings.MINIO_BUCKET_MEDIA

    # 1. Download original from MinIO
    logger.info("downloading_from_minio", object_name=object_name)
    response = await minio_client.get_object(bucket, object_name)
    image_data = await response.read()
    await response.close()
    await response.release()

    # 2. Load image with Pillow and extract dimensions
    img = Image.open(BytesIO(image_data))
    original_format = img.format
    width, height = img.size
    logger.info(
        "image_dimensions_extracted",
        width=width,
        height=height,
        format=original_format,
    )

    # Convert RGBA to RGB if needed (WebP with transparency requires special handling)
    if img.mode in ("RGBA", "LA", "P"):
        # Create white background
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = background

    # 3. Convert to WebP (quality=85 is optimal balance)
    webp_buffer = BytesIO()
    img.save(webp_buffer, format="WEBP", quality=85, method=6)
    webp_buffer.seek(0)
    webp_size = len(webp_buffer.getvalue())

    # Generate WebP filename
    path_obj = Path(object_name)
    webp_name = str(path_obj.with_suffix(".webp"))

    logger.info(
        "uploading_webp",
        webp_name=webp_name,
        size_bytes=webp_size,
    )

    # Upload WebP to MinIO
    await minio_client.put_object(
        bucket,
        webp_name,
        webp_buffer,
        length=webp_size,
        content_type="image/webp",
    )

    # 4. Create thumbnail (max 480px on longest side)
    img.thumbnail((480, 480), Image.Resampling.LANCZOS)
    thumb_buffer = BytesIO()
    img.save(thumb_buffer, format="WEBP", quality=85, method=6)
    thumb_buffer.seek(0)
    thumb_size = len(thumb_buffer.getvalue())
    thumb_width, thumb_height = img.size

    thumb_name = str(path_obj.with_stem(f"{path_obj.stem}_thumb").with_suffix(".webp"))

    logger.info(
        "uploading_thumbnail",
        thumb_name=thumb_name,
        size_bytes=thumb_size,
        dimensions=f"{thumb_width}x{thumb_height}",
    )

    await minio_client.put_object(
        bucket,
        thumb_name,
        thumb_buffer,
        length=thumb_size,
        content_type="image/webp",
    )

    # 5. Update database record
    async with AsyncSessionLocal() as db:
        if context == "blog":
            from app.db.models.blog import BlogPostMedia

            stmt = select(BlogPostMedia).where(BlogPostMedia.id == media_id)
            result = await db.execute(stmt)
            media = result.scalar_one_or_none()

            if media:
                media.url = webp_name
                media.width = width
                media.height = height
                media.mime_type = "image/webp"
                media.size_bytes = webp_size
                await db.commit()
                logger.info("blog_media_updated", media_id=media_id)

        elif context == "product":
            from app.db.models.product import ProductImage

            stmt = select(ProductImage).where(ProductImage.id == media_id)
            result = await db.execute(stmt)
            media = result.scalar_one_or_none()

            if media:
                media.url = webp_name
                media.width = width
                media.height = height
                await db.commit()
                logger.info("product_image_updated", media_id=media_id)

    # 6. Optionally delete original (if not already WebP)
    if settings.MINIO_DELETE_ORIGINAL and original_format != "WEBP":
        try:
            await minio_client.remove_object(bucket, object_name)
            logger.info("original_image_deleted", object_name=object_name)
        except Exception as e:
            logger.warning(
                "original_deletion_failed",
                object_name=object_name,
                error=str(e),
            )


@celery_app.task(name="tasks.delete_media_from_storage")
def delete_media_from_storage(object_name: str):
    """
    Delete media file from MinIO storage.
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
    """Async deletion of media from MinIO."""
    bucket = settings.MINIO_BUCKET_MEDIA
    await minio_client.remove_object(bucket, object_name)

    # Also delete thumbnail if exists
    path_obj = Path(object_name)
    thumb_name = str(path_obj.with_stem(f"{path_obj.stem}_thumb"))
    try:
        await minio_client.remove_object(bucket, thumb_name)
    except Exception:
        pass  # Thumbnail might not exist
