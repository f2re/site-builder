import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from redis.asyncio import Redis

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.db.redis import get_redis

# Import all models to ensure they are registered with SQLAlchemy
from app.db.models import user, product, order, blog, delivery_address, order_tracking  # noqa: F401

# Test database URL - using a separate database for testing
# In a real environment, this should be provided via environment variables
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncSessionTest = async_sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

async def init_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    await init_db()
    yield
    # Cleanup after all tests
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionTest() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client(db_session: AsyncSession, redis_client: Redis) -> AsyncGenerator[AsyncClient, None]:
    def _get_test_db():
        yield db_session
    
    async def _get_test_redis():
        yield redis_client

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_redis] = _get_test_redis
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
