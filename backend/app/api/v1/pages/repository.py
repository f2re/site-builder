# Module: api/v1/pages/repository.py | Agent: backend-agent | Task: p12_backend_001
from typing import Sequence, Optional
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.models.page import StaticPage
from app.db.session import get_db


class PageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, page_id: UUID) -> Optional[StaticPage]:
        return await self.session.get(StaticPage, page_id)

    async def get_by_slug(self, slug: str, active_only: bool = False) -> Optional[StaticPage]:
        stmt = select(StaticPage).where(StaticPage.slug == slug)
        if active_only:
            stmt = stmt.where(StaticPage.is_active)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, active_only: bool = False) -> Sequence[StaticPage]:
        stmt = select(StaticPage).order_by(StaticPage.title)
        if active_only:
            stmt = stmt.where(StaticPage.is_active)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, page: StaticPage) -> StaticPage:
        self.session.add(page)
        await self.session.flush()
        await self.session.refresh(page)
        return page

    async def update(self, page_id: UUID, **kwargs) -> Optional[StaticPage]:
        page = await self.get_by_id(page_id)
        if not page:
            return None
            
        for key, value in kwargs.items():
            if value is not None:
                setattr(page, key, value)
        
        await self.session.flush()
        return page

    async def delete(self, page_id: UUID) -> bool:
        stmt = delete(StaticPage).where(StaticPage.id == page_id)
        result = await self.session.execute(stmt)
        return getattr(result, "rowcount", 0) > 0


async def get_page_repo(session: AsyncSession = Depends(get_db)) -> PageRepository:
    return PageRepository(session)
