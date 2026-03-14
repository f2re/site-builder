# Module: db/celery_session.py | Agent: backend-agent | Task: fix_celery_db_connection
"""
Отдельная фабрика сессий для Celery-задач.

ВАЖНО: каждый вызов asyncio.run() в Celery создаёт новый event loop.
Async engines привязаны к event loop, поэтому нельзя переиспользовать
глобальный engine между разными asyncio.run() вызовами.

CelerySessionLocal() создаёт НОВЫЙ engine при каждом вызове.
Вызывающий код ОБЯЗАН использовать `async with CelerySessionLocal() as session:`
и engine будет dispose'd автоматически при выходе из контекста.
"""
import os
from contextlib import asynccontextmanager
from sqlalchemy.pool import NullPool, StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from app.core.config import settings


def _create_celery_engine() -> AsyncEngine:
    """Create a fresh async engine for the current event loop."""
    test_url = os.getenv("TEST_DATABASE_URL")
    if test_url:
        db_url = test_url
        poolclass = StaticPool if "sqlite" in test_url else NullPool
    elif os.getenv("PYTEST_CURRENT_TEST"):
        db_url = "sqlite+aiosqlite:///./test.db"
        poolclass = StaticPool
    else:
        db_url = settings.DATABASE_URL
        poolclass = NullPool

    return create_async_engine(db_url, poolclass=poolclass)


@asynccontextmanager
async def CelerySessionLocal():
    """
    Async context manager that creates a fresh engine + session per call.
    Engine is disposed on exit — safe for asyncio.run() in Celery prefork workers.

    Usage:
        async with CelerySessionLocal() as session:
            result = await session.execute(...)
    """
    engine = _create_celery_engine()
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    session = factory()
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()


# Legacy compat — не используется в новом коде
def get_celery_engine():
    return _create_celery_engine()


def reset_celery_engine() -> None:
    """No-op — engines are now per-call, no global state to reset."""
    pass
