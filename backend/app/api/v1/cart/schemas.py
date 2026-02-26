# Module: api/v1/cart/schemas.py | Agent: backend-agent | Task: phase4_backend_ecommerce
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import List, Optional


class CartItemBase(BaseModel):
    variant_id: UUID
    quantity: int = Field(gt=0)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(CartItemBase):
    name: str
    price: float
    image_url: Optional[str] = None
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_quantity: int
    total_price: float

    model_config = ConfigDict(from_attributes=True)
