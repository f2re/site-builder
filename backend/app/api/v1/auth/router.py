# Module: api/v1/auth/router.py | Agent: backend-agent | Task: BE-01_products_catalog
from typing import cast, Dict, Any
from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import RedirectResponse
from app.api.v1.auth.schemas import LoginRequest, Token, UserCreate, UserResponse, TokenRefreshRequest
from app.api.v1.auth.service import AuthService
from app.core.dependencies import get_auth_service
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    return await auth_service.authenticate(login_data)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    user = await auth_service.register(user_in)
    return cast(UserResponse, user)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    return await auth_service.refresh_token(refresh_data.refresh_token)

@router.get("/{provider}/login")
async def provider_login(provider: str, redirect_uri: str = Query(...)):
    if provider == "google":
        url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.GOOGLE_CLIENT_ID}&response_type=code&"
            f"scope=openid%20profile%20email&redirect_uri={redirect_uri}"
        )
        return RedirectResponse(url)
    elif provider == "yandex":
        url = (
            f"https://oauth.yandex.ru/authorize?response_type=code&"
            f"client_id={settings.YANDEX_CLIENT_ID}&redirect_uri={redirect_uri}"
        )
        return RedirectResponse(url)
    else:
        return {"error": "Invalid provider"}

@router.get("/{provider}/callback", response_model=Token)
async def provider_callback(
    provider: str,
    code: str = Query(...),
    redirect_uri: str = Query(...),
    auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    if provider == "google":
        return await auth_service.handle_google_callback(code, redirect_uri)
    elif provider == "yandex":
        return await auth_service.handle_yandex_callback(code)
    else:
        raise ValueError("Unsupported provider")

@router.post("/telegram", response_model=Token)
async def telegram_auth(
    tg_data: Dict[str, Any],
    auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    return await auth_service.handle_telegram_auth(tg_data)
