# Module: api/v1/orders/router.py | Agent: backend-agent | Task: phase4_orders_logic
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.v1.orders.schemas import OrderCreate, OrderRead
from app.api.v1.orders.service import OrderService
from app.core.dependencies import get_current_user, get_order_service, get_cart_id
from app.db.models.user import User

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    cart_id: str = Depends(get_cart_id),
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    """
    Create a new order from current cart items.
    """
    return await order_service.create_order(current_user, order_data, cart_id)


@router.get("/", response_model=List[OrderRead])
async def list_my_orders(
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    """
    Get all orders for the current user.
    """
    return await order_service.get_my_orders(current_user.id)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order_details(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    """
    Get detailed information about a specific order.
    """
    return await order_service.get_order(order_id, current_user.id)
