# Module: api/v1/cart/service.py | Agent: backend-agent | Task: BE-03
import json
from uuid import UUID
from typing import Any, Dict, Optional
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status

from app.api.v1.cart.schemas import CartItemCreate, CartItemUpdate
from app.db.models.product import ProductVariant
from app.integrations.redis_inventory import inventory


class CartService:
    def __init__(self, redis: Optional[Redis], session: AsyncSession):
        self.redis = redis
        self.session = session
        self.ttl = 60 * 60 * 24 * 7  # 7 days

    def _get_key(self, cart_id: str) -> str:
        return f"cart:{cart_id}"

    async def get_cart(self, cart_id: str) -> Dict[str, Any]:
        if not self.redis:
            return {"items": [], "total_quantity": 0, "total_price": 0.0}
        
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
        
        # Sort variants to maintain consistent order if needed, or just follow items_dict
        for variant in variants:
            qty = items_dict[str(variant.id)]
            subtotal = float(variant.price) * qty
            
            cart_items.append({
                "variant_id": variant.id,
                "name": f"{variant.product.name} ({variant.sku})",
                "price": float(variant.price),
                "quantity": qty,
                "subtotal": round(subtotal, 2),
                "image_url": None  # Simplified
            })
            total_price += subtotal
            total_quantity += qty
            
        return {
            "items": cart_items,
            "total_quantity": total_quantity,
            "total_price": round(total_price, 2)
        }

    async def add_item(self, cart_id: str, item: CartItemCreate) -> Dict[str, Any]:
        if not self.redis:
             raise HTTPException(status_code=500, detail="Redis client not initialized")
        
        # Check stock before adding
        current_stock = await inventory.get_stock(item.variant_id)
        
        key = self._get_key(cart_id)
        cart_data = await self.redis.get(key)
        items_dict = json.loads(cart_data) if cart_data else {}
        
        variant_id_str = str(item.variant_id)
        requested_qty = item.quantity
        if variant_id_str in items_dict:
            requested_qty += items_dict[variant_id_str]
            
        if current_stock < requested_qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {current_stock}"
            )

        items_dict[variant_id_str] = requested_qty
            
        await self.redis.setex(key, self.ttl, json.dumps(items_dict))
        return await self.get_cart(cart_id)

    async def update_item(self, cart_id: str, variant_id: UUID, item: CartItemUpdate) -> Optional[Dict[str, Any]]:
        # Check stock
        current_stock = await inventory.get_stock(variant_id)
        if current_stock < item.quantity:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {current_stock}"
            )

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

    async def merge_carts(self, guest_cart_id: str, user_cart_id: str) -> None:
        if not self.redis:
            return
            
        guest_key = self._get_key(guest_cart_id)
        user_key = self._get_key(user_cart_id)
        
        guest_data = await self.redis.get(guest_key)
        if not guest_data:
            return
            
        user_data = await self.redis.get(user_key)
        
        guest_items = json.loads(guest_data)
        user_items = json.loads(user_data) if user_data else {}
        
        for variant_id, qty in guest_items.items():
            if variant_id in user_items:
                user_items[variant_id] += qty
            else:
                user_items[variant_id] = qty
                
        await self.redis.setex(user_key, self.ttl, json.dumps(user_items))
        await self.redis.delete(guest_key)
