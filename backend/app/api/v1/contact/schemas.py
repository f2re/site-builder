# Module: api/v1/contact/schemas.py | Agent: backend-agent | Task: p43_backend_feedback
"""Pydantic schemas for the contact form feature."""
import enum
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactStatus(str, enum.Enum):
    NEW = "NEW"
    READ = "READ"
    REPLIED = "REPLIED"


class ContactFormRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)
    subject: str = Field(min_length=2, max_length=500)
    message: str = Field(min_length=10, max_length=5000)
    # Cloudflare Turnstile widget token — submitted by the frontend
    turnstile_token: str


class ContactMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    phone: str | None
    subject: str
    message: str
    status: ContactStatus
    ip_address: str
    created_at: datetime
    read_at: datetime | None


class ContactListResponse(BaseModel):
    items: list[ContactMessageRead]
    total: int
    next_cursor: uuid.UUID | None


class ContactReplyRequest(BaseModel):
    """Update message status. Only REPLIED is accepted via this endpoint."""
    status: ContactStatus


# ── Site Settings ────────────────────────────────────────────────────────────

class SiteSettingRead(BaseModel):
    key: str
    value: str | None


class SiteSettingsUpdate(BaseModel):
    contact_email: EmailStr | None = None
    contact_page_text: str | None = None


class SiteSettingsResponse(BaseModel):
    contact_email: str | None
    contact_page_text: str | None
