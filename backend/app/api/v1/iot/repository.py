# Module: api/v1/iot/repository.py | Agent: backend-agent | Task: phase5_backend_iot
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

    async def update_last_seen(self, device_id: str) -> None:
        """Update the last_seen_at timestamp for a device."""
        await self.session.execute(
            update(UserDevice)
            .where(UserDevice.id == device_id)
            .values(last_seen_at=datetime.now(timezone.utc))
        )
        await self.session.commit()
