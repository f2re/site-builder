# Module: api/v1/cart/repository.py | Agent: backend-agent | Task: BE-03
from typing import Dict, List, Optional, Any
from uuid import UUID
from redis.asyncio import Redis
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models.cart import Cart, CartItem
from app.db.models.product import ProductVariant

class CartRepository:
    def __init__(self, redis: Redis, session: AsyncSession):
        self.redis = redis
        self.session = session

    def _get_redis_key(self, user_id: str | UUID | None = None, session_id: str | None = None) -> str:
        if user_id:
            return f"cart:{user_id}"
        return f"cart:guest:{session_id}"

    async def get_redis_items(self, user_id: str | UUID | None = None, session_id: str | None = None) -> Dict[str, int]:
        key = self._get_redis_key(user_id, session_id)
        items = await self.redis.hgetall(key)
        return {k.decode(): int(v) for k, v in items.items()}

    async def add_redis_item(self, variant_id: UUID, quantity: int, user_id: str | UUID | None = None, session_id: str | None = None) -> None:
        key = self._get_redis_key(user_id, session_id)
        await self.redis.hincrby(key, str(variant_id), quantity)
        if not user_id and session_id:
            await self.redis.expire(key, 7 * 24 * 60 * 60)  # 7 days

    async def remove_redis_item(self, variant_id: UUID, user_id: str | UUID | None = None, session_id: str | None = None) -> None:
        key = self._get_redis_key(user_id, session_id)
        await self.redis.hdel(key, str(variant_id))

    async def clear_redis_cart(self, user_id: str | UUID | None = None, session_id: str | None = None) -> None:
        key = self._get_redis_key(user_id, session_id)
        await self.redis.delete(key)

    async def get_db_cart(self, user_id: str | UUID | None = None, session_id: str | None = None) -> Optional[Cart]:
        stmt = select(Cart).options(joinedload(Cart.items).joinedload(CartItem.variant))
        if user_id:
            stmt = stmt.where(Cart.user_id == UUID(str(user_id)))
        else:
            stmt = stmt.where(Cart.session_id == session_id)
        
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_or_create_db_cart(self, user_id: str | UUID | None = None, session_id: str | None = None) -> Cart:
        cart = await self.get_db_cart(user_id, session_id)
        if not cart:
            cart = Cart(
                user_id=UUID(str(user_id)) if user_id else None,
                session_id=session_id
            )
            self.session.add(cart)
            await self.session.flush()
        return cart

    async def add_db_item(self, cart_id: UUID, variant_id: UUID, quantity: int, reserved_until: Any = None) -> CartItem:
        stmt = select(CartItem).where(CartItem.cart_id == cart_id, CartItem.variant_id == variant_id)
        result = await self.session.execute(stmt)
        item = result.scalars().first()
        
        if item:
            item.quantity += quantity
            if reserved_until:
                item.reserved_until = reserved_until
        else:
            item = CartItem(
                cart_id=cart_id,
                variant_id=variant_id,
                quantity=quantity,
                reserved_until=reserved_until
            )
            self.session.add(item)
        
        await self.session.flush()
        return item

    async def remove_db_item(self, cart_id: UUID, variant_id: UUID) -> None:
        stmt = delete(CartItem).where(CartItem.cart_id == cart_id, CartItem.variant_id == variant_id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def clear_db_cart(self, cart_id: UUID) -> None:
        stmt = delete(CartItem).where(CartItem.cart_id == cart_id)
        await self.session.execute(stmt)
        await self.session.flush()
