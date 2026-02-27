from pydantic import BaseModel
from typing import Literal

class UploadUrlRequest(BaseModel):
    filename: str
    content_type: str
    context: Literal["blog", "product"]

class UploadUrlResponse(BaseModel):
    upload_url: str
    object_name: str
    public_url: str

class ConfirmUploadRequest(BaseModel):
    object_name: str
    alt: str
    context: Literal["blog", "product"]
    entity_id: str  # UUID or int depending on context
