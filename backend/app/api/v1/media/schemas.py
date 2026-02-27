"""Media API schemas for upload and confirmation."""
from pydantic import BaseModel, Field
from typing import Literal


class UploadUrlRequest(BaseModel):
    """Request presigned upload URL from MinIO."""
    
    filename: str = Field(..., description="Original filename with extension")
    content_type: str = Field(..., description="MIME type (e.g., 'image/jpeg')")
    context: Literal["blog", "product"] = Field(
        ...,
        description="Upload context: 'blog' for blog posts, 'product' for product images",
    )


class UploadUrlResponse(BaseModel):
    """Response with presigned upload URL."""
    
    upload_url: str = Field(..., description="Presigned PUT URL for direct upload")
    object_name: str = Field(..., description="Generated object path in MinIO")
    public_url: str = Field(
        ...,
        description="Future public URL (available after processing)",
    )
    expires_in: int = Field(default=15, description="URL expiration in minutes")


class MediaConfirmRequest(BaseModel):
    """Confirm successful upload and trigger processing."""
    
    object_name: str = Field(..., description="Object path from upload response")
    alt: str = Field(..., description="Alt text for accessibility and SEO")
    context: Literal["blog", "product"] = Field(..., description="Upload context")
    entity_id: int | None = Field(
        None,
        description="ID of BlogPost or Product (optional for new entities)",
    )
    caption: str | None = Field(None, description="Image caption (blog only)")


class MediaConfirmResponse(BaseModel):
    """Response after confirming upload."""
    
    media_id: int = Field(..., description="ID of created BlogPostMedia or ProductImage")
    status: str = Field(
        default="processing",
        description="Processing status: 'processing' or 'completed'",
    )
    message: str = Field(
        default="Image is being processed",
        description="Human-readable status message",
    )
