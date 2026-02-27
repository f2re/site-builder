# Module: api/v1/users/repository.py | Agent: backend-agent | Task: phase7_backend_security
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import set_committed_value
from app.db.models.user import User
from app.core.security import encrypt_data, decrypt_data, get_blind_index

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _decrypt_user(self, user: User) -> User:
        """Decrypt PII data and mark them as committed to avoid accidental re-saves."""
        if user.email:
            # set_committed_value ensures SQLAlchemy doesn't see this as a change to be saved
            set_committed_value(user, "email", decrypt_data(user.email))
        if user.full_name:
            set_committed_value(user, "full_name", decrypt_data(user.full_name))
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Search by blind index and decrypt result."""
        email_hash = get_blind_index(email)
        result = await self.session.execute(
            select(User).where(User.email_hash == email_hash)
        )
        user = result.scalars().first()
        if user:
            return self._decrypt_user(user)
        return None

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get by ID and decrypt result."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalars().first()
        if user:
            return self._decrypt_user(user)
        return None

    async def create(self, user_in: User) -> User:
        """Encrypt PII data before creating a new user."""
        if user_in.email:
            user_in.email_hash = get_blind_index(user_in.email)
            user_in.email = encrypt_data(user_in.email)
        if user_in.full_name:
            user_in.full_name = encrypt_data(user_in.full_name)
            
        self.session.add(user_in)
        await self.session.commit()
        await self.session.refresh(user_in)
        return self._decrypt_user(user_in)

    async def update(self, user_id: UUID, **kwargs) -> User | None:
        """Encrypt PII data before updating."""
        if not kwargs:
            return await self.get_by_id(user_id)
            
        if "email" in kwargs:
            kwargs["email_hash"] = get_blind_index(kwargs["email"])
            kwargs["email"] = encrypt_data(kwargs["email"])
        if "full_name" in kwargs:
            kwargs["full_name"] = encrypt_data(kwargs["full_name"])
            
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(user_id)
