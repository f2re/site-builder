import asyncio
import pytest
import pytest_asyncio
import os
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from redis.asyncio import Redis

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.db.redis import get_redis
from app.tasks.celery_app import celery_app
from unittest.mock import MagicMock

# --- CRITICAL FIX FOR LOOP MISMATCH ---
# We must ensure that a single event loop is used for the entire session
# and that sqlalchemy engines are created WITHIN that loop.

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    # Force use of standard asyncio loop to avoid uvloop + nest_asyncio incompatibility
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

# Configure Celery for tests - ALWAYS EAGER
celery_app.conf.update(
    task_always_eager=True,
    task_eager_propagates=True,
    result_backend=None,
)

# Mock AsyncResult to avoid Redis connection attempts
import celery.result
celery.result.AsyncResult = MagicMock()

# Import all models
from app.db.models import user, product, order, blog, delivery_address, order_tracking  # noqa: F401

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")

@pytest_asyncio.fixture(scope="session")
async def engine(event_loop):
    # Ensure engine is created within the session event loop
    poolclass = StaticPool if "sqlite" in TEST_DATABASE_URL else None
    
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=poolclass,
    )
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session
        # Use rollback to keep tests isolated
        await session.rollback()

@pytest_asyncio.fixture
async def client(db_session: AsyncSession, redis_client: Redis) -> AsyncGenerator[AsyncClient, None]:
    # Dependency overrides must be clean
    def _get_test_db():
        yield db_session
    
    async def _get_test_redis():
        yield redis_client

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_redis] = _get_test_redis
    
    # Using ASGITransport ensures we don't start a real server but use the app directly
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def redis_client() -> AsyncGenerator[Redis, None]:
    from fakeredis.aioredis import FakeRedis
    client = FakeRedis(decode_responses=True)
    yield client
    await client.flushdb()
    await client.close()

@pytest_asyncio.fixture
async def admin_token(db_session: AsyncSession) -> str:
    from app.db.models.user import User
    from app.core.security import create_access_token, get_password_hash, get_blind_index
    import uuid

    admin_id = uuid.uuid4()
    email = f"admin-test-{admin_id}@example.com"
    admin = User(
        id=admin_id,
        email=email,
        email_hash=get_blind_index(email),
        hashed_password=get_password_hash("admin-password"),
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    await db_session.commit()

    return create_access_token(subject=str(admin_id), role="admin")
