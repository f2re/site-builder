# Module: api/v1/auth/service.py | Agent: backend-agent | Task: phase11_backend_admin_blog_refinement
import hmac
import hashlib
import time
from typing import Dict, Any, Optional
import httpx
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
from app.core.config import settings


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
        if not user.hashed_password or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
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

    async def get_or_create_oauth_user(
        self,
        provider: str,
        provider_id: str,
        email: str,
        full_name: Optional[str] = None
    ) -> User:
        """Find user by provider_id or email, then update or create."""
        # 1. Check by provider_id
        user = await self.repo.get_by_provider_id(provider, provider_id)
        
        if user:
            # Update user if email changed (rare for OAuth but possible)
            if user.email != email:
                user = await self.repo.update(user.id, email=email)
            return user

        # 2. Check by email (if they already have a local account)
        user = await self.repo.get_by_email(email)
        if user:
            # Link existing user to this provider
            user = await self.repo.update(
                user.id,
                auth_provider=provider,
                provider_id=provider_id
            )
            return user

        # 3. Create new user
        user_db = User(
            email=email,
            full_name=full_name,
            auth_provider=provider,
            provider_id=provider_id,
            is_active=True,
            role="customer",
        )
        return await self.repo.create(user_db)

    async def handle_google_callback(self, code: str, redirect_uri: str) -> Token:
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if token_res.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get Google token")
            
            token_data = token_res.json()
            access_token = token_data.get("access_token")
            
            # Get user info
            user_res = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if user_res.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get Google user info")
            
            user_info = user_res.json()
            email = user_info.get("email")
            provider_id = user_info.get("id")
            full_name = user_info.get("name")
            
            if not email or not provider_id:
                raise HTTPException(status_code=400, detail="Google did not return enough info")
            
            user = await self.get_or_create_oauth_user("google", provider_id, email, full_name)
            return Token(
                access_token=create_access_token(user.id, role=user.role),
                refresh_token=create_refresh_token(user.id),
            )

    async def handle_yandex_callback(self, code: str) -> Token:
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_res = await client.post(
                "https://oauth.yandex.ru/token",
                data={
                    "code": code,
                    "client_id": settings.YANDEX_CLIENT_ID,
                    "client_secret": settings.YANDEX_CLIENT_SECRET,
                    "grant_type": "authorization_code",
                },
            )
            if token_res.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get Yandex token")
            
            token_data = token_res.json()
            access_token = token_data.get("access_token")
            
            # Get user info
            user_res = await client.get(
                "https://login.yandex.ru/info?format=json",
                headers={"Authorization": f"OAuth {access_token}"},
            )
            if user_res.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get Yandex user info")
            
            user_info = user_res.json()
            email = user_info.get("default_email")
            provider_id = user_info.get("id")
            full_name = user_info.get("real_name") or user_info.get("display_name")
            
            if not email or not provider_id:
                raise HTTPException(status_code=400, detail="Yandex did not return enough info")
            
            user = await self.get_or_create_oauth_user("yandex", provider_id, email, full_name)
            return Token(
                access_token=create_access_token(user.id, role=user.role),
                refresh_token=create_refresh_token(user.id),
            )

    async def handle_telegram_auth(self, tg_data: Dict[str, Any]) -> Token:
        # Verify hash
        # 1. Sort all params except 'hash'
        auth_hash = tg_data.pop("hash", None)
        if not auth_hash:
            raise HTTPException(status_code=400, detail="Telegram hash missing")
            
        data_check_list = []
        for k, v in sorted(tg_data.items()):
            data_check_list.append(f"{k}={v}")
        data_check_string = "\n".join(data_check_list)
        
        # 2. Compute secret key = SHA256(bot_token)
        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        
        # 3. Compute HMAC-SHA256(secret_key, data_check_string)
        hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if hmac_hash != auth_hash:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram hash")
            
        # 4. Check auth_date to prevent replay attacks (e.g. within 24 hours)
        auth_date = int(tg_data.get("auth_date", 0))
        if time.time() - auth_date > 86400:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Telegram auth date expired")
            
        # Telegram ID is the provider_id
        provider_id = str(tg_data.get("id"))
        # We might not have email from Telegram, so we can use a placeholder or ask later.
        # But our User model requires email (hashed).
        # Telegram widget doesn't return email by default.
        # For now, if no email, we use username@telegram.org or something if email is required by DB.
        # User model has email as nullable=False.
        username = tg_data.get("username", f"user_{provider_id}")
        email = f"{username}@telegram.org"  # Placeholder if not provided
        
        full_name = tg_data.get("first_name", "")
        if tg_data.get("last_name"):
            full_name += f" {tg_data['last_name']}"
            
        user = await self.get_or_create_oauth_user("telegram", provider_id, email, full_name)
        return Token(
            access_token=create_access_token(user.id, role=user.role),
            refresh_token=create_refresh_token(user.id),
        )
