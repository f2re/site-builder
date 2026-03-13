import pytest
import uuid
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.db.base import Base
from app.core.config import settings

@pytest.fixture
def anyio_backend():
    return "asyncio"

# Test database URL - using a separate database for tests
TEST_SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("site-builder", "site-builder-test")

@pytest.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture(scope="function")
async def redis_client():
    import fakeredis
    # Using FakeAsyncRedis for redis-py 5.x/4.x (asyncio)
    client = fakeredis.FakeAsyncRedis(decode_responses=True)
    try:
        yield client
    finally:
        await client.flushall()
        await client.aclose()

@pytest.fixture(scope="function")
async def client(db_session, redis_client):
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.db.session import get_db
    from app.db.redis import get_redis
    from app.integrations.redis_inventory import get_inventory, RedisInventory
    import app.db.redis as redis_module
    import app.integrations.redis_inventory as inventory_module

    async def override_get_db():
        yield db_session

    async def override_get_redis():
        yield redis_client

    def override_get_inventory():
        return RedisInventory(redis_client)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_inventory] = override_get_inventory

    # Patch global objects if they are used directly
    old_redis_client = redis_module.redis_client
    old_inventory = inventory_module.inventory
    
    redis_module.redis_client = redis_client
    inventory_module.inventory = RedisInventory(redis_client)

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()
        redis_module.redis_client = old_redis_client
        inventory_module.inventory = old_inventory

@pytest.fixture(scope="function")
async def admin_token(db_session: AsyncSession):
    from app.db.models.user import User
    from app.core.security import get_blind_index, get_password_hash, create_access_token

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


@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    from app.db.models.user import User
    from app.core.security import get_blind_index

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
