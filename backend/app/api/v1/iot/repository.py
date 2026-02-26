# Module: api/v1/iot/repository.py | Agent: backend-agent | Task: phase5_backend_users_cabinet
from typing import Sequence
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user_device import UserDevice
from datetime import datetime, timezone

class IoTRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_device_by_uid(self, device_uid: str) -> UserDevice | None:
        """Fetch an active device by its unique UID."""
        result = await self.session.execute(
            select(UserDevice).where(
                UserDevice.device_uid == device_uid,
                UserDevice.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_device_by_id(self, device_id: UUID) -> UserDevice | None:
        """Fetch a device by its UUID."""
        result = await self.session.execute(
            select(UserDevice).where(UserDevice.id == device_id)
        )
        return result.scalar_one_or_none()

    async def get_user_devices(self, user_id: UUID) -> Sequence[UserDevice]:
        """List all devices owned by a user."""
        result = await self.session.execute(
            select(UserDevice).where(UserDevice.user_id == user_id)
        )
        return result.scalars().all()

    async def create_device(
        self, user_id: UUID, device_uid: str, name: str | None = None, model: str | None = None
    ) -> UserDevice:
        """Register a new device for a user."""
        device = UserDevice(
            user_id=user_id,
            device_uid=device_uid,
            name=name,
            model=model
        )
        self.session.add(device)
        await self.session.commit()
        await self.session.refresh(device)
        return device

    async def update_last_seen(self, device_id: UUID) -> None:
        """Update the last_seen_at timestamp for a device."""
        await self.session.execute(
            update(UserDevice)
            .where(UserDevice.id == device_id)
            .values(last_seen_at=datetime.now(timezone.utc))
        )
        await self.session.commit()
