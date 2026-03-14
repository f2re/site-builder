# Module: db/opencart_session.py | Agent: orchestrator | Task: opencart_migration
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.pool import NullPool
from app.core.config import settings
from typing import Optional

_oc_engine: Optional[AsyncEngine] = None
_OCAsyncSessionLocal: Optional[async_sessionmaker] = None


def _build_oc_url() -> str:
    return (
        f"mysql+aiomysql://{settings.OC_DB_USER}:{settings.OC_DB_PASSWORD}"
        f"@{settings.OC_DB_HOST}:{settings.OC_DB_PORT}/{settings.OC_DB_NAME}"
    )


def get_oc_engine() -> AsyncEngine:
    """Lazy initialization — safe after fork."""
    global _oc_engine
    if _oc_engine is None:
        _oc_engine = create_async_engine(
            _build_oc_url(),
            poolclass=NullPool,
            pool_pre_ping=True,
            echo=settings.DEBUG,
        )
    return _oc_engine


def reset_oc_engine() -> None:
    """Call after fork to force re-creation in the child process."""
    global _oc_engine, _OCAsyncSessionLocal
    _oc_engine = None
    _OCAsyncSessionLocal = None


def OCAsyncSessionLocal():
    """Lazy session factory — always uses current engine."""
    global _OCAsyncSessionLocal
    if _OCAsyncSessionLocal is None:
        _OCAsyncSessionLocal = async_sessionmaker(
            get_oc_engine(),
            expire_on_commit=False,
        )
    return _OCAsyncSessionLocal()


# Keep backward-compatible alias
oc_engine = None  # Deprecated: use get_oc_engine()


async def get_oc_async_session():
    """Dependency for getting OpenCart async session"""
    async with OCAsyncSessionLocal() as session:
        yield session
