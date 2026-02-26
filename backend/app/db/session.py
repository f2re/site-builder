# Module: db.session | Agent: backend-agent | Task: stage1_backend
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# In case DATABASE_URL is still None (e.g., in unit tests without .env)
if settings.DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set.")

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
