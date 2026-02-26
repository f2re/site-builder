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
from fastapi import APIRouter, Depends, status, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Any

from app.core.dependencies import require_customer
from app.db.models.user import User

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
) -> Any:
    """Update current user profile. TODO: wire UserRepository update."""
    return {
        "id": str(current_user.id),
        "full_name": body.full_name or current_user.full_name,
    }


# ─── Purchase history ────────────────────────────────────────────────────────

@router.get("/me/orders")
async def get_my_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = UserDep,
) -> Any:
    """
    List orders for the current user.
    TODO: wire OrderRepository filtered by user_id.
    """
    return {"items": [], "total": 0, "page": page, "per_page": per_page}


@router.get("/me/orders/{order_id}")
async def get_my_order(
    order_id: UUID,
    current_user: User = UserDep,
) -> Any:
    """
    Get order detail for the current user.
    TODO: wire OrderRepository, verify ownership.
    """
    return {"order_id": str(order_id), "user_id": str(current_user.id)}


# ─── IoT / OBD2 Devices ──────────────────────────────────────────────────────

@router.get("/me/devices")
async def get_my_devices(
    current_user: User = UserDep,
) -> Any:
    """
    List IoT/OBD2 devices owned by the current user.
    TODO: wire DeviceRepository filtered by user_id.
    """
    return {"items": [], "total": 0}


@router.post("/me/devices", status_code=status.HTTP_201_CREATED)
async def register_device(
    body: DeviceRegisterRequest,
    current_user: User = UserDep,
) -> Any:
    """
    Register a new IoT/OBD2 device to the current user account.
    TODO: wire DeviceRepository + check device_uid uniqueness.
    """
    return {
        "detail": "stub — device registration not yet implemented",
        "device_uid": body.device_uid,
        "user_id": str(current_user.id),
    }


@router.get("/me/devices/{device_id}")
async def get_my_device(
    device_id: UUID,
    current_user: User = UserDep,
) -> Any:
    """
    Get device detail.
    TODO: wire DeviceRepository, verify ownership.
    """
    return {"device_id": str(device_id), "user_id": str(current_user.id)}


@router.delete("/me/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_device(
    device_id: UUID,
    current_user: User = UserDep,
) -> None:
    """
    Unregister a device.
    TODO: wire DeviceRepository, verify ownership.
    """
    return


# ─── Real-time WebSocket connection to device ─────────────────────────────────

@router.websocket("/me/devices/{device_id}/connect")
async def device_websocket(
    device_id: UUID,
    websocket: WebSocket,
) -> None:
    """
    WebSocket endpoint for real-time OBD2/IoT data stream.
    Client must pass JWT in query param ?token=<access_token>.
    TODO:
      1. Validate token via get_current_user (manual decode here — Depends not supported in WS).
      2. Verify device ownership via DeviceRepository.
      3. Subscribe to Redis Stream XREAD for device_id.
      4. Forward events to client in real time.
    """
    await websocket.accept()
    try:
        await websocket.send_json({
            "event": "connected",
            "device_id": str(device_id),
            "message": "WebSocket stub — real-time stream not yet wired to Redis.",
        })
        while True:
            data = await websocket.receive_text()
            # Echo back until real IoT stream is wired
            await websocket.send_json({"event": "echo", "data": data})
    except WebSocketDisconnect:
        pass
