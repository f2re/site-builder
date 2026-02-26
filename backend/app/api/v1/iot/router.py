# Module: api/v1/iot/router.py | Agent: backend-agent | Task: phase5_backend_users_cabinet
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.db.session import get_db
from app.db.redis import get_redis
from app.api.v1.iot.repository import IoTRepository
from app.api.v1.iot.service import IoTService
from app.api.v1.iot.schemas import TelemetryDataRequest, TelemetryDataResponse

router = APIRouter(prefix="/iot", tags=["iot"])

def get_iot_service(
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> IoTService:
    repo = IoTRepository(session)
    return IoTService(repo, redis)

@router.post(
    "/data",
    response_model=TelemetryDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit telemetry data from an IoT device",
    description="Validates device existence and pushes telemetry data to a message stream"
)
async def submit_telemetry(
    data: TelemetryDataRequest,
    service: IoTService = Depends(get_iot_service)
) -> TelemetryDataResponse:
    """Submit telemetry data for processing."""
    return await service.process_telemetry(data)
