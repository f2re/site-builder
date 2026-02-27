import uuid
from fastapi import APIRouter, Depends, status
from app.api.v1.media.schemas import UploadUrlRequest, UploadUrlResponse, ConfirmUploadRequest
from app.integrations.minio import minio_client
from app.core.dependencies import require_admin
from app.db.models.user import User

router = APIRouter(prefix="/media", tags=["Media"])

@router.post("/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(
    body: UploadUrlRequest,
    _admin: User = Depends(require_admin)
):
    """
    Generate a presigned URL for direct upload to MinIO.
    """
    ext = body.filename.split(".")[-1]
    object_name = f"{body.context}/{uuid.uuid4()}.{ext}"
    
    upload_url = await minio_client.get_presigned_upload_url(object_name)
    public_url = await minio_client.get_public_url(object_name)
    
    return UploadUrlResponse(
        upload_url=upload_url,
        object_name=object_name,
        public_url=public_url
    )

@router.post("/confirm", status_code=status.HTTP_201_CREATED)
async def confirm_upload(
    body: ConfirmUploadRequest,
    _admin: User = Depends(require_admin)
):
    """
    Confirm upload completion and trigger background processing.
    TODO: Create DB entry and trigger Celery task 'tasks.process_image'.
    """
    return {"status": "confirmed", "object_name": body.object_name}
