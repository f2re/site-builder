"""Local storage integration for media files.

Provides async methods for saving, reading, and managing media files
using aiofiles and local filesystem.
"""
import os
import aiofiles
from pathlib import Path
from io import BytesIO
from app.core.config import settings
from app.core.logging import logger

class LocalStorageClient:
    """Async local storage client."""

    def __init__(self):
        self.media_root = Path(settings.MEDIA_ROOT)
        self.media_url = settings.MEDIA_URL

    async def ensure_directory_exists(self, object_name: str):
        """Create directory for object if it doesn't exist."""
        file_path = self.media_root / object_name
        file_path.parent.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        object_name: str,
        data: bytes | BytesIO,
        content_type: str = "application/octet-stream",
    ):
        """Save file to local storage.
        
        Args:
            object_name: Path relative to MEDIA_ROOT
            data: file content (bytes or BytesIO)
            content_type: MIME type (optional, for compatibility)
        """
        await self.ensure_directory_exists(object_name)
        file_path = self.media_root / object_name
        
        if isinstance(data, BytesIO):
            content = data.getvalue()
        else:
            content = data

        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(content)
        
        logger.info("file_saved_locally", path=str(file_path))

    async def read_file(self, object_name: str) -> bytes:
        """Read file from local storage."""
        file_path = self.media_root / object_name
        async with aiofiles.open(file_path, mode='rb') as f:
            return await f.read()

    async def delete_file(self, object_name: str):
        """Delete file from local storage."""
        file_path = self.media_root / object_name
        if file_path.exists():
            os.remove(file_path)
            logger.info("file_deleted_locally", path=str(file_path))

    def get_public_url(self, object_name: str) -> str:
        """Get the public URL for an object."""
        # Ensure object_name doesn't start with /
        clean_name = object_name.lstrip("/")
        return f"{self.media_url}/{clean_name}"

storage_client = LocalStorageClient()
