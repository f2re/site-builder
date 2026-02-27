from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import uuid
from datetime import datetime

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.integrations.minio import (
    get_presigned_upload_url,
    get_public_url,
)
from .service import MediaService

router = APIRouter(prefix="/media", tags=["Media"])


class UploadUrlRequest(BaseModel):
    filename: str
    content_type: str
    context: str  # "blog" | "product"


class UploadUrlResponse(BaseModel):
    upload_url: str
    object_name: str
    public_url: str


class ConfirmUploadRequest(BaseModel):
    object_name: str
    alt: str
    context: str
    entity_id: int | None = None


@router.post("/upload-url", response_model=UploadUrlResponse)
async def request_upload_url(
    data: UploadUrlRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate presigned MinIO upload URL for direct browser upload."""
    # Generate unique object name
    ext = data.filename.split('.')[-1] if '.' in data.filename else 'jpg'
    now = datetime.utcnow()
    object_name = f"{data.context}/{now.year}/{now.month:02d}/{uuid.uuid4()}.{ext}"

    # Get presigned URL (15 min expiry)
    upload_url = await get_presigned_upload_url(object_name, data.content_type)
    public_url = await get_public_url(object_name)

    return UploadUrlResponse(
        upload_url=upload_url,
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

    return {"message": "Upload confirmed", "media_id": media.id}
