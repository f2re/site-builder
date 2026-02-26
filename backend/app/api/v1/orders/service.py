# Module: api/v1/orders/service.py | Agent: backend-agent | Task: phase4_orders_logic
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.cart.service import CartService
from app.api.v1.orders.repository import OrderRepository
from app.api.v1.orders.schemas import OrderCreate
from app.db.models.order import Order, OrderItem, OrderStatus
from app.db.models.user import User


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        cart_service: CartService,
    ):
        self.order_repo = order_repo
        self.cart_service = cart_service

    async def create_order(self, user: User, order_data: OrderCreate) -> Order:
        # 1. Get cart items
        # For now, we use user.id as cart_id
        cart = await self.cart_service.get_cart(str(user.id))
        
        if not cart["items"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )

        # 2. Create Order
        order = Order(
            user_id=user.id,
            status=OrderStatus.PENDING,
            total_amount=Decimal(str(cart["total_price"])),
            shipping_address=order_data.shipping_address,
            currency="RUB"
        )
        
        # 3. Create OrderItems
        for item in cart["items"]:
            order_item = OrderItem(
                product_variant_id=item["variant_id"],
                quantity=item["quantity"],
                price=Decimal(str(item["price"]))
            )
            order.items.append(order_item)

        # 4. Save to DB
        created_order = await self.order_repo.create(order)
        
        # 5. Clear Cart
        await self.cart_service.clear_cart(str(user.id))
        
        return created_order

    async def get_order(self, order_id: UUID, user_id: UUID) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this order"
            )
        return order

    async def get_my_orders(self, user_id: UUID) -> List[Order]:
        orders = await self.order_repo.get_user_orders(user_id)
        return list(orders)
