#!/usr/bin/env python3
"""
Создание администратора.

Использование:
  ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD=secret python -m app.db.create_admin

Или через docker compose:
  docker compose -f deploy/docker-compose.prod.yml --env-file .env.prod \\
    run --rm --no-deps \\
    -e ADMIN_EMAIL=admin@example.com \\
    -e ADMIN_PASSWORD=secret \\
    -e ADMIN_NAME="Administrator" \\
    backend python -m app.db.create_admin
См. DEVOPS.md, раздел 11.
"""
import asyncio
import os
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash, encrypt_data, get_blind_index
from app.db.models.user import User


async def create_admin(email: str, password: str, full_name: str = "Administrator") -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Проверяем, что пользователь с таким email ещё не существует
        email_hash = get_blind_index(email)
        result = await session.execute(
            select(User).where(User.email_hash == email_hash)
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            print(f"⚠️  Пользователь с email {email!r} уже существует (id={existing.id}, role={existing.role}).")
            print("Если нужно сбросить пароль, используйте API /api/v1/admin/users/{id}.")
            await engine.dispose()
            sys.exit(0)

        user = User(
            email=encrypt_data(email),
            email_hash=email_hash,
            full_name=encrypt_data(full_name),
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,
            role="admin",
            auth_provider="local",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"✅ Администратор создан: email={email!r}, id={user.id}, role={user.role}")

    await engine.dispose()


if __name__ == "__main__":
    _email    = os.environ.get("ADMIN_EMAIL", "").strip()
    _password = os.environ.get("ADMIN_PASSWORD", "").strip()
    _name     = os.environ.get("ADMIN_NAME", "Administrator").strip()

    if not _email or not _password:
        print(
            "Usage:\n"
            "  ADMIN_EMAIL=admin@example.com "
            "ADMIN_PASSWORD=secret "
            "python -m app.db.create_admin"
        )
        sys.exit(1)

    asyncio.run(create_admin(_email, _password, _name))
