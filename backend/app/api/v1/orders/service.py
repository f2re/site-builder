# Module: api/v1/orders/service.py | Agent: backend-agent | Task: phase4_orders_logic
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.cart.service import CartService
from app.api.v1.orders.repository import OrderRepository
from app.api.v1.products.repository import ProductRepository
from app.api.v1.orders.schemas import OrderCreate
from app.db.models.order import Order, OrderItem, OrderStatus
from app.db.models.user import User
from app.integrations.yoomoney import yoomoney_client
from app.integrations.redis_inventory import inventory
from app.tasks.notifications.dispatcher import send_email_task
from app.core.config import settings


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        cart_service: CartService,
        product_repo: ProductRepository,
        session: AsyncSession,
    ):
        self.order_repo = order_repo
        self.cart_service = cart_service
        self.product_repo = product_repo
        self.session = session

    async def create_order(self, user: User, order_data: OrderCreate) -> Order:
        cart = await self.cart_service.get_cart(str(user.id))
        if not cart["items"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )

        # Reserve stock atomically in Redis, validate availability
        for item in cart["items"]:
            reserved = await inventory.reserve_stock(
                variant_id=item["variant_id"],
                quantity=item["quantity"]
            )
            if not reserved:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for item: {item['name']}"
                )

        total_amount = Decimal(str(cart["total_price"]))
        order = Order(
            user_id=user.id,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            shipping_address=order_data.shipping_address,
            currency="RUB"
        )

        for item in cart["items"]:
            order_item = OrderItem(
                product_variant_id=item["variant_id"],
                quantity=item["quantity"],
                price=Decimal(str(item["price"]))
            )
            order.items.append(order_item)

        order_id_str = str(order.id)
        return_url = f"{settings.FRONTEND_URL}/orders/{order_id_str}"
        payment_result = await yoomoney_client.create_payment(
            amount=total_amount,
            order_id=order_id_str,
            return_url=return_url,
            description=f"Order {order_id_str} at WifiOBD Shop",
        )
        order.payment_url = payment_result["payment_url"]
        order.payment_id = payment_result["payment_id"]

        created_order = await self.order_repo.create(order)
        await self.cart_service.clear_cart(str(user.id))
        await self.session.commit()
        await self.session.refresh(created_order)

        send_email_task.delay(
            recipient=user.email,
            subject=f"Zakaz #{created_order.id} prinyat",
            template_name="order_created.html",
            context={
                "full_name": user.full_name or user.email,
                "order_id": str(created_order.id),
                "total_amount": str(created_order.total_amount),
                "shipping_address": created_order.shipping_address,
                "payment_url": created_order.payment_url
            }
        )

        return created_order

    async def update_order_status(self, order_id: UUID, new_status: OrderStatus) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        order.status = new_status
        await self.order_repo.update(order)
        await self.session.commit()
        await self.session.refresh(order)

        if order.user:
            send_email_task.delay(
                recipient=order.user.email,
                subject=f"Status zakaza #{order.id} obnovlen",
                template_name="order_status_updated.html",
                context={
                    "full_name": order.user.full_name or order.user.email,
                    "order_id": str(order.id),
                    "status": order.status.value
                }
            )

        return order

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
