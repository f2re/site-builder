# Module: api/v1/auth/service.py | Agent: backend-agent | Task: stage2_rbac
from fastapi import HTTPException, status
from app.api.v1.auth.schemas import LoginRequest, Token, UserCreate
from app.api.v1.users.repository import UserRepository
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.db.models.user import User


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def authenticate(self, login_data: LoginRequest) -> Token:
        user = await self.repo.get_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
        # Pass role into token so every request can be authorized without extra DB hit
        return Token(
            access_token=create_access_token(user.id, role=user.role),
            refresh_token=create_refresh_token(user.id),
        )

    async def register(self, user_in: UserCreate) -> User:
        user = await self.repo.get_by_email(user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this username already exists in the system.",
            )

        user_db = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_active=True,
            is_superuser=False,
            role="customer",
        )
        return await self.repo.create(user_db)
