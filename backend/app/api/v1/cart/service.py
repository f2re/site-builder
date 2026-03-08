# Module: api/v1/cart/service.py | Agent: backend-agent | Task: p31_backend_cart_options
import json
from uuid import UUID
from typing import Any, Dict, Optional, List
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status

from app.api.v1.cart.schemas import CartItemCreate, CartItemUpdate
from app.db.models.product import ProductVariant, ProductOptionValue
from app.integrations.redis_inventory import RedisInventory


class CartService:
    def __init__(self, redis: Optional[Redis], session: AsyncSession, inventory: RedisInventory):
        self.redis = redis
        self.session = session
        self.inventory = inventory
        self.ttl = 60 * 60 * 24 * 7  # 7 days

    def _get_key(self, cart_id: str) -> str:
        return f"cart:{cart_id}"

    async def get_cart(self, cart_id: str) -> Dict[str, Any]:
        empty_cart = {
            "cart_id": UUID(cart_id),
            "items": [],
            "subtotal_rub": 0.0,
            "reserved_until": None
        }
        
        if not self.redis:
            return empty_cart
        
        key = self._get_key(cart_id)
        cart_data = await self.redis.get(key)
        if not cart_data:
            return empty_cart
        
        items_dict = json.loads(cart_data)
        if not items_dict:
            return empty_cart

        # items_dict: { "item_key": { "variant_id": "...", "quantity": 1, "selected_options": [...] } }
        variant_ids = list({UUID(v["variant_id"]) for v in items_dict.values()})
        
        stmt = (
            select(ProductVariant)
            .options(joinedload(ProductVariant.product))
            .where(ProductVariant.id.in_(variant_ids))
        )
        result = await self.session.execute(stmt)
        variants_map = {v.id: v for v in result.scalars().all()}
        
        cart_items = []
        total_price = 0.0
        
        for item_key, item_data in items_dict.items():
            variant_id = UUID(item_data["variant_id"])
            variant = variants_map.get(variant_id)
            if not variant:
                continue
                
            qty = item_data["quantity"]
            selected_options = item_data.get("selected_options", [])
            
            # Price calculation: variant price + sum of modifiers
            item_price = float(variant.price)
            for opt in selected_options:
                item_price += float(opt.get("price_modifier", 0))
                
            subtotal = item_price * qty
            
            # Get current stock
            stock_available = await self.inventory.get_stock(variant.id)

            cart_items.append({
                "item_id": item_key,
                "product_id": variant.id,
                "slug": variant.product.slug,
                "name": f"{variant.product.name} ({variant.sku})",
                "quantity": qty,
                "price_rub": round(item_price, 2),
                "stock_available": stock_available,
                "selected_options": selected_options
            })
            total_price += subtotal
            
        return {
            "cart_id": UUID(cart_id),
            "items": cart_items,
            "subtotal_rub": round(total_price, 2),
            "reserved_until": None
        }

    async def add_item(self, cart_id: str, item: CartItemCreate) -> Dict[str, Any]:
        if not self.redis:
             raise HTTPException(status_code=500, detail="Redis client not initialized")
        
        # 1. Resolve options to snapshots
        option_snapshots = []
        if item.selected_option_value_ids:
            # We need to fetch option values with their groups
            stmt = (
                select(ProductOptionValue)
                .options(joinedload(ProductOptionValue.group))
                .where(ProductOptionValue.id.in_(item.selected_option_value_ids))
            )
            res = await self.session.execute(stmt)
            values = res.scalars().all()
            
            if len(values) != len(item.selected_option_value_ids):
                raise HTTPException(status_code=422, detail="One or more invalid option value IDs")
                
            for val in values:
                option_snapshots.append({
                    "group_id": str(val.group_id),
                    "group_name": val.group.name,
                    "value_id": str(val.id),
                    "value_name": val.name,
                    "price_modifier": float(val.price_modifier)
                })
        
        # 2. Generate unique key for this combination
        # Sort option IDs to ensure consistent key for same combination
        sorted_opt_ids = sorted([str(v) for v in item.selected_option_value_ids])
        item_key = f"{item.variant_id}:{':'.join(sorted_opt_ids)}"
        
        # 3. Check stock
        current_stock = await self.inventory.get_stock(item.variant_id)
        
        key = self._get_key(cart_id)
        cart_data = await self.redis.get(key)
        items_dict = json.loads(cart_data) if cart_data else {}
        
        requested_qty = item.quantity
        if item_key in items_dict:
            requested_qty += items_dict[item_key]["quantity"]
            
        if current_stock < requested_qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {current_stock}"
            )

        items_dict[item_key] = {
            "variant_id": str(item.variant_id),
            "quantity": requested_qty,
            "selected_options": option_snapshots
        }
            
        await self.redis.setex(key, self.ttl, json.dumps(items_dict))
        return await self.get_cart(cart_id)

    async def update_item(self, cart_id: str, item_id: str, item: CartItemUpdate) -> Optional[Dict[str, Any]]:
        if not self.redis:
            return None
            
        key = self._get_key(cart_id)
        cart_data = await self.redis.get(key)
        if not cart_data:
            return None
            
        items_dict = json.loads(cart_data)
        if item_id not in items_dict:
            return None

        # Check stock
        variant_id = UUID(items_dict[item_id]["variant_id"])
        current_stock = await self.inventory.get_stock(variant_id)
        if current_stock < item.quantity:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {current_stock}"
            )

        items_dict[item_id]["quantity"] = item.quantity
        await self.redis.setex(key, self.ttl, json.dumps(items_dict))
        return await self.get_cart(cart_id)

    async def remove_item(self, cart_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        if not self.redis:
            return None
            
        key = self._get_key(cart_id)
        cart_data = await self.redis.get(key)
        if not cart_data:
            return None
            
        items_dict = json.loads(cart_data)
        if item_id in items_dict:
            del items_dict[item_id]
            await self.redis.setex(key, self.ttl, json.dumps(items_dict))
            return await self.get_cart(cart_id)
        return None

    async def clear_cart(self, cart_id: str) -> None:
        if not self.redis:
            return
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
        
        for item_key, item_data in guest_items.items():
            if item_key in user_items:
                user_items[item_key]["quantity"] += item_data["quantity"]
            else:
                user_items[item_key] = item_data
                
        await self.redis.setex(user_key, self.ttl, json.dumps(user_items))
        await self.redis.delete(guest_key)
