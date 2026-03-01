# Module: api/v1/firmware/router.py | Agent: backend-agent | Task: Phase 2 Dashfirm
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.api.v1.firmware.service import FirmwareService, get_firmware_service
from app.api.v1.firmware.schemas import (
    DeviceRead, DeviceCreate, TokenRead, 
    FirmwareVersionResponse, DownloadRequest
)
from app.db.models.firmware import DeviceType

router = APIRouter(prefix="/firmware", tags=["Firmware"])

@router.get("/my-token", response_model=TokenRead)
async def get_my_token(
    current_user: User = Depends(get_current_user),
    service: FirmwareService = Depends(get_firmware_service)
):
    token = await service.get_or_create_token(current_user.id)
    return {"token": token}

@router.get("/my-devices", response_model=List[DeviceRead])
async def get_my_devices(
    current_user: User = Depends(get_current_user),
    service: FirmwareService = Depends(get_firmware_service)
):
    return await service.get_my_devices(current_user.id)

@router.post("/add-device", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
async def add_device(
    payload: DeviceCreate,
    current_user: User = Depends(get_current_user),
    service: FirmwareService = Depends(get_firmware_service)
):
    return await service.add_device(current_user.id, payload.serial)

@router.get("/versions/{device_type}", response_model=FirmwareVersionResponse)
async def get_versions(
    device_type: DeviceType,
    service: FirmwareService = Depends(get_firmware_service)
):
    versions = service.get_versions(device_type)
    return {"versions": versions}

@router.post("/download")
async def download_firmware(
    payload: DownloadRequest,
    current_user: User = Depends(get_current_user),
    service: FirmwareService = Depends(get_firmware_service)
):
    # 1. Owner check
    devices = await service.get_my_devices(current_user.id)
    if not any(d.serial == payload.serial for d in devices):
        # Admin bypass or just owner check
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't own this device"
            )
    
    # 2. Summation logic
    final_label = await service.sum_complectations(payload.selected_complectation_ids)
    
    # 3. Compiler call
    file_path = service.compile_firmware(
        payload.device_type,
        payload.serial,
        payload.version,
        final_label
    )
    
    # 4. File streaming
    return FileResponse(
        path=file_path,
        filename=f"{payload.serial}_{payload.version}.bin",
        media_type="application/octet-stream"
    )
