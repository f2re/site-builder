# Module: api/v1/orders/schemas.py | Agent: backend-agent | Task: phase13_profile_orders_refactoring
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.order import OrderStatus


class OrderItemBase(BaseModel):
    product_variant_id: UUID
    quantity: int = Field(gt=0)


class OrderItemRead(OrderItemBase):
    id: UUID
    price: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    shipping_address: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = Field(None, max_length=255)


class OrderRead(BaseModel):
    id: UUID
    status: OrderStatus
    total_amount: Decimal
    currency: str
    shipping_address: Optional[str]
    payment_url: Optional[str] = None
    created_at: datetime
    items: List[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)


class OrderList(BaseModel):
    items: List[OrderRead]
    total: int


class OrderUpdateStatus(BaseModel):
    status: OrderStatus


class PaymentLinkResponse(BaseModel):
    payment_url: str
