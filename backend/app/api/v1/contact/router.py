# Module: api/v1/contact/router.py | Agent: backend-agent | Task: p43_backend_feedback
"""Contact form router — public POST endpoint and admin management endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.contact.repository import ContactRepository, SiteSettingsRepository
from app.api.v1.contact.schemas import (
    ContactFormRequest,
    ContactListResponse,
    ContactMessageRead,
    ContactReplyRequest,
    ContactStatus,
    SiteSettingsResponse,
    SiteSettingsUpdate,
)
from app.api.v1.contact.service import ContactService
from app.core.dependencies import require_admin
from app.db.models.contact import ContactMessage
from app.db.models.user import User
from app.db.session import get_db

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["Contact"])


# ── Dependency factories ─────────────────────────────────────────────────────

def get_contact_repo(session: AsyncSession = Depends(get_db)) -> ContactRepository:
    return ContactRepository(session)


def get_settings_repo(session: AsyncSession = Depends(get_db)) -> SiteSettingsRepository:
    return SiteSettingsRepository(session)


def get_contact_service(
    repo: ContactRepository = Depends(get_contact_repo),
    settings_repo: SiteSettingsRepository = Depends(get_settings_repo),
) -> ContactService:
    return ContactService(repo, settings_repo)


# ── Helper: decrypt and build response ──────────────────────────────────────

def _to_read(svc: ContactService, obj: ContactMessage) -> ContactMessageRead:
    return svc._decrypt_message(obj)


# ── Public endpoints ─────────────────────────────────────────────────────────

@router.post(
    "/contact",
    response_model=ContactMessageRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a contact form",
)
@limiter.limit("5/minute")
async def submit_contact(
    request: Request,
    data: ContactFormRequest,
    svc: ContactService = Depends(get_contact_service),
) -> ContactMessageRead:
    ip = request.client.host if request.client else "unknown"
    obj = await svc.submit_contact(data, ip)
    return svc._decrypt_message(obj)


# ── Admin endpoints ──────────────────────────────────────────────────────────

@router.get(
    "/admin/contact",
    response_model=ContactListResponse,
    summary="List contact messages (admin)",
)
async def list_contact_messages(
    msg_status: ContactStatus | None = None,
    cursor: uuid.UUID | None = None,
    limit: int = 20,
    svc: ContactService = Depends(get_contact_service),
    _admin: User = Depends(require_admin),
) -> ContactListResponse:
    if limit > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="limit must be <= 100",
        )
    return await svc.list_messages(msg_status, cursor, limit)


@router.get(
    "/admin/contact/{msg_id}",
    response_model=ContactMessageRead,
    summary="Get contact message and mark as READ (admin)",
)
async def get_contact_message(
    msg_id: uuid.UUID,
    svc: ContactService = Depends(get_contact_service),
    _admin: User = Depends(require_admin),
) -> ContactMessageRead:
    obj = await svc.get_message(msg_id)
    return svc._decrypt_message(obj)


@router.put(
    "/admin/contact/{msg_id}/reply",
    response_model=ContactMessageRead,
    summary="Update contact message status (admin)",
)
async def reply_contact_message(
    msg_id: uuid.UUID,
    body: ContactReplyRequest,
    svc: ContactService = Depends(get_contact_service),
    _admin: User = Depends(require_admin),
) -> ContactMessageRead:
    obj = await svc.update_message_status(msg_id, body.status)
    return svc._decrypt_message(obj)


@router.delete(
    "/admin/contact/{msg_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete contact message (admin)",
)
async def delete_contact_message(
    msg_id: uuid.UUID,
    svc: ContactService = Depends(get_contact_service),
    _admin: User = Depends(require_admin),
) -> Response:
    await svc.delete_message(msg_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── Admin settings ───────────────────────────────────────────────────────────

@router.get(
    "/admin/settings/contact",
    response_model=SiteSettingsResponse,
    summary="Get contact page settings (admin)",
)
async def get_contact_settings(
    svc: ContactService = Depends(get_contact_service),
    _admin: User = Depends(require_admin),
) -> SiteSettingsResponse:
    return await svc.get_contact_settings()


@router.put(
    "/admin/settings/contact",
    response_model=SiteSettingsResponse,
    summary="Update contact page settings (admin)",
)
async def update_contact_settings(
    data: SiteSettingsUpdate,
    svc: ContactService = Depends(get_contact_service),
    _admin: User = Depends(require_admin),
) -> SiteSettingsResponse:
    return await svc.update_contact_settings(data)
