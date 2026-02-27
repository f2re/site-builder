from datetime import timedelta
from miniopy_async import Minio
from app.core.config import settings

class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,  # Set to True if using SSL
        )
        self.bucket_name = settings.MINIO_BUCKET

    async def get_presigned_upload_url(self, object_name: str, expires: int = 15) -> str:
        """Get a presigned URL for uploading an object via PUT."""
        return await self.client.presigned_put_object(
            self.bucket_name,
            object_name,
            expires=timedelta(minutes=expires),
        )

    async def get_public_url(self, object_name: str) -> str:
        """Get the public URL for an object."""
        # This assumes the bucket is configured for public read access
        # or accessed via a proxy like Nginx as defined in plan.md
        return f"/media/{object_name}"

minio_client = MinioClient()
