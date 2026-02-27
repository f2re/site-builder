from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import uuid
from typing import Optional

from app.db.models.blog import BlogPostMedia
from app.tasks.media import process_image

logger = structlog.get_logger()


class MediaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def confirm_upload(
        self,
        object_name: str,
        alt: str,
        context: str,
        entity_id: Optional[uuid.UUID],
    ):
        """Confirm upload and create DB record, trigger Celery processing."""
        # Create media record
        if context == "blog":
            media = BlogPostMedia(
                post_id=entity_id,
                url=object_name,
                media_type="image",
                alt=alt,
                mime_type="image/jpeg",  # Will be updated by Celery
                size_bytes=0, # Will be updated by Celery
            )
            self.db.add(media)
            await self.db.commit()
            await self.db.refresh(media)

            # Trigger Celery processing (async, fire-and-forget)
            # context determines which model to update in process_image
            process_image.delay(object_name, media.id, context="blog")

            logger.info("media_upload_confirmed", media_id=str(media.id), object_name=object_name)
            return media
        else:
            # TODO: Handle product images
            raise NotImplementedError("Product images not yet implemented")
