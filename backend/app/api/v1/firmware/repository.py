# Module: api/v1/firmware/repository.py | Agent: backend-agent | Task: feature_dashfirm_backend_001
import uuid
from typing import List, Optional, Sequence
from sqlalchemy import select, update, delete, and_
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import Depends
from app.db.session import get_db
from app.db.models.firmware import ModuleToken, ModuleDevice, ModuleComplectation, device_complectations
from app.db.models.user import User


class FirmwareRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_token_by_user_id(self, user_id: uuid.UUID) -> Optional[ModuleToken]:
        stmt = select(ModuleToken).where(ModuleToken.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_token_by_token_str(self, token: str) -> Optional[ModuleToken]:
        stmt = (
            select(ModuleToken)
            .where(ModuleToken.token == token)
            .options(
                selectinload(ModuleToken.devices).selectinload(ModuleDevice.complectations)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_token(self, user_id: uuid.UUID, token: str) -> ModuleToken:
        new_token = ModuleToken(user_id=user_id, token=token)
        self.session.add(new_token)
        await self.session.flush()
        return new_token

    async def get_devices_by_token_id(self, token_id: uuid.UUID) -> Sequence[ModuleDevice]:
        stmt = (
            select(ModuleDevice)
            .where(ModuleDevice.token_id == token_id)
            .options(selectinload(ModuleDevice.complectations))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_all_devices(self, search: Optional[str] = None) -> Sequence[ModuleDevice]:
        stmt = select(ModuleDevice).options(
            selectinload(ModuleDevice.complectations),
            selectinload(ModuleDevice.token).selectinload(ModuleToken.user),
        )
        if search:
            stmt = stmt.join(ModuleToken, ModuleDevice.token_id == ModuleToken.id).join(
                User, ModuleToken.user_id == User.id
            ).where(ModuleDevice.serial.ilike(f"%{search}%"))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_device_by_serial(self, serial: str) -> Optional[ModuleDevice]:
        stmt = (
            select(ModuleDevice)
            .where(ModuleDevice.serial == serial)
            .options(selectinload(ModuleDevice.complectations))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_device(
        self,
        token_id: uuid.UUID,
        serial: str,
        device_type: str,
        comment: Optional[str] = None,
    ) -> ModuleDevice:
        new_device = ModuleDevice(
            token_id=token_id,
            serial=serial,
            device_type=device_type,
            comment=comment,
        )
        self.session.add(new_device)
        await self.session.flush()
        return new_device

    async def delete_device(self, serial: str) -> bool:
        stmt = delete(ModuleDevice).where(ModuleDevice.serial == serial)
        result: CursorResult = await self.session.execute(stmt)  # type: ignore[assignment]
        return result.rowcount > 0

    async def get_complectations_by_ids(self, ids: List[uuid.UUID]) -> Sequence[ModuleComplectation]:
        stmt = select(ModuleComplectation).where(ModuleComplectation.id.in_(ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_complectation_by_id(self, comp_id: uuid.UUID) -> Optional[ModuleComplectation]:
        stmt = select(ModuleComplectation).where(ModuleComplectation.id == comp_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_complectation_by_code(
        self, code: int, simple: bool = False
    ) -> Optional[ModuleComplectation]:
        stmt = select(ModuleComplectation).where(
            and_(
                ModuleComplectation.code == code,
                ModuleComplectation.simple == simple,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_complectation_by_label(self, label: str) -> Optional[ModuleComplectation]:
        stmt = select(ModuleComplectation).where(ModuleComplectation.label == label)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_complectations(self) -> Sequence[ModuleComplectation]:
        stmt = select(ModuleComplectation).order_by(ModuleComplectation.caption)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_complectation(
        self, caption: str, label: str, code: int, simple: bool
    ) -> ModuleComplectation:
        new_comp = ModuleComplectation(
            caption=caption,
            label=label,
            code=code,
            simple=simple,
        )
        self.session.add(new_comp)
        await self.session.flush()
        return new_comp

    async def update_complectation(
        self, comp_id: uuid.UUID, caption: str, label: str, code: int, simple: bool
    ) -> Optional[ModuleComplectation]:
        stmt = (
            update(ModuleComplectation)
            .where(ModuleComplectation.id == comp_id)
            .values(caption=caption, label=label, code=code, simple=simple)
            .returning(ModuleComplectation)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete_complectation(self, comp_id: uuid.UUID) -> bool:
        stmt = delete(ModuleComplectation).where(ModuleComplectation.id == comp_id)
        result: CursorResult = await self.session.execute(stmt)  # type: ignore[assignment]
        return result.rowcount > 0

    async def add_complectation_to_device(self, serial: str, comp_id: uuid.UUID) -> None:
        stmt = device_complectations.insert().values(
            device_serial=serial, complectation_id=comp_id
        )
        await self.session.execute(stmt)

    async def toggle_device_complectation(self, serial: str, comp_id: uuid.UUID) -> None:
        # Check if association already exists
        check_stmt = select(device_complectations).where(
            and_(
                device_complectations.c.device_serial == serial,
                device_complectations.c.complectation_id == comp_id,
            )
        )
        result = await self.session.execute(check_stmt)
        existing = result.first()
        if existing:
            del_stmt = delete(device_complectations).where(
                and_(
                    device_complectations.c.device_serial == serial,
                    device_complectations.c.complectation_id == comp_id,
                )
            )
            await self.session.execute(del_stmt)
        else:
            ins_stmt = device_complectations.insert().values(
                device_serial=serial, complectation_id=comp_id
            )
            await self.session.execute(ins_stmt)

    async def merge_tokens(
        self, source_user_id: uuid.UUID, target_user_id: uuid.UUID
    ) -> None:
        source_token = await self.get_token_by_user_id(source_user_id)
        target_token = await self.get_token_by_user_id(target_user_id)

        if not source_token:
            return

        if not target_token:
            source_token.user_id = target_user_id
            await self.session.flush()
        else:
            stmt = (
                update(ModuleDevice)
                .where(ModuleDevice.token_id == source_token.id)
                .values(token_id=target_token.id)
            )
            await self.session.execute(stmt)
            await self.session.delete(source_token)
            await self.session.flush()

    async def get_user_by_email_hash(self, email_hash: str) -> Optional[User]:
        stmt = select(User).where(User.email_hash == email_hash)
        result = await self.session.execute(stmt)
        return result.scalars().first()


async def get_firmware_repo(
    session: AsyncSession = Depends(get_db),
) -> FirmwareRepository:
    return FirmwareRepository(session)
