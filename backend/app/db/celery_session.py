# Module: db/celery_session.py | Agent: backend-agent | Task: p29_backend_meilisearch_eventloop_fix
"""
Отдельная фабрика сессий для Celery-задач.

Причина: asyncio.run() при завершении закрывает event loop. asyncpg (connection pool)
пытается вернуть соединения в пул — что требует работающего event loop — и падает с:
    RuntimeError: Event loop is closed
    RuntimeWarning: coroutine 'Connection._cancel' was never awaited

Решение: NullPool — соединения НЕ возвращаются в пул, а закрываются немедленно.
Это корректно для Celery, где каждый asyncio.run() создаёт изолированный event loop.

ВАЖНО: AsyncSessionLocal из session.py остаётся без изменений — он используется
в FastAPI через Depends(get_db), где event loop живёт всё время жизни запроса.
NullPool нужен ТОЛЬКО для Celery-задач.
"""
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

celery_engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
)

CelerySessionLocal = async_sessionmaker(
    bind=celery_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
