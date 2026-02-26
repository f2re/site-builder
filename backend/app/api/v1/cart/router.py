# Module: api/v1/cart/router.py | Agent: backend-agent | Task: phase4_orders_logic
from uuid import UUID
from fastapi import APIRouter, Depends

from app.api.v1.cart.schemas import CartItemCreate, CartResponse
from app.api.v1.cart.service import CartService
from app.core.dependencies import get_current_user, get_cart_service
from app.db.models.user import User

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Get current user's cart.
    """
    return await cart_service.get_cart(str(current_user.id))


@router.post("/add", response_model=CartResponse)
async def add_to_cart(
    item: CartItemCreate,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Add a product variant to the cart.
    """
    return await cart_service.add_item(str(current_user.id), item)


@router.delete("/{variant_id}", response_model=CartResponse)
async def remove_from_cart(
    variant_id: UUID,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Remove a product variant from the cart.
    """
    return await cart_service.remove_item(str(current_user.id), variant_id)
