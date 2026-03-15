# Module: api/v1/contact/repository.py | Agent: backend-agent | Task: p43_backend_feedback
"""Repository layer for ContactMessage and SiteSettings."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.contact import ContactMessage, ContactStatus, SiteSettings


class ContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict) -> ContactMessage:
        """Create a new contact message and flush to obtain the assigned ID."""
        obj = ContactMessage(**data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, msg_id: uuid.UUID) -> ContactMessage | None:
        result = await self.session.execute(
            select(ContactMessage).where(ContactMessage.id == msg_id)
        )
        return result.scalar_one_or_none()

    async def list_messages(
        self,
        status: ContactStatus | None,
        cursor: uuid.UUID | None,
        limit: int,
    ) -> tuple[list[ContactMessage], int]:
        """Cursor-based pagination, sorted by created_at DESC."""
        base_q = select(ContactMessage)
        count_q = select(func.count()).select_from(ContactMessage)

        if status is not None:
            base_q = base_q.where(ContactMessage.status == status)
            count_q = count_q.where(ContactMessage.status == status)

        if cursor is not None:
            # Fetch the created_at of the cursor row to paginate correctly
            cursor_row = await self.get_by_id(cursor)
            if cursor_row is not None:
                base_q = base_q.where(
                    ContactMessage.created_at < cursor_row.created_at
                )

        base_q = base_q.order_by(ContactMessage.created_at.desc()).limit(limit)

        rows = (await self.session.execute(base_q)).scalars().all()
        total = (await self.session.execute(count_q)).scalar_one()
        return list(rows), total

    async def mark_read(self, msg_id: uuid.UUID) -> ContactMessage | None:
        """Mark message as READ and set read_at if it was NEW."""
        obj = await self.get_by_id(msg_id)
        if obj is None:
            return None
        if obj.status == ContactStatus.NEW:
            obj.status = ContactStatus.READ
            obj.read_at = datetime.now(timezone.utc)
            await self.session.flush()
            await self.session.refresh(obj)
        return obj

    async def update_status(
        self, msg_id: uuid.UUID, status: ContactStatus
    ) -> ContactMessage | None:
        obj = await self.get_by_id(msg_id)
        if obj is None:
            return None
        obj.status = status
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, msg_id: uuid.UUID) -> bool:
        obj = await self.get_by_id(msg_id)
        if obj is None:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True


class SiteSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, key: str) -> str | None:
        result = await self.session.execute(
            select(SiteSettings.value).where(SiteSettings.key == key)
        )
        return result.scalar_one_or_none()

    async def set(self, key: str, value: str | None) -> None:
        """Upsert a setting value using PostgreSQL ON CONFLICT DO UPDATE."""
        await self.session.execute(
            text(
                "INSERT INTO site_settings (key, value, updated_at) "
                "VALUES (:key, :val, now()) "
                "ON CONFLICT (key) DO UPDATE SET value = :val, updated_at = now()"
            ),
            {"key": key, "val": value},
        )
        await self.session.flush()

    async def get_contact_settings(self) -> dict:
        contact_email = await self.get("contact_email")
        contact_page_text = await self.get("contact_page_text")
        return {
            "contact_email": contact_email,
            "contact_page_text": contact_page_text,
        }
