# Module: api/v1/admin/migration_repository.py | Agent: backend-agent | Task: BE-03_cart_orders_payments
from uuid import UUID
from typing import List, Optional, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.migration import MigrationJob, MigrationStatus, MigrationEntity

class MigrationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, entity: MigrationEntity) -> MigrationJob:
        job = MigrationJob(entity=entity, status=MigrationStatus.PENDING)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_job_by_id(self, job_id: UUID) -> Optional[MigrationJob]:
        stmt = select(MigrationJob).where(MigrationJob.id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_job_by_entity(self, entity: MigrationEntity) -> Optional[MigrationJob]:
        stmt = select(MigrationJob).where(
            MigrationJob.entity == entity,
            MigrationJob.status.in_([
                MigrationStatus.PENDING,
                MigrationStatus.RUNNING,
                MigrationStatus.PAUSED,
                MigrationStatus.FAILED
            ])
        ).order_by(MigrationJob.updated_at.desc())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_jobs(self) -> List[MigrationJob]:
        stmt = select(MigrationJob).order_by(MigrationJob.updated_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_job_status(self, job_id: UUID, status: MigrationStatus, **kwargs: Any) -> Optional[MigrationJob]:
        stmt = (
            update(MigrationJob)
            .where(MigrationJob.id == job_id)
            .values(status=status, **kwargs)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_job_by_id(job_id)
