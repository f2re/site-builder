# Module: db/celery_session.py | Agent: backend-agent | Task: p29_backend_meilisearch_eventloop_fix
"""
Отдельная фабрика сессий для Celery-задач.
"""
import os
from sqlalchemy.pool import NullPool, StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

_celery_engine = None
_CelerySessionLocal = None

def get_celery_engine():
    global _celery_engine
    if _celery_engine is None:
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
        
        _celery_engine = create_async_engine(
            db_url,
            poolclass=poolclass,
        )
    return _celery_engine

def CelerySessionLocal():
    global _CelerySessionLocal
    if _CelerySessionLocal is None:
        engine = get_celery_engine()
        _CelerySessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _CelerySessionLocal()
