# Module: api/v1/users/router.py | Agent: backend-agent | Task: stage2_rbac
"""
User cabinet API — accessible only to authenticated users (any role).

Sections:
  GET  /users/me                       — current user profile
  PUT  /users/me                       — update profile
  GET  /users/me/orders                — purchase history
  GET  /users/me/orders/{id}           — order detail
  GET  /users/me/devices               — owned IoT/OBD2 devices
  POST /users/me/devices               — register a new device
  GET  /users/me/devices/{id}          — device detail
  DEL  /users/me/devices/{id}          — unregister device
  WS   /users/me/devices/{id}/connect  — real-time WebSocket connection to device
"""
from uuid import UUID
import json
import asyncio
from fastapi import APIRouter, Depends, status, Query, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Any, List
from jose import jwt, JWTError

from app.core.config import settings
from app.core.dependencies import require_customer, get_user_repository, get_order_repository, get_iot_repository, get_redis
from app.db.models.user import User
from app.api.v1.users.repository import UserRepository
from app.api.v1.orders.repository import OrderRepository
from app.api.v1.iot.repository import IoTRepository
from app.api.v1.orders.schemas import OrderRead
from redis.asyncio import Redis

router = APIRouter(prefix="/users", tags=["User Cabinet"])

# ─── Shared guard ────────────────────────────────────────────────────────────
UserDep = Depends(require_customer)


# ─── Schemas (inline) ────────────────────────────────────────────────────────

class UserProfileUpdate(BaseModel):
    full_name: str | None = None


class DeviceRegisterRequest(BaseModel):
    device_uid: str
    name: str | None = None
    model: str | None = None


class DeviceResponse(BaseModel):
    id: UUID
    device_uid: str
    name: str | None = None
    model: str | None = None
    is_active: bool
    last_seen_at: Any | None = None

    class Config:
        from_attributes = True


# ─── Profile ─────────────────────────────────────────────────────────────────

@router.get("/me")
async def get_my_profile(
    current_user: User = UserDep,
) -> Any:
    """Return current user profile."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }


@router.put("/me")
async def update_my_profile(
    body: UserProfileUpdate,
    current_user: User = UserDep,
    user_repo: UserRepository = Depends(get_user_repository)
) -> Any:
    """Update current user profile."""
    updated_user = await user_repo.update(current_user.id, full_name=body.full_name)
    return {
        "id": str(updated_user.id),
        "full_name": updated_user.full_name,
    }


# ─── Purchase history ────────────────────────────────────────────────────────

@router.get("/me/orders", response_model=List[OrderRead])
async def get_my_orders(
    current_user: User = UserDep,
    order_repo: OrderRepository = Depends(get_order_repository)
) -> Any:
    """List orders for the current user."""
    orders = await order_repo.get_user_orders(current_user.id)
    return orders


@router.get("/me/orders/{order_id}", response_model=OrderRead)
async def get_my_order(
    order_id: UUID,
    current_user: User = UserDep,
    order_repo: OrderRepository = Depends(get_order_repository)
) -> Any:
    """Get order detail for the current user."""
    order = await order_repo.get_by_id(order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# ─── IoT / OBD2 Devices ──────────────────────────────────────────────────────

@router.get("/me/devices", response_model=List[DeviceResponse])
async def get_my_devices(
    current_user: User = UserDep,
    iot_repo: IoTRepository = Depends(get_iot_repository)
) -> Any:
    """List IoT/OBD2 devices owned by the current user."""
    devices = await iot_repo.get_user_devices(current_user.id)
    return devices


@router.post("/me/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    body: DeviceRegisterRequest,
    current_user: User = UserDep,
    iot_repo: IoTRepository = Depends(get_iot_repository)
) -> Any:
    """Register a new IoT/OBD2 device to the current user account."""
    # Check if device_uid already exists
    existing = await iot_repo.get_device_by_uid(body.device_uid)
    if existing:
        raise HTTPException(status_code=400, detail="Device UID already registered")
        
    device = await iot_repo.create_device(
        user_id=current_user.id,
        device_uid=body.device_uid,
        name=body.name,
        model=body.model
    )
    return device


# ─── Real-time WebSocket connection to device ─────────────────────────────────

@router.websocket("/me/devices/{device_id}/connect")
async def device_websocket(
    device_id: UUID,
    websocket: WebSocket,
    redis: Redis = Depends(get_redis),
    user_repo: UserRepository = Depends(get_user_repository),
    iot_repo: IoTRepository = Depends(get_iot_repository)
) -> None:
    """
    WebSocket endpoint for real-time OBD2/IoT data stream.
    Client must pass JWT in query param ?token=<access_token>.
    """
    await websocket.accept()
    
    # 1. Manual Token Validation
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        user = await user_repo.get_by_id(UUID(user_id))
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except (JWTError, ValueError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Verify device ownership
    device = await iot_repo.get_device_by_id(device_id)
    if not device or device.user_id != user.id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 3. Subscribe to Redis Stream
    last_id = "$"  # Start from the latest message
    try:
        await websocket.send_json({
            "event": "connected",
            "device_id": str(device_id),
            "message": "Real-time telemetry stream connected",
        })
        
        while True:
            # Read from stream with blocking
            streams = await redis.xread({"iot:telemetry": last_id}, count=1, block=5000)
            if streams:
                for stream_name, messages in streams:
                    for msg_id, data in messages:
                        # Filter by device_id in data
                        if data.get("device_id") == str(device_id):
                            await websocket.send_json({
                                "event": "telemetry",
                                "data": json.loads(data.get("payload", "{}")),
                                "timestamp": msg_id.split("-")[0]
                            })
                        last_id = msg_id
            
            # Prevent busy loop and check for disconnects
            await asyncio.sleep(0.1)
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"event": "error", "message": str(e)})
        await websocket.close()
