import pytest
import asyncio
import uuid
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.db.base import Base
from app.core.config import settings

# Test database URL - using a separate database for tests
TEST_SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("site-builder", "site-builder-test")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client(db_session):
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.db.session import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def admin_token(db_session: AsyncSession):
    from app.db.models.user import User
    from app.core.security import get_blind_index, get_password_hash, create_access_token
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


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    from app.db.models.user import User
    from app.core.security import get_blind_index
    import uuid

    user_id = uuid.uuid4()
    email = f"user-{user_id}@example.com"
    user = User(
        id=user_id,
        email=email,
        email_hash=get_blind_index(email),
        role="customer",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
