# Module: api/v1/cart/service.py | Agent: backend-agent | Task: phase4_backend_ecommerce
import json
from uuid import UUID
from typing import Any, Dict, Optional
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.v1.cart.schemas import CartItemCreate, CartItemUpdate
from app.db.models.product import ProductVariant


class CartService:
    def __init__(self, redis: Redis, session: AsyncSession):
        self.redis = redis
        self.session = session
        self.ttl = 60 * 60 * 24 * 7  # 7 days

    def _get_key(self, cart_id: str) -> str:
        return f"cart:{cart_id}"

    async def get_cart(self, cart_id: str) -> Dict[str, Any]:
        key = self._get_key(cart_id)
        cart_data = await self.redis.get(key)
        if not cart_data:
            return {"items": [], "total_quantity": 0, "total_price": 0.0}
        
        items_dict = json.loads(cart_data)
        if not items_dict:
            return {"items": [], "total_quantity": 0, "total_price": 0.0}

        variant_ids = [UUID(vid) for vid in items_dict.keys()]
        
        stmt = (
            select(ProductVariant)
            .options(joinedload(ProductVariant.product))
            .where(ProductVariant.id.in_(variant_ids))
        )
        result = await self.session.execute(stmt)
        variants = result.scalars().all()
        
        cart_items = []
        total_price = 0.0
        total_quantity = 0
        
        for variant in variants:
            qty = items_dict[str(variant.id)]
            subtotal = float(variant.price) * qty
            
            cart_items.append({
                "variant_id": variant.id,
                "name": f"{variant.product.name} ({variant.sku})",
                "price": float(variant.price),
                "quantity": qty,
                "subtotal": round(subtotal, 2),
                "image_url": None  # Simplified for now
            })
            total_price += subtotal
            total_quantity += qty
            
        return {
            "items": cart_items,
            "total_quantity": total_quantity,
            "total_price": round(total_price, 2)
        }

    async def add_item(self, cart_id: str, item: CartItemCreate) -> Dict[str, Any]:
        key = self._get_key(cart_id)
        cart_data = await self.redis.get(key)
        items_dict = json.loads(cart_data) if cart_data else {}
        
        variant_id_str = str(item.variant_id)
        if variant_id_str in items_dict:
            items_dict[variant_id_str] += item.quantity
        else:
            items_dict[variant_id_str] = item.quantity
            
        await self.redis.setex(key, self.ttl, json.dumps(items_dict))
        return await self.get_cart(cart_id)

    async def update_item(self, cart_id: str, variant_id: UUID, item: CartItemUpdate) -> Optional[Dict[str, Any]]:
        key = self._get_key(cart_id)
        cart_data = await self.redis.get(key)
        if not cart_data:
            return None
            
        items_dict = json.loads(cart_data)
        variant_id_str = str(variant_id)
        
        if variant_id_str in items_dict:
            items_dict[variant_id_str] = item.quantity
            await self.redis.setex(key, self.ttl, json.dumps(items_dict))
            return await self.get_cart(cart_id)
        return None

    async def remove_item(self, cart_id: str, variant_id: UUID) -> Optional[Dict[str, Any]]:
        key = self._get_key(cart_id)
        cart_data = await self.redis.get(key)
        if not cart_data:
            return None
            
        items_dict = json.loads(cart_data)
        variant_id_str = str(variant_id)
        
        if variant_id_str in items_dict:
            del items_dict[variant_id_str]
            await self.redis.setex(key, self.ttl, json.dumps(items_dict))
            return await self.get_cart(cart_id)
        return None

    async def clear_cart(self, cart_id: str) -> None:
        key = self._get_key(cart_id)
        await self.redis.delete(key)
