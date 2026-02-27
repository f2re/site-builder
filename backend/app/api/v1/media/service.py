from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
import uuid
from typing import Optional

from app.db.models.blog import BlogPostMedia
from app.tasks.media import process_image, delete_media_from_storage

logger = structlog.get_logger()


class MediaService:
    def __init__(self, db: AsyncSession):
        self.db = db

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
    ) -> BlogPostMedia:
        """Create media record and trigger Celery processing."""
        if context == "blog":
            media = BlogPostMedia(
                post_id=entity_id,
                url=object_name,
                media_type="image",
                alt=alt,
                width=width,
                height=height,
                mime_type=mime_type,
                size_bytes=size_bytes,
            )
            self.db.add(media)
            await self.db.commit()
            await self.db.refresh(media)

            # Trigger Celery processing (async, fire-and-forget)
            process_image.delay(object_name, media.id, context="blog")

            logger.info("media_record_created", media_id=str(media.id), object_name=object_name)
            return media
        else:
            # TODO: Handle product images
            raise NotImplementedError("Product images not yet implemented")

    async def delete_media(self, object_name: str):
        """Delete media record and trigger file deletion."""
        # Check blog media
        stmt = select(BlogPostMedia).where(BlogPostMedia.url == object_name)
        result = await self.db.execute(stmt)
        media = result.scalar_one_or_none()

        if media:
            await self.db.delete(media)
            await self.db.commit()
            logger.info("media_record_deleted", object_name=object_name)

        # Trigger Celery task to delete file from storage
        delete_media_from_storage.delay(object_name)
