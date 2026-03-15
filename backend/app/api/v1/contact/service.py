# Module: api/v1/contact/service.py | Agent: backend-agent | Task: p43_backend_feedback
"""Business logic layer for the contact form feature."""
import uuid

import httpx
from fastapi import HTTPException, status

from app.api.v1.contact.repository import ContactRepository, SiteSettingsRepository
from app.api.v1.contact.schemas import (
    ContactFormRequest,
    ContactListResponse,
    ContactMessageRead,
    ContactStatus,
    SiteSettingsResponse,
    SiteSettingsUpdate,
)
from app.core.config import settings
from app.core.logging import logger
from app.core.security import decrypt_data, encrypt_data
from app.db.models.contact import ContactMessage
from app.db.models.contact import ContactStatus as ModelContactStatus


class ContactService:
    def __init__(
        self,
        repo: ContactRepository,
        settings_repo: SiteSettingsRepository,
    ) -> None:
        self.repo = repo
        self.settings_repo = settings_repo

    # ── SmartCaptcha ─────────────────────────────────────────────────────────

    async def verify_captcha(self, token: str, ip: str) -> bool:
        """Verify a Yandex SmartCaptcha token server-side.

        If SMARTCAPTCHA_SECRET_KEY is empty (dev environment) — skip verification
        and return True so developers can test without a real key.
        """
        if not settings.SMARTCAPTCHA_SECRET_KEY:
            logger.info("smartcaptcha_skip_dev_mode", ip=ip)
            return True

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    "https://smartcaptcha.yandexcloud.net/validate",
                    data={
                        "secret": settings.SMARTCAPTCHA_SECRET_KEY,
                        "token": token,
                        "ip": ip,
                    },
                )
                result = resp.json()
                return result.get("status") == "ok"
        except Exception as exc:
            logger.warning("smartcaptcha_verification_error", error=str(exc))
            return False

    # ── Public ───────────────────────────────────────────────────────────────

    async def submit_contact(
        self, data: ContactFormRequest, ip: str
    ) -> ContactMessage:
        """Validate, persist, and notify about a new contact form submission."""
        valid = await self.verify_captcha(data.captcha_token, ip)
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Captcha verification failed. Please try again.",
            )

        # Encrypt PII fields before storing
        record_data: dict = {
            "name": encrypt_data(data.name),
            "email": encrypt_data(data.email),
            "phone": encrypt_data(data.phone) if data.phone else None,
            "subject": data.subject,
            "message": data.message,
            "ip_address": ip,
        }

        obj = await self.repo.create(record_data)
        await self.repo.session.commit()
        await self.repo.session.refresh(obj)

        # Resolve recipient: SiteSettings → fallback to config
        recipient = await self.settings_repo.get("contact_email")
        if not recipient:
            recipient = settings.CONTACT_EMAIL_RECIPIENT

        if recipient:
            try:
                # Import here to avoid circular imports at module load time
                from app.tasks.notifications.dispatcher import (
                    send_contact_notification_task,
                )

                send_contact_notification_task.delay(
                    recipient=recipient,
                    sender_name=data.name,
                    sender_email=data.email,
                    subject=data.subject,
                    message=data.message,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("contact_notification_enqueue_error", error=str(exc))

        return obj

    # ── Admin ────────────────────────────────────────────────────────────────

    async def get_message(self, msg_id: uuid.UUID) -> ContactMessage:
        obj = await self.repo.mark_read(msg_id)
        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact message not found.",
            )
        await self.repo.session.commit()
        await self.repo.session.refresh(obj)
        return obj

    async def list_messages(
        self,
        msg_status: ContactStatus | None,
        cursor: uuid.UUID | None,
        limit: int,
    ) -> ContactListResponse:
        model_status = ModelContactStatus(msg_status.value) if msg_status is not None else None
        items, total = await self.repo.list_messages(model_status, cursor, limit)
        next_cursor: uuid.UUID | None = None
        if len(items) == limit:
            next_cursor = items[-1].id

        # Decrypt PII fields before returning
        readable: list[ContactMessageRead] = []
        for m in items:
            readable.append(
                ContactMessageRead(
                    id=m.id,
                    name=decrypt_data(m.name),
                    email=decrypt_data(m.email),
                    phone=decrypt_data(m.phone) if m.phone else None,
                    subject=m.subject,
                    message=m.message,
                    status=ContactStatus(m.status.value),
                    ip_address=m.ip_address,
                    created_at=m.created_at,
                    read_at=m.read_at,
                )
            )
        return ContactListResponse(items=readable, total=total, next_cursor=next_cursor)

    async def update_message_status(
        self, msg_id: uuid.UUID, status_val: ContactStatus
    ) -> ContactMessage:
        obj = await self.repo.update_status(msg_id, ModelContactStatus(status_val.value))
        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact message not found.",
            )
        await self.repo.session.commit()
        await self.repo.session.refresh(obj)
        return obj

    async def delete_message(self, msg_id: uuid.UUID) -> None:
        deleted = await self.repo.delete(msg_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact message not found.",
            )
        await self.repo.session.commit()

    # ── Settings ─────────────────────────────────────────────────────────────

    async def get_contact_settings(self) -> SiteSettingsResponse:
        data = await self.settings_repo.get_contact_settings()
        return SiteSettingsResponse(
            contact_email=data.get("contact_email"),
            contact_page_text=data.get("contact_page_text"),
        )

    async def update_contact_settings(
        self, data: SiteSettingsUpdate
    ) -> SiteSettingsResponse:
        if data.contact_email is not None:
            await self.settings_repo.set("contact_email", str(data.contact_email))
        if data.contact_page_text is not None:
            await self.settings_repo.set("contact_page_text", data.contact_page_text)
        await self.repo.session.commit()
        return await self.get_contact_settings()

    # ── Helper: decrypt single message ───────────────────────────────────────

    def _decrypt_message(self, obj: ContactMessage) -> ContactMessageRead:
        return ContactMessageRead(
            id=obj.id,
            name=decrypt_data(obj.name),
            email=decrypt_data(obj.email),
            phone=decrypt_data(obj.phone) if obj.phone else None,
            subject=obj.subject,
            message=obj.message,
            status=ContactStatus(obj.status.value),
            ip_address=obj.ip_address,
            created_at=obj.created_at,
            read_at=obj.read_at,
        )
