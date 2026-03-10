# Module: integrations/redis_inventory.py | Agent: backend-agent | Task: BE-01
import redis.asyncio as redis
from fastapi import Depends
from app.db.redis import redis_client, get_redis
from uuid import UUID


class RedisInventory:
    def __init__(self, client: redis.Redis):
        self.client = client
        self._reserve_script = self.client.register_script("""
            local stock = tonumber(redis.call('GET', KEYS[1]))
            if not stock or stock < tonumber(ARGV[1]) then
                return -1
            end
            return redis.call('DECRBY', KEYS[1], ARGV[1])
        """)
        
        self._release_script = self.client.register_script("""
            return redis.call('INCRBY', KEYS[1], ARGV[1])
        """)

        # Confirm might be needed if we want to track 'committed' stock vs 'reserved'
        # But for now, simple DECR (reserve) and INCR (release) is the requirement.
        self._confirm_script = self.client.register_script("""
            -- Just a placeholder if we already decremented in reserve
            return 1
        """)

    async def reserve_stock(self, variant_id: UUID, quantity: int) -> bool:
        """
        Atomically reserve stock in Redis.
        Returns True if successful, False otherwise.
        """
        key = f"stock:{variant_id}"
        result = await self._reserve_script(keys=[key], args=[quantity])
        return result != -1

    async def release_stock(self, variant_id: UUID, quantity: int) -> int:
        """
        Release reserved stock back to Redis.
        """
        key = f"stock:{variant_id}"
        return await self._release_script(keys=[key], args=[quantity])

    async def confirm_stock(self, variant_id: UUID, quantity: int) -> bool:
        """
        Finalize stock reservation.
        """
        key = f"stock:{variant_id}"
        await self._confirm_script(keys=[key], args=[quantity])
        return True

    async def set_stock(self, variant_id: UUID, quantity: int) -> None:
        """
        Initialize or update stock in Redis.
        """
        key = f"stock:{variant_id}"
        await self.client.set(key, quantity)

    async def get_stock(self, variant_id: UUID) -> int:
        """
        Get current stock from Redis.
        """
        key = f"stock:{variant_id}"
        val = await self.client.get(key)
        return int(val) if val is not None else 0


def get_inventory(client: redis.Redis = Depends(get_redis)) -> RedisInventory:
    return RedisInventory(client)


def get_inventory_for_celery() -> RedisInventory:
    """
    Create a fresh RedisInventory instance for Celery tasks.
    Each call creates a new Redis client to avoid event loop conflicts
    when using asyncio.run() in Celery workers.
    """
    from app.core.config import settings
    client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return RedisInventory(client)


inventory = RedisInventory(redis_client)
