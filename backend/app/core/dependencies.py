# Module: core/dependencies.py | Agent: backend-agent | Task: phase5_backend_users_cabinet
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.config import settings
from app.db.session import get_db
from app.db.redis import get_redis
from app.db.models.user import User
from app.api.v1.users.repository import UserRepository
from app.api.v1.auth.service import AuthService
from app.api.v1.auth.schemas import TokenPayload
from app.api.v1.cart.service import CartService
from app.api.v1.orders.repository import OrderRepository
from app.api.v1.products.repository import ProductRepository, get_product_repo
from app.api.v1.orders.service import OrderService
from app.api.v1.iot.repository import IoTRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ──────────────────────────────────────────────
# DB / Service factories
# ──────────────────────────────────────────────

async def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    return UserRepository(session)


async def get_auth_service(
    repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repo)


async def get_cart_service(
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_db),
) -> CartService:
    return CartService(redis, session)


async def get_order_repository(
    session: AsyncSession = Depends(get_db),
) -> OrderRepository:
    return OrderRepository(session)


async def get_iot_repository(
    session: AsyncSession = Depends(get_db),
) -> IoTRepository:
    return IoTRepository(session)


async def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    cart_service: CartService = Depends(get_cart_service),
    product_repo: ProductRepository = Depends(get_product_repo),
    session: AsyncSession = Depends(get_db),
) -> OrderService:
    return OrderService(order_repo, cart_service, product_repo, session)


# ──────────────────────────────────────────────
# Current user extraction from JWT
# ──────────────────────────────────────────────

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    repo: UserRepository = Depends(get_user_repository),
) -> User:
    """Decode JWT, validate token type, fetch and return the user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.sub is None or token_data.type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await repo.get_by_id(UUID(token_data.sub))
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Shortcut: any active authenticated user (customer, manager, admin)."""
    return current_user


# ──────────────────────────────────────────────
# Role-based guards  (use as FastAPI Depends)
# ──────────────────────────────────────────────

async def require_customer(
    current_user: User = Depends(get_current_user),
) -> User:
    """Any authenticated user may access the endpoint."""
    return current_user


async def require_manager(
    current_user: User = Depends(get_current_user),
) -> User:
    """Only manager or admin roles are allowed."""
    if current_user.role not in ("manager", "admin") and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Admin access required",
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Only admin role / superuser is allowed."""
    if current_user.role != "admin" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
