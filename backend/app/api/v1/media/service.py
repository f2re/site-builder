# Module: api/v1/media/service.py | Agent: backend-agent | Task: p3_backend_image_upload_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog
import uuid
from typing import Optional, Literal

from app.db.models.blog import BlogPostMedia
from app.db.models.product import ProductImage
from app.tasks.media import process_image_variants, delete_media_from_storage
from app.integrations.local_storage import storage_client

logger = structlog.get_logger()


class MediaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _generate_next_sequence(
        self,
        entity_type: Literal["product", "blog"],
        entity_id: uuid.UUID
    ) -> int:
        """Generate next sequence number for image.

        Args:
            entity_type: 'product' or 'blog'
            entity_id: UUID of product or blog post

        Returns:
            Next sequence number (1 if no images exist)
        """
        if entity_type == "product":
            stmt = select(func.max(ProductImage.sequence)).where(
                ProductImage.product_id == entity_id
            )
        else:  # blog
            stmt = select(func.max(BlogPostMedia.sequence)).where(
                BlogPostMedia.post_id == entity_id
            )

        result = await self.db.execute(stmt)
        max_seq = result.scalar_one_or_none()

        return (max_seq or 0) + 1

    async def _delete_all_variants(self, formats: dict) -> None:
        """Delete all image variants from storage.

        Args:
            formats: Dictionary mapping size names to file paths
        """
        for size_name, file_path in formats.items():
            try:
                await storage_client.delete_file(file_path)
                logger.info("variant_deleted", size=size_name, path=file_path)
            except Exception as exc:
                logger.warning(
                    "variant_deletion_failed",
                    size=size_name,
                    path=file_path,
                    error=str(exc)
                )

    async def create_media_record(
        self,
        object_name: str,
        alt: str,
        context: str,
        width: int,
        height: int,
        mime_type: str,
        size_bytes: int,
        entity_id: Optional[uuid.UUID] = None,
    ) -> Optional[BlogPostMedia]:
        """Create media record and trigger Celery processing with multi-size variants."""
        if context == "blog":
            if not entity_id:
                raise ValueError("entity_id is required for blog context")

            # Generate sequence
            sequence = await self._generate_next_sequence("blog", entity_id)

            # Note: For blog uploads, object_name is already in storage
            # Celery task will process it directly

            media = BlogPostMedia(
                post_id=entity_id,
                url=object_name,  # Keep for backward compatibility
                media_type="image",
                alt=alt,
                width=width,
                height=height,
                mime_type=mime_type,
                size_bytes=size_bytes,
                sequence=sequence,
                base_path="",  # Will be filled by Celery task
                formats={},  # Will be filled by Celery task
            )
            self.db.add(media)
            await self.db.commit()
            await self.db.refresh(media)

            # Trigger Celery processing with new task
            process_image_variants.delay(
                object_name,  # source_path
                "blog",
                str(entity_id),
                sequence,
                str(media.id)
            )

            logger.info(
                "media_record_created",
                media_id=str(media.id),
                sequence=sequence,
                object_name=object_name
            )
            return media
        else:
            # For non-blog contexts (products, etc.) — handled by ProductService
            return None

    async def delete_media(self, object_name: str):
        """Delete media record and all image variants from storage."""
        # Check blog media
        stmt = select(BlogPostMedia).where(BlogPostMedia.url == object_name)
        result = await self.db.execute(stmt)
        media = result.scalar_one_or_none()

        if media:
            # Delete all variants if formats is populated
            if media.formats:
                await self._delete_all_variants(media.formats)
            elif media.url:
                # Backward compatibility: delete single file
                delete_media_from_storage.delay(media.url)

            await self.db.delete(media)
            await self.db.commit()
            logger.info("media_record_deleted", object_name=object_name)
        else:
            # No DB record, just delete file (backward compatibility)
            delete_media_from_storage.delay(object_name)
