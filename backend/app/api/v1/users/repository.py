# Module: api/v1/users/repository.py | Agent: backend-agent | Task: phase5_backend_users_cabinet
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()

    async def create(self, user_in: User) -> User:
        self.session.add(user_in)
        await self.session.commit()
        await self.session.refresh(user_in)
        return user_in

    async def update(self, user_id: UUID, **kwargs) -> User | None:
        if not kwargs:
            return await self.get_by_id(user_id)
            
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(user_id)
