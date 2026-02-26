from fastapi import APIRouter, Depends, status
from app.api.v1.auth.schemas import LoginRequest, Token, UserCreate, UserResponse
from app.api.v1.auth.service import AuthService
from app.core.dependencies import get_auth_service

router = APIRouter()

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
    return await auth_service.register(user_in)
