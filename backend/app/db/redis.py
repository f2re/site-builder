# Module: db/redis.py | Agent: backend-agent | Task: phase4_backend_ecommerce
import redis.asyncio as redis
from app.core.config import settings
from typing import Optional

_redis_client: Optional[redis.Redis] = None

def get_redis_client() -> redis.Redis:
    """Lazy initialization of redis client to avoid loop mismatch."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client

async def get_redis():
    yield get_redis_client()
