# Module: api/v1/orders/schemas.py | Agent: backend-agent | Task: p30_backend_order_items_schema_fix
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.db.models.order import OrderStatus


class OrderTrackingEventRead(BaseModel):
    id: UUID
    provider: str
    status: str
    message: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductImageBrief(BaseModel):
    url: str
    is_cover: bool

    model_config = ConfigDict(from_attributes=True)


class ProductBrief(BaseModel):
    name: str
    images: List[ProductImageBrief] = []

    model_config = ConfigDict(from_attributes=True)


class ProductVariantBrief(BaseModel):
    sku: Optional[str] = None
    product: Optional[ProductBrief] = None

    model_config = ConfigDict(from_attributes=True)


class OrderItemBase(BaseModel):
    product_variant_id: UUID
    quantity: int = Field(gt=0)


class OrderItemRead(OrderItemBase):
    id: UUID
    price: Decimal
    product_variant: Optional[ProductVariantBrief] = None
    selected_options: List[dict] = []

    @computed_field
    def product_name(self) -> str:
        if self.product_variant and self.product_variant.product:
            return self.product_variant.product.name
        return "Unknown Product"

    @computed_field
    def sku(self) -> Optional[str]:
        if self.product_variant:
            return self.product_variant.sku
        return None

    @computed_field
    def image_url(self) -> Optional[str]:
        if self.product_variant and self.product_variant.product:
            images = self.product_variant.product.images
            if images:
                cover = next((img for img in images if img.is_cover), images[0])
                return cover.url
        return None

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    shipping_address: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = Field(None, max_length=255)


class OrderRead(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    status: OrderStatus
    total_amount: Decimal
    currency: str
    shipping_address: Optional[str]
    payment_id: Optional[str] = None
    payment_url: Optional[str] = None
    paid_at: Optional[datetime] = None
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    delivery_status: Optional[str] = None
    delivery_provider: Optional[str] = None
    is_archived: bool = False
    created_at: datetime
    items: List[OrderItemRead]
    tracking_events: List[OrderTrackingEventRead] = []

    @computed_field
    def user_full_name(self) -> Optional[str]:
        if hasattr(self, "user") and self.user:
            return self.user.full_name
        return None

    @computed_field
    def user_email(self) -> Optional[str]:
        if hasattr(self, "user") and self.user:
            return self.user.email
        return None

    @computed_field
    def user_phone(self) -> Optional[str]:
        if hasattr(self, "user") and self.user:
            return self.user.phone
        return None

    model_config = ConfigDict(from_attributes=True)


class OrderList(BaseModel):
    items: List[OrderRead]
    total: int


class OrderUpdateStatus(BaseModel):
    status: OrderStatus


class PaymentLinkResponse(BaseModel):
    payment_url: str
