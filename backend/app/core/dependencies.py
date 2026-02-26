# Module: core/dependencies.py | Agent: backend-agent | Task: stage1_backend
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.v1.users.repository import UserRepository
from app.api.v1.auth.service import AuthService

async def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)

async def get_auth_service(repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(repo)
