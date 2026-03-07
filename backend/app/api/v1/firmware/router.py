# Module: api/v1/firmware/router.py | Agent: backend-agent | Task: feature_dashfirm_backend_001
import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.api.v1.firmware.service import FirmwareService, get_firmware_service
from app.api.v1.firmware.schemas import (
    DeviceRead,
    DeviceCreate,
    TokenRead,
    FirmwareVersionResponse,
    VersionInfoResponse,
    DownloadRequest,
)
from app.db.models.firmware import DeviceType

router = APIRouter(prefix="/firmware", tags=["Firmware"])


@router.get("/my-token", response_model=TokenRead)
async def get_my_token(
    current_user: User = Depends(get_current_user),
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    token = await service.get_or_create_token(current_user.id)
    return {"token": token}


@router.get("/my-devices", response_model=List[DeviceRead])
async def get_my_devices(
    current_user: User = Depends(get_current_user),
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    return await service.get_my_devices(current_user.id)


@router.post("/add-device", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
async def add_device(
    payload: DeviceCreate,
    current_user: User = Depends(get_current_user),
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    return await service.add_device(current_user.id, payload.serial)


@router.get("/versions/{device_type}", response_model=FirmwareVersionResponse)
async def get_versions(
    device_type: DeviceType,
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    versions = service.get_versions(device_type)
    return {"versions": versions}


@router.post("/download")
async def download_firmware(
    payload: DownloadRequest,
    current_user: User = Depends(get_current_user),
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    # Owner check
    devices = await service.get_my_devices(current_user.id)
    if not any(d.serial == payload.serial for d in devices):
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't own this device",
            )

    final_label = await service.sum_complectations(payload.selected_complectation_ids)

    file_path = service.compile_firmware(
        payload.device_type,
        payload.serial,
        payload.version,
        final_label,
    )

    dev_type_str = "OBD2" if payload.device_type == DeviceType.OBD else "AFR"
    filename = f"Firmware_{dev_type_str}_{payload.version}_{final_label}_{payload.serial}.bin"
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


# ── Public token-based endpoints (для устройств без авторизации) ──────────────

@router.get("/by-token/{token}/devices", response_model=List[DeviceRead])
async def get_devices_by_token(
    token: str,
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    return await service.get_devices_by_token_str(token)


@router.get("/by-token/{token}/versions/{device_type}", response_model=FirmwareVersionResponse)
async def get_versions_by_token(
    token: str,
    device_type: DeviceType,
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    # Validates token exists, raises 404 if not
    await service.get_devices_by_token_str(token)
    versions = service.get_versions(device_type)
    return {"versions": versions}


@router.get("/version-info", response_model=VersionInfoResponse)
async def get_version_info(
    version: str = Query(..., description="Revision number"),
    device_type: DeviceType = Query(..., description="Device type"),
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    return service.get_version_info(device_type, version)


@router.post("/by-token/{token}/download")
async def download_by_token(
    token: str,
    payload: DownloadRequest,
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    owns = await service.verify_token_owns_device(token, payload.serial)
    if not owns:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")

    final_label = await service.sum_complectations(payload.selected_complectation_ids)
    file_path = service.compile_firmware(payload.device_type, payload.serial, payload.version, final_label)

    dev_type_str = "OBD2" if payload.device_type == DeviceType.OBD else "AFR"
    filename = f"Firmware_{dev_type_str}_{payload.version}_{final_label}_{payload.serial}.bin"
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.post(
    "/devices/{serial}/complectations/{complectation_id}/toggle",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def toggle_device_complectation(
    serial: str,
    complectation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FirmwareService = Depends(get_firmware_service),
) -> None:
    await service.toggle_complectation(serial, complectation_id, current_user.id)
