# Module: api/v1/firmware/schemas.py | Agent: backend-agent | Task: Phase 2 Dashfirm
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.db.models.firmware import DeviceType

class ComplectationBase(BaseModel):
    caption: str
    label: str
    code: int
    simple: bool

class ComplectationRead(ComplectationBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class ComplectationCreate(ComplectationBase):
    pass

class DeviceBase(BaseModel):
    serial: str
    device_type: DeviceType
    comment: Optional[str] = None

class DeviceRead(DeviceBase):
    id: UUID
    created_at: datetime
    complectations: List[ComplectationRead]
    owner_email: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class DeviceCreate(BaseModel):
    serial: str
    # token is determined by the current user session

class TokenRead(BaseModel):
    token: str
    model_config = ConfigDict(from_attributes=True)

class FirmwareVersionResponse(BaseModel):
    versions: List[str]

class DownloadRequest(BaseModel):
    device_type: DeviceType
    serial: str
    version: str
    selected_complectation_ids: List[UUID]

class UserMergeRequest(BaseModel):
    source_email: str
    target_email: str

class ExcelImportResponse(BaseModel):
    clients_imported: int
    devices_imported: int
    errors: List[str]
