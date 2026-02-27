# Module: api/v1/cart/router.py | Agent: backend-agent | Task: BE-03
from uuid import UUID
from fastapi import APIRouter, Depends

from app.api.v1.cart.schemas import CartItemCreate, CartResponse, CartItemUpdate
from app.api.v1.cart.service import CartService
from app.core.dependencies import get_cart_service, get_cart_id

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=CartResponse)
async def get_cart(
    cart_id: str = Depends(get_cart_id),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Get current cart.
    """
    return await cart_service.get_cart(cart_id)


@router.post("/add", response_model=CartResponse)
async def add_to_cart(
    item: CartItemCreate,
    cart_id: str = Depends(get_cart_id),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Add a product variant to the cart.
    """
    return await cart_service.add_item(cart_id, item)


@router.patch("/{variant_id}", response_model=CartResponse)
async def update_cart_item(
    variant_id: UUID,
    item: CartItemUpdate,
    cart_id: str = Depends(get_cart_id),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Update a cart item's quantity.
    """
    return await cart_service.update_item(cart_id, variant_id, item)


@router.delete("/{variant_id}", response_model=CartResponse)
async def remove_from_cart(
    variant_id: UUID,
    cart_id: str = Depends(get_cart_id),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Remove a product variant from the cart.
    """
    return await cart_service.remove_item(cart_id, variant_id)


@router.delete("/", status_code=204)
async def clear_cart(
    cart_id: str = Depends(get_cart_id),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Clear the cart.
    """
    await cart_service.clear_cart(cart_id)
    return None
