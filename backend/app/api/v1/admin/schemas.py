# Module: api/v1/admin/schemas.py | Agent: backend-agent | Task: BE-03_cart_orders_payments
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.db.models.migration import MigrationStatus, MigrationEntity

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
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MigrationStartRequest(BaseModel):
    entity: MigrationEntity

class MigrationStatusResponse(BaseModel):
    jobs: List[MigrationJobResponse]
