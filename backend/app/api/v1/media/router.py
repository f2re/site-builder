from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.integrations.local_storage import storage_client
from .service import MediaService

router = APIRouter(prefix="/media", tags=["Media"])


class UploadResponse(BaseModel):
    object_name: str
    public_url: str


class ConfirmUploadRequest(BaseModel):
    object_name: str
    alt: str
    context: str
    entity_id: Optional[uuid.UUID] = None


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    context: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    """Upload file directly to local storage."""
    # Generate unique object name
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    now = datetime.utcnow()
    object_name = f"{context}/{now.year}/{now.month:02d}/{uuid.uuid4()}.{ext}"

    # Read and save file
    content = await file.read()
    await storage_client.save_file(
        object_name=object_name,
        data=content,
        content_type=file.content_type,
    )

    public_url = storage_client.get_public_url(object_name)

    return UploadResponse(
        object_name=object_name,
        public_url=public_url,
    )


@router.post("/confirm")
async def confirm_upload(
    data: ConfirmUploadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Confirm upload and trigger Celery processing."""
    service = MediaService(db)
    
    media = await service.confirm_upload(
        object_name=data.object_name,
        alt=data.alt,
        context=data.context,
        entity_id=data.entity_id,
    )

    return {"message": "Upload confirmed", "media_id": str(media.id)}
