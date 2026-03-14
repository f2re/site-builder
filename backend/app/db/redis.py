# Module: db/redis.py | Agent: backend-agent | Task: fix_redis_fork_issue
import redis.asyncio as redis
from app.core.config import settings
from typing import Optional

_redis_client: Optional[redis.Redis] = None

def get_redis_client() -> redis.Redis:
    """Lazy initialization of redis client to avoid loop mismatch and fork issues."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client

def reset_redis_client() -> None:
    """Call after fork to force re-creation of the client in the child process."""
    global _redis_client
    _redis_client = None

async def get_redis():
    """Dependency for FastAPI to get redis client."""
    yield get_redis_client()
