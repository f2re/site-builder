# Module: api/v1/users/schemas.py | Agent: backend-agent | Task: stage2_rbac
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class UserDeviceResponse(BaseModel):
    id: UUID
    device_uid: str
    name: str | None
    model: str | None
    firmware_version: str | None
    is_active: bool
    last_seen_at: datetime | None
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderSummary(BaseModel):
    """Lightweight order summary for the user cabinet purchase history."""
    id: UUID
    status: str
    total_amount: Decimal
    currency: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderDetail(OrderSummary):
    """Full order detail (extends summary)."""
    shipping_address: str | None
    cdek_order_uuid: str | None
    payment_id: str | None
    paid_at: datetime | None
    updated_at: datetime


class DeliveryAddressCreate(BaseModel):
    name: str
    recipient_name: str
    recipient_phone: str
    address_type: str
    full_address: str
    city: str
    postal_code: str | None = None
    provider: str
    pickup_point_code: str | None = None
    is_default: bool = False


class DeliveryAddressUpdate(BaseModel):
    name: str | None = None
    recipient_name: str | None = None
    recipient_phone: str | None = None
    address_type: str | None = None
    full_address: str | None = None
    city: str | None = None
    postal_code: str | None = None
    provider: str | None = None
    pickup_point_code: str | None = None


class DeliveryAddressResponse(BaseModel):
    id: UUID
    name: str
    recipient_name: str
    recipient_phone: str
    address_type: str
    full_address: str
    city: str
    postal_code: str | None
    provider: str
    pickup_point_code: str | None
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
