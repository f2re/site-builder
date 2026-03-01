# Module: db/opencart_session.py | Agent: orchestrator | Task: opencart_migration
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

# MySQL (OpenCart) async engine
# Format: mysql+aiomysql://user:password@host:port/dbname
oc_db_url = (
    f"mysql+aiomysql://{settings.OC_DB_USER}:{settings.OC_DB_PASSWORD}"
    f"@{settings.OC_DB_HOST}:{settings.OC_DB_PORT}/{settings.OC_DB_NAME}"
)

oc_engine = create_async_engine(
    oc_db_url,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

OCAsyncSessionLocal = async_sessionmaker(
    oc_engine, 
    expire_on_commit=False
)

async def get_oc_async_session():
    """Dependency for getting OpenCart async session"""
    async with OCAsyncSessionLocal() as session:
        yield session
