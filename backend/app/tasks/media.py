"""Media processing tasks for Celery.

Handles image optimization, WebP conversion, thumbnail generation,
and dimension extraction for blog posts and product images.
"""
from io import BytesIO
from pathlib import Path
from typing import Literal, Any, cast

from PIL import Image, ImageOps
from sqlalchemy import select

from app.core.logging import logger
from app.core.utils import run_async
from app.db.celery_session import CelerySessionLocal
from app.integrations.local_storage import storage_client
from app.tasks.celery_app import celery_app


def _smart_resize(img: Any, target_size: int) -> tuple[Any, bool]:
    """Smart resize without upscaling.

    Args:
        img: PIL Image object
        target_size: Target size for longest dimension

    Returns:
        Tuple of (resized_image, was_resized)
    """
    width, height = img.size
    longest = max(width, height)

    # Don't upscale if image is smaller than target
    if longest <= target_size:
        return img, False

    # Calculate new dimensions maintaining aspect ratio
    if width > height:
        new_width = target_size
        new_height = int(height * (target_size / width))
    else:
        new_height = target_size
        new_width = int(width * (target_size / height))

    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return resized, True


def _generate_thumb_crop(img: Any, size: int = 150) -> Any:
    """Generate centered square crop thumbnail.

    Args:
        img: PIL Image object
        size: Square size (default 150x150)

    Returns:
        Cropped PIL Image
    """
    return ImageOps.fit(img, (size, size), Image.Resampling.LANCZOS, centering=(0.5, 0.5))


@celery_app.task(name="tasks.process_image_variants", bind=True, max_retries=3)
def process_image_variants(
    self,
    source_path: str,
    entity_type: Literal["product", "blog"],
    entity_id: str,
    sequence: int,
    image_id: str,
):
    """
    Process uploaded image and generate multiple size variants.

    Generates 5 sizes:
    - original: max 1920px (no upscaling)
    - large: 1024px
    - medium: 480px
    - small: 320px
    - thumb: 150x150 (centered square crop)

    All variants saved as WebP (quality=85).
    Updates ProductImage.formats or BlogPostMedia.formats with paths.

    Args:
        source_path: Path to source image in storage
        entity_type: 'product' or 'blog'
        entity_id: UUID of product or blog post
        sequence: Sequence number (e.g., 1, 2, 3)
        image_id: UUID of ProductImage or BlogPostMedia record
    """
    try:
        logger.info(
            "processing_image_variants_start",
            source_path=source_path,
            entity_type=entity_type,
            entity_id=entity_id,
            sequence=sequence,
            image_id=image_id,
        )

        run_async(
            _process_image_variants_async(
                source_path, entity_type, entity_id, sequence, image_id
            )
        )

        logger.info(
            "processing_image_variants_complete",
            entity_type=entity_type,
            entity_id=entity_id,
            sequence=sequence,
        )

    except Exception as exc:
        logger.error(
            "processing_image_variants_failed",
            source_path=source_path,
            entity_type=entity_type,
            entity_id=entity_id,
            error=str(exc),
            retry_count=self.request.retries,
        )
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


async def _process_image_variants_async(
    source_path: str,
    entity_type: Literal["product", "blog"],
    entity_id: str,
    sequence: int,
    image_id: str,
):
    """Async implementation of multi-size image processing."""
    # 1. Read source image
    logger.info("reading_source_image", source_path=source_path)
    image_data = await storage_client.read_file(source_path)

    # 2. Load with Pillow
    img = cast(Any, Image.open(BytesIO(image_data)))
    original_width, original_height = img.size
    logger.info(
        "source_image_loaded",
        width=original_width,
        height=original_height,
        format=img.format,
    )

    # Convert RGBA/LA/P to RGB
    if img.mode in ("RGBA", "LA", "P"):
        background = cast(Any, Image.new("RGB", img.size, (255, 255, 255)))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = background

    # 3. Define size variants
    sizes = {
        "original": 1920,
        "large": 1024,
        "medium": 480,
        "small": 320,
    }

    # Base path pattern: media/{entity_type}/{entity_id}/{seq}
    base_dir = f"media/{entity_type}/{entity_id}"
    seq_str = f"{sequence:03d}"  # 001, 002, etc.

    formats_dict = {}

    # 4. Generate standard sizes
    for size_name, target_px in sizes.items():
        resized_img, was_resized = _smart_resize(img.copy(), target_px)

        # Determine filename
        if size_name == "original":
            filename = f"{seq_str}.webp"
        else:
            filename = f"{seq_str}_{size_name}.webp"

        full_path = f"{base_dir}/{filename}"

        # Save as WebP
        buffer = BytesIO()
        resized_img.save(buffer, format="WEBP", quality=85, method=6)
        buffer.seek(0)
        webp_bytes = buffer.getvalue()

        await storage_client.save_file(
            full_path,
            webp_bytes,
            content_type="image/webp",
        )

        w, h = resized_img.size
        logger.info(
            "variant_saved",
            size=size_name,
            path=full_path,
            dimensions=f"{w}x{h}",
            bytes=len(webp_bytes),
            was_resized=was_resized,
        )

        formats_dict[size_name] = full_path

    # 5. Generate thumb (150x150 crop)
    thumb_img = _generate_thumb_crop(img.copy(), 150)
    thumb_filename = f"{seq_str}_thumb.webp"
    thumb_path = f"{base_dir}/{thumb_filename}"

    thumb_buffer = BytesIO()
    thumb_img.save(thumb_buffer, format="WEBP", quality=85, method=6)
    thumb_buffer.seek(0)
    thumb_bytes = thumb_buffer.getvalue()

    await storage_client.save_file(
        thumb_path,
        thumb_bytes,
        content_type="image/webp",
    )

    logger.info(
        "variant_saved",
        size="thumb",
        path=thumb_path,
        dimensions="150x150",
        bytes=len(thumb_bytes),
        was_resized=True,
    )

    formats_dict["thumb"] = thumb_path

    # 6. Update database record
    async with CelerySessionLocal() as db:
        if entity_type == "product":
            from app.db.models.product import ProductImage

            stmt_prod = select(ProductImage).where(ProductImage.id == image_id)
            result_prod = await db.execute(stmt_prod)
            media_prod = result_prod.scalar_one_or_none()

            if media_prod:
                media_prod.base_path = base_dir
                media_prod.formats = formats_dict
                media_prod.width = original_width
                media_prod.height = original_height
                await db.commit()
                logger.info("product_image_formats_updated", image_id=image_id)

        elif entity_type == "blog":
            from app.db.models.blog import BlogPostMedia

            stmt_blog = select(BlogPostMedia).where(BlogPostMedia.id == image_id)
            result_blog = await db.execute(stmt_blog)
            media_blog = result_blog.scalar_one_or_none()

            if media_blog:
                media_blog.base_path = base_dir
                media_blog.formats = formats_dict
                media_blog.width = original_width
                media_blog.height = original_height
                media_blog.mime_type = "image/webp"
                await db.commit()
                logger.info("blog_media_formats_updated", image_id=image_id)

    # 7. Optionally delete source (if configured)
    # Note: KEEP_ORIGINAL setting not implemented yet, keeping source for now
    logger.info("image_variants_processing_complete", formats=list(formats_dict.keys()))


@celery_app.task(name="tasks.process_image", bind=True, max_retries=3)
def process_image(
    self,
    object_name: str,
    media_id: int,
    context: Literal["blog", "product"] = "blog",
):
    """
    DEPRECATED: Use process_image_variants instead.
    This task is kept for backward compatibility only.

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
        run_async(_process_image_async(object_name, media_id, context))

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
        run_async(_delete_media_async(object_name))
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
