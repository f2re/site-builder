# Module: api/v1/auth/schemas.py | Agent: backend-agent | Task: BE-01_products_catalog
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None = None
    phone: str | None = None
    is_active: bool
    is_superuser: bool
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    sub: str | None = None
    type: str | None = None
    role: str = "customer"   # <-- role claim added


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
