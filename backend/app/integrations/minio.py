"""MinIO/S3 integration for media storage.

Provides async methods for uploading, downloading, and managing media files.
Used by media processing tasks and API endpoints.
"""
from datetime import timedelta
from io import BytesIO

from miniopy_async import Minio

from app.core.config import settings
from app.core.logging import logger


class MinioClient:
    """Async MinIO client wrapper."""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        self.bucket_name = settings.MINIO_BUCKET
        self.media_bucket = settings.MINIO_BUCKET_MEDIA

    async def ensure_bucket_exists(self, bucket_name: str):
        """Create bucket if it doesn't exist."""
        try:
            exists = await self.client.bucket_exists(bucket_name)
            if not exists:
                await self.client.make_bucket(bucket_name)
                logger.info("minio_bucket_created", bucket=bucket_name)
        except Exception as e:
            logger.error("minio_bucket_check_failed", bucket=bucket_name, error=str(e))
            raise

    async def get_presigned_upload_url(
        self,
        object_name: str,
        bucket: str | None = None,
        expires: int = 15,
    ) -> str:
        """Get a presigned URL for uploading an object via PUT.
        
        Args:
            object_name: Path in bucket (e.g., 'blog/2026/02/image.jpg')
            bucket: Bucket name (defaults to media bucket)
            expires: URL expiration in minutes (default 15)
            
        Returns:
            Presigned PUT URL for direct browser upload
        """
        bucket = bucket or self.media_bucket
        await self.ensure_bucket_exists(bucket)
        
        return await self.client.presigned_put_object(
            bucket,
            object_name,
            expires=timedelta(minutes=expires),
        )

    async def get_presigned_download_url(
        self,
        object_name: str,
        bucket: str | None = None,
        expires: int = 60,
    ) -> str:
        """Get a presigned URL for downloading an object.
        
        Args:
            object_name: Path in bucket
            bucket: Bucket name (defaults to media bucket)
            expires: URL expiration in minutes (default 60)
            
        Returns:
            Presigned GET URL
        """
        bucket = bucket or self.media_bucket
        return await self.client.presigned_get_object(
            bucket,
            object_name,
            expires=timedelta(minutes=expires),
        )

    async def get_object(self, bucket: str, object_name: str):
        """Download object from MinIO.
        
        Returns:
            HTTP response object with .read(), .close(), .release() methods
        """
        return await self.client.get_object(bucket, object_name)

    async def put_object(
        self,
        bucket: str,
        object_name: str,
        data: BytesIO,
        length: int,
        content_type: str = "application/octet-stream",
    ):
        """Upload object to MinIO.
        
        Args:
            bucket: Bucket name
            object_name: Path in bucket
            data: BytesIO buffer with file content
            length: Size in bytes
            content_type: MIME type (e.g., 'image/webp')
        """
        await self.ensure_bucket_exists(bucket)
        await self.client.put_object(
            bucket,
            object_name,
            data,
            length=length,
            content_type=content_type,
        )

    async def remove_object(self, bucket: str, object_name: str):
        """Delete object from MinIO.
        
        Args:
            bucket: Bucket name
            object_name: Path in bucket
        """
        await self.client.remove_object(bucket, object_name)

    async def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        recursive: bool = True,
    ):
        """List objects in bucket.
        
        Args:
            bucket: Bucket name
            prefix: Filter by prefix (e.g., 'blog/2026/')
            recursive: Include subdirectories
            
        Returns:
            Async generator of object metadata
        """
        return self.client.list_objects(
            bucket,
            prefix=prefix,
            recursive=recursive,
        )

    def get_public_url(self, object_name: str) -> str:
        """Get the public URL for an object.
        
        Assumes Nginx proxies /media/* to MinIO or CDN is configured.
        For production, use settings.MINIO_PUBLIC_DOMAIN.
        
        Args:
            object_name: Path in bucket (without leading slash)
            
        Returns:
            Public URL (e.g., 'https://media.wifiobd.shop/blog/image.webp')
        """
        if settings.MINIO_USE_SSL and settings.MINIO_PUBLIC_DOMAIN:
            return f"https://{settings.MINIO_PUBLIC_DOMAIN}/{object_name}"
        return f"/media/{object_name}"


minio_client = MinioClient()
