# Module: api/v1/admin/schemas.py | Agent: backend-agent | Task: BE-03_cart_orders_payments
from datetime import datetime
from uuid import UUID
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict
from app.db.models.migration import MigrationStatus, MigrationEntity
from app.api.v1.auth.schemas import UserResponse
from app.api.v1.orders.schemas import OrderRead


class AdminDeviceRead(BaseModel):
    id: UUID
    user_id: UUID
    device_uid: str
    name: Optional[str] = None
    model: Optional[str] = None
    is_active: bool
    registered_at: datetime
    last_seen_at: Optional[datetime] = None
    comment: Optional[str] = None
    oc_device_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class AdminDeviceUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    is_active: Optional[bool] = None
    comment: Optional[str] = None

class MigrationJobResponse(BaseModel):
    id: UUID
    entity: MigrationEntity
    status: MigrationStatus
    total: int
    processed: int
    skipped: int
    failed: int
    last_oc_id: Optional[int]
    errors: Optional[List]
    started_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class MigrationStartRequest(BaseModel):
    entity: Optional[MigrationEntity] = None

class MigrationEntityStatus(BaseModel):
    total: int
    processed: int
    status: str # Matches frontend PENDING | RUNNING | COMPLETED | PAUSED | FAILED
    error: Optional[str] = None

class MigrationStatusResponse(BaseModel):
    overall_status: str # IDLE | RUNNING | PAUSED | COMPLETED | FAILED
    overall_progress: float
    entities: Dict[str, MigrationEntityStatus]


# Admin Full User Response Models

class AdminDeliveryAddressRead(BaseModel):
    id: UUID
    name: str
    recipient_name: str
    recipient_phone: str
    full_address: str
    address_type: str
    city: str
    postal_code: Optional[str] = None
    provider: str
    pickup_point_code: Optional[str] = None
    is_default: bool

    model_config = ConfigDict(from_attributes=True)

class AdminUserDeviceRead(BaseModel):
    id: UUID
    device_uid: str
    name: Optional[str] = None
    model: Optional[str] = None
    last_seen_at: Optional[datetime] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class AdminUserFullResponse(UserResponse):
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    last_login_device: Optional[str] = None
    
    addresses: List[AdminDeliveryAddressRead] = []
    orders: List[OrderRead] = []
    devices: List[AdminUserDeviceRead] = []

    model_config = ConfigDict(from_attributes=True)
