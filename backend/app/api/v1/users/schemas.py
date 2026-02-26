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
