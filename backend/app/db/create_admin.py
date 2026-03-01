#!/usr/bin/env python3
"""
Создание администратора.
Использование:
  ADMIN_EMAIL=<email> ADMIN_PASSWORD=<password> python -m app.db.create_admin
"""
import asyncio
import os
import sys

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash, encrypt_data, get_blind_index
from app.db.models.user import User


async def create_admin(email: str, password: str, full_name: str = "Admin"):
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        user = User(
            email=encrypt_data(email),
            email_hash=get_blind_index(email),
            full_name=encrypt_data(full_name),
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,
            role="admin",
            auth_provider="local",
        )
        session.add(user)
        await session.commit()
        print(f"✅ Admin created: {email}")

    await engine.dispose()


if __name__ == "__main__":
    email    = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    name     = os.environ.get("ADMIN_NAME", "Administrator")

    if not email or not password:
        print("Usage: ADMIN_EMAIL=<email> ADMIN_PASSWORD=<password> python -m app.db.create_admin")
        sys.exit(1)

    asyncio.run(create_admin(email, password, name))
