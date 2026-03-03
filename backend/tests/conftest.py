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
from app.core.config import settings

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
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def redis_client() -> AsyncGenerator[Redis, None]:
    # In a real integration test, we might want a real Redis (e.g. db 15)
    # For now, let's assume we use a real one or mock it if needed.
    # Given the constraints, I'll try to connect to the configured Redis.
    client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield client
    await client.flushdb()
    await client.close()
