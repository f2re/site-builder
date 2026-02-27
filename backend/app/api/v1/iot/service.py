# Module: api/v1/iot/service.py | Agent: backend-agent | Task: phase5_backend_iot
import json
from typing import Dict, Any, cast
from redis.asyncio import Redis
from fastapi import HTTPException, status
from app.api.v1.iot.repository import IoTRepository
from app.api.v1.iot.schemas import TelemetryDataRequest, TelemetryDataResponse

class IoTService:
    def __init__(self, repo: IoTRepository, redis: Redis):
        self.repo = repo
        self.redis = redis

    async def process_telemetry(self, data: TelemetryDataRequest) -> TelemetryDataResponse:
        """Process incoming telemetry data: validate device and push to Redis Stream."""
        # 1. Verify existence of device
        device = await self.repo.get_device_by_uid(data.device_uid)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with UID {data.device_uid} not found or inactive"
            )

        # 2. Push telemetry to Redis Stream "iot:telemetry"
        # XADD key ID field value [field value ...]
        # We store the device_id, device_uid and serialized payload
        telemetry_payload = {
            "device_id": str(device.id),
            "device_uid": data.device_uid,
            "payload": json.dumps(data.payload)
        }
        
        try:
            await self.redis.xadd("iot:telemetry", cast(Dict[Any, Any], telemetry_payload))
        except Exception:
            # TODO: Logging structured errors
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to queue telemetry data"
            )

        # 3. Asynchronously update last_seen_at in DB
        # Ideally, this should be done in the background worker processing the stream,
        # but let's do it here for now as part of the initial implementation.
        # However, for high throughput, move this to the worker.
        await self.repo.update_last_seen(device.id)

        return TelemetryDataResponse()
