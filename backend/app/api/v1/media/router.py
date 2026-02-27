"""Media upload and management API endpoints.

Provides presigned URLs for direct browser → MinIO uploads,
confirmation endpoint to trigger Celery image processing,
and media deletion.
"""
from datetime import datetime
from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.media.schemas import (
    MediaConfirmRequest,
    MediaConfirmResponse,
    UploadUrlRequest,
    UploadUrlResponse,
)
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.logging import logger
from app.db.models.user import User
from app.integrations.minio import minio_client
from app.tasks.media import process_image

router = APIRouter()


@router.post("/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(
    request: UploadUrlRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate presigned upload URL for direct browser → MinIO upload.
    
    Flow:
    1. Client calls this endpoint with filename and context
    2. Backend generates unique object path and presigned PUT URL
    3. Client uploads file directly to MinIO using PUT request
    4. Client calls /media/confirm to trigger processing
    
    Requires authentication.
    """
    # Generate unique filename to prevent collisions
    ext = Path(request.filename).suffix.lower()
    
    # Validate extension
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}",
        )
    
    # Generate path: {context}/{year}/{month}/{uuid}{ext}
    now = datetime.utcnow()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    object_name = f"{request.context}/{now.year}/{now.month:02d}/{unique_name}"
    
    logger.info(
        "generating_upload_url",
        user_id=current_user.id,
        context=request.context,
        object_name=object_name,
    )
    
    # Get presigned URL (15 min expiration)
    upload_url = await minio_client.get_presigned_upload_url(
        object_name=object_name,
        expires=15,
    )
    
    public_url = minio_client.get_public_url(object_name)
    
    return UploadUrlResponse(
        upload_url=upload_url,
        object_name=object_name,
        public_url=public_url,
        expires_in=15,
    )


@router.post("/confirm", response_model=MediaConfirmResponse)
async def confirm_upload(
    request: MediaConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm successful upload and trigger image processing.
    
    Creates database record (BlogPostMedia or ProductImage)
    and launches Celery task for WebP conversion, thumbnail generation,
    and dimension extraction.
    
    Requires authentication.
    """
    logger.info(
        "confirming_upload",
        user_id=current_user.id,
        object_name=request.object_name,
        context=request.context,
    )
    
    # Create database record based on context
    if request.context == "blog":
        from app.db.models.blog import BlogPostMedia
        
        media = BlogPostMedia(
            post_id=request.entity_id,  # Can be None for new posts
            url=request.object_name,  # Will be updated to .webp by Celery
            media_type="image",
            alt=request.alt,
            caption=request.caption,
            mime_type="image/jpeg",  # Will be updated by Celery
            size_bytes=0,  # Will be updated by Celery
            sort_order=0,
        )
        db.add(media)
        await db.commit()
        await db.refresh(media)
        media_id = media.id
        
    elif request.context == "product":
        from app.db.models.product import ProductImage
        
        if not request.entity_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="entity_id (product_id) is required for product images",
            )
        
        media = ProductImage(
            product_id=request.entity_id,
            url=request.object_name,  # Will be updated to .webp
            alt=request.alt,
            is_cover=False,
            sort_order=0,
        )
        db.add(media)
        await db.commit()
        await db.refresh(media)
        media_id = media.id
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid context",
        )
    
    # Launch Celery task for image processing
    process_image.delay(
        object_name=request.object_name,
        media_id=media_id,
        context=request.context,
    )
    
    logger.info(
        "upload_confirmed",
        media_id=media_id,
        context=request.context,
    )
    
    return MediaConfirmResponse(
        media_id=media_id,
        status="processing",
        message="Image uploaded successfully. Processing in background.",
    )
