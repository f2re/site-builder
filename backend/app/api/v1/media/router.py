# Module: media/router.py | Agent: backend-agent | Task: BE-02
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import uuid
from datetime import datetime, timezone
from typing import Optional
from PIL import Image
from io import BytesIO

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.integrations.local_storage import storage_client
from .service import MediaService

router = APIRouter(prefix="/media", tags=["Media"])


class UploadResponse(BaseModel):
    url: str
    width: int
    height: int


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    context: str = Form(...),
    alt: str = Form(""),
    entity_id: Optional[uuid.UUID] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload file directly to local storage.
    Handles multipart/form-data, saves to /media/ using storage_client.save_file,
    then starts tasks.process_image (Celery). Returns {url, width, height}.
    """
    # Generate unique object name
    filename = file.filename or "image.jpg"
    ext = filename.split('.')[-1] if '.' in filename else 'jpg'
    now = datetime.now(timezone.utc)
    object_name = f"{context}/{now.year}/{now.month:02d}/{uuid.uuid4()}.{ext}"

    # Read file content
    content = await file.read()
    size_bytes = len(content)
    
    # Calculate dimensions
    try:
        img = Image.open(BytesIO(content))
        width, height = img.size
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(e)}"
        )

    # Save to local storage
    await storage_client.save_file(
        object_name=object_name,
        data=content,
        content_type=file.content_type or "application/octet-stream",
    )

    # Create DB record and trigger Celery task
    service = MediaService(db)
    await service.create_media_record(
        object_name=object_name,
        alt=alt,
        context=context,
        width=width,
        height=height,
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=size_bytes,
        entity_id=entity_id,
    )

    public_url = storage_client.get_public_url(object_name)

    return UploadResponse(
        url=public_url,
        width=width,
        height=height,
    )


@router.delete("/{object_name:path}")
async def delete_media(
    object_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Removes file and DB record."""
    service = MediaService(db)
    await service.delete_media(object_name)
    return {"message": "Media deleted"}
