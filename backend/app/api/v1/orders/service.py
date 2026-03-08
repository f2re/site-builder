# Module: api/v1/orders/service.py | Agent: backend-agent | Task: update-admin-orders
import uuid
from decimal import Decimal
from typing import Dict, Any, cast
from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.cart.service import CartService
from app.api.v1.orders.repository import OrderRepository
from app.api.v1.products.repository import ProductRepository
from app.api.v1.orders.schemas import OrderCreate
from app.db.models.order import Order, OrderItem, OrderStatus
from app.db.models.order_tracking import OrderTrackingEvent
from app.db.models.user import User
from app.integrations.yoomoney import yoomoney_client
from app.integrations.redis_inventory import inventory
from app.integrations.cdek import cdek_client
from app.integrations.pochta import pochta_client
from app.tasks.notifications.dispatcher import send_email_task
from app.core.config import settings
from app.core.logging import logger


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

    async def create_order(self, user: User, order_data: OrderCreate, cart_id: str) -> Order:
        # 1. Get cart items
        cart = await self.cart_service.get_cart(cart_id)

        if not cart["items"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )

        # 2. Stock reservation via Redis (Lua)
        reserved_items = []
        try:
            for item in cart["items"]:
                success = await inventory.reserve_stock(
                    variant_id=item["product_id"], 
                    quantity=item["quantity"]
                )
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock for item: {item['name']}"
                    )
                reserved_items.append(item)

            # 3. Create Order
            total_amount = Decimal(str(cart["total_price"])) if "total_price" in cart else Decimal(str(cart["subtotal_rub"]))
            order = Order(
                id=uuid.uuid4(),
                user_id=user.id if user else None,
                status=OrderStatus.PENDING_PAYMENT,
                total_amount=total_amount,
                shipping_address=order_data.shipping_address,
                currency="RUB"
            )

            for item in cart["items"]:
                order_item = OrderItem(
                    product_variant_id=item["product_id"],
                    quantity=item["quantity"],
                    price=Decimal(str(item["price_rub"])),
                    selected_options=item.get("selected_options", [])
                )
                order.items.append(order_item)

            # 4. Save Order to DB
            created_order = await self.order_repo.create(order)
            await self.session.flush()

            # 5. Generate Payment
            try:
                payment_data = await yoomoney_client.create_payment(
                    amount=total_amount,
                    order_id=str(created_order.id),
                    return_url=f"{settings.NUXT_PUBLIC_SITE_URL}/orders/success?id={created_order.id}",
                    description=f"Order {created_order.id} at WifiOBD Shop"
                )
                created_order.payment_id = payment_data["payment_id"]
                created_order.payment_url = payment_data["payment_url"]
            except Exception as e:
                logger.error("payment_creation_failed", order_id=str(created_order.id), error=str(e))
                # Even if payment creation fails, the order is created.
                # User can retry payment later via get_payment_link.

            # 7. Clear Cart
            await self.cart_service.clear_cart(cart_id)

            # 8. Commit transaction
            await self.session.commit()
            await self.session.refresh(created_order)

            # 9. Trigger Notification (Async via Celery)
            recipient_email = user.email if user else order_data.email
            if recipient_email:
                send_email_task.delay(
                    recipient=recipient_email,
                    subject=f"Заказ №{created_order.id} принят",
                    template_name="order_created.html",
                    context={
                        "full_name": (user.full_name if user else None) or recipient_email,
                        "order_id": str(created_order.id),
                        "total_amount": str(created_order.total_amount),
                        "shipping_address": created_order.shipping_address,
                        "payment_url": created_order.payment_url
                    }
                )

            return created_order

        except Exception as e:
            # Release reserved stock in Redis on error
            for item in reserved_items:
                await inventory.release_stock(item["variant_id"], item["quantity"])
            
            # Rollback DB transaction (though it would happen anyway on uncaught exception)
            await self.session.rollback()
            
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create order: {str(e)}"
            )

    async def update_order_status(self, order_id: UUID, new_status: OrderStatus) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        old_status = order.status
        order.status = new_status
        if new_status == OrderStatus.PAID:
            order.paid_at = datetime.now(timezone.utc)
            
        # Add tracking event for manual status change
        if old_status != new_status:
            tracking_event = OrderTrackingEvent(
                order_id=order.id,
                provider="admin",
                status=new_status.value,
                message=f"Status changed from {old_status.value} to {new_status.value} by administrator"
            )
            self.session.add(tracking_event)

        await self.order_repo.update(order)
        await self.session.commit()
        await self.session.refresh(order)

        if order.user:
            send_email_task.delay(
                recipient=order.user.email,
                subject=f"Статус заказа #{order.id} обновлен",
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

    async def get_my_orders(self, user_id: UUID) -> Dict[str, Any]:
        orders = await self.order_repo.get_user_orders(user_id)
        items = list(orders)
        return {"items": items, "total": len(items)}

    async def cancel_order(self, order_id: UUID, user_id: UUID) -> Order:
        """Cancel an order and release stock in Redis."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this order"
            )

        if order.status not in [OrderStatus.PENDING, OrderStatus.PENDING_PAYMENT]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel order in status: {order.status.value}"
            )

        # 1. Release stock in Redis
        for item in order.items:
            await inventory.release_stock(item.product_variant_id, item.quantity)

        # 2. Update order status
        order.status = OrderStatus.CANCELLED
        
        # Add tracking event
        tracking_event = OrderTrackingEvent(
            order_id=order.id,
            provider="system",
            status=OrderStatus.CANCELLED.value,
            message="Order cancelled by user"
        )
        self.session.add(tracking_event)
        
        await self.order_repo.update(order)
        await self.session.commit()
        await self.session.refresh(order)

        logger.info("order_cancelled", order_id=str(order.id), user_id=str(user_id))
        return order

    async def get_payment_link(self, order_id: UUID, user_id: UUID) -> str:
        """Return existing payment link or generate a new one."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

        if order.status != OrderStatus.PENDING_PAYMENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order is in status {order.status.value}, payment link not available"
            )

        if order.payment_url:
            return cast(str, order.payment_url)

        # Generate new payment
        try:
            payment_data = await yoomoney_client.create_payment(
                amount=order.total_amount,
                order_id=str(order.id),
                return_url=f"{settings.NUXT_PUBLIC_SITE_URL}/orders/success?id={order.id}",
                description=f"Order {order.id} at WifiOBD Shop"
            )
            order.payment_id = payment_data["payment_id"]
            order.payment_url = payment_data["payment_url"]
            
            await self.order_repo.update(order)
            await self.session.commit()
            
            return cast(str, order.payment_url)
        except Exception as e:
            logger.error("payment_regeneration_failed", order_id=str(order.id), error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate payment link"
            )

    async def create_shipment(self, order_id: UUID, provider: str) -> Order:
        """Auto-fulfillment: create shipment via provider API."""
        order = await self.order_repo.get_by_id(order_id)
        if not order or order.status != OrderStatus.PAID:
            raise HTTPException(status_code=400, detail="Order not eligible for shipment")

        try:
            if provider == "cdek":
                shipment_data = await cdek_client.create_order({
                    "type": 1,
                    "number": str(order.id),
                    "tariff_code": 136,
                    "recipient": {"name": order.user.full_name if order.user else "Customer"},
                    "to_location": {"address": order.shipping_address},
                    "packages": [{"number": "1", "weight": 500}]
                })
                order.cdek_order_uuid = shipment_data.get("entity", {}).get("uuid")
                order.tracking_number = shipment_data.get("entity", {}).get("cdek_number")
                order.tracking_url = cdek_client.get_tracking_url(order.tracking_number or "")
                order.delivery_provider = "cdek"

            elif provider == "pochta":
                from app.api.v1.delivery.provider import DeliveryOption
                from decimal import Decimal
                option = DeliveryOption(
                    provider="pochta", provider_label="Почта России",
                    service_type="courier", service_name="Посылка онлайн",
                    cost_rub=Decimal("0"), days_min=3, days_max=7,
                    tariff_code="ONLINE_PARCEL", logo_url="/img/delivery/pochta.svg"
                )
                result = await pochta_client.create_shipment(str(order.id), option)
                order.tracking_number = result.tracking_number
                order.tracking_url = pochta_client.get_tracking_url(result.tracking_number)
                order.delivery_provider = "pochta"

            order.status = OrderStatus.SHIPPED
            order.delivery_status = "created"
            
            # Add tracking event
            tracking_event = OrderTrackingEvent(
                order_id=order.id,
                provider=provider,
                status="SHIPPED",
                message=f"Shipment created via {provider}. Tracking: {order.tracking_number}"
            )
            self.session.add(tracking_event)
            
            await self.order_repo.update(order)
            await self.session.commit()
            await self.session.refresh(order)

            if order.user:
                send_email_task.delay(
                    recipient=order.user.email,
                    subject=f"Заказ #{order.id} отправлен",
                    template_name="order_shipped.html",
                    context={
                        "full_name": order.user.full_name or order.user.email,
                        "order_id": str(order.id),
                        "tracking_url": order.tracking_url
                    }
                )

            return order
        except Exception as e:
            logger.error("shipment_creation_failed", order_id=str(order.id), error=str(e))
            raise HTTPException(status_code=500, detail=f"Failed to create shipment: {str(e)}")
