# Module: api/v1/pages/schemas.py | Agent: backend-agent | Task: p12_backend_001
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class PageBase(BaseModel):
    slug: Optional[str] = Field(None, max_length=255)
    title: str = Field(..., max_length=255)
    content: str
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class PageCreate(PageBase):
    pass


class PageUpdate(BaseModel):
    slug: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class PageRead(PageBase):
    id: UUID
    slug: str  # Mandatory in Read
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RedirectRead(BaseModel):
    id: int
    old_path: str
    new_path: str
    status_code: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
