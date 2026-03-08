# Module: api/v1/cart/schemas.py | Agent: backend-agent | Task: BE-03
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class CartItemBase(BaseModel):
    variant_id: UUID = Field(alias="product_id") # Contract says product_id
    quantity: int = Field(gt=0)


class CartItemCreate(CartItemBase):
    selected_option_value_ids: List[UUID] = []


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    item_id: str  # composite key for variant + options
    product_id: UUID
    slug: str
    name: str
    quantity: int
    price_rub: Decimal
    stock_available: int
    selected_options: List[dict] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CartResponse(BaseModel):
    cart_id: UUID
    items: List[CartItemResponse]
    subtotal_rub: Decimal
    reserved_until: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
