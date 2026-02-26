# Module: api/v1/iot/schemas.py | Agent: backend-agent | Task: phase5_backend_iot
from typing import Any, Dict
from pydantic import BaseModel, Field

class TelemetryDataRequest(BaseModel):
    """Request schema for incoming IoT telemetry data."""
    device_uid: str = Field(..., description="Unique hardware identifier of the device")
    payload: Dict[str, Any] = Field(..., description="Telemetry data payload")

class TelemetryDataResponse(BaseModel):
    """Response schema for telemetry data submission."""
    status: str = "success"
    message: str = "Telemetry data received and queued for processing"
