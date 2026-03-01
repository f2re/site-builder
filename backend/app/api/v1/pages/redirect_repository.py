# Module: api/v1/pages/redirect_repository.py | Agent: backend-agent | Task: p12_backend_001
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.models.redirect import Redirect
from app.db.session import get_db


class RedirectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_old_path(self, old_path: str) -> Optional[Redirect]:
        """Find a redirect by its old path."""
        # Ensure path starts with / for consistency
        if not old_path.startswith("/"):
            old_path = "/" + old_path
            
        stmt = select(Redirect).where(Redirect.old_path == old_path)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, redirect: Redirect) -> Redirect:
        self.session.add(redirect)
        await self.session.flush()
        await self.session.refresh(redirect)
        return redirect


async def get_redirect_repo(session: AsyncSession = Depends(get_db)) -> RedirectRepository:
    return RedirectRepository(session)
