# Module: api/v1/firmware/service.py | Agent: backend-agent | Task: Phase 2 Dashfirm
import os
import secrets
import subprocess
import uuid
from typing import List, Tuple, Sequence
from fastapi import HTTPException, status, Depends
from app.api.v1.firmware.repository import FirmwareRepository, get_firmware_repo
from app.db.models.firmware import DeviceType, ModuleDevice, ModuleComplectation
from app.core.config import settings
from app.core.security import get_blind_index, encrypt_data
from app.db.models.user import User
import openpyxl

class FirmwareService:
    def __init__(self, repo: FirmwareRepository = Depends(get_firmware_repo)):
        self.repo = repo

    async def get_or_create_token(self, user_id: uuid.UUID) -> str:
        token_obj = await self.repo.get_token_by_user_id(user_id)
        if token_obj:
            return token_obj.token
        
        # Generate 40-char hex token
        new_token_str = secrets.token_hex(20) # 20 bytes = 40 hex chars
        token_obj = await self.repo.create_token(user_id, new_token_str)
        return token_obj.token

    async def get_my_devices(self, user_id: uuid.UUID) -> Sequence[ModuleDevice]:
        token_obj = await self.repo.get_token_by_user_id(user_id)
        if not token_obj:
            return []
        return await self.repo.get_devices_by_token_id(token_obj.id)

    async def get_all_devices(self) -> List[dict]:
        from app.core.security import decrypt_data
        devices = await self.repo.list_all_devices()
        result = []
        for d in devices:
            # ModuleDevice has token -> user -> email
            owner_email = "Unknown"
            if d.token and d.token.user:
                try:
                    owner_email = decrypt_data(d.token.user.email)
                except Exception:
                    owner_email = "Error decrypting"
            
            # Map to dict compatible with DeviceRead
            d_dict = {
                "id": d.id,
                "serial": d.serial,
                "device_type": d.device_type,
                "comment": d.comment,
                "created_at": d.created_at,
                "complectations": d.complectations,
                "owner_email": owner_email
            }
            result.append(d_dict)
        return result

    async def add_device(self, user_id: uuid.UUID, serial: str) -> ModuleDevice:
        # This will create token if it doesn't exist
        await self.get_or_create_token(user_id)
        token_obj = await self.repo.get_token_by_user_id(user_id)
        
        if not token_obj:
            raise HTTPException(status_code=500, detail="Failed to create/get token")

        existing_device = await self.repo.get_device_by_serial(serial)
        if existing_device:
            if existing_device.token_id == token_obj.id:
                return existing_device # Already owned
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device already registered to another user"
            )
        
        # Determine device type from serial
        device_type = DeviceType.OBD
        if serial.upper().startswith("A"):
            device_type = DeviceType.AFR
            
        return await self.repo.create_device(token_obj.id, serial, device_type)

    async def create_complectation(self, caption: str, label: str, code: int, simple: bool) -> ModuleComplectation:
        return await self.repo.create_complectation(caption, label, code, simple)

    async def update_complectation(self, comp_id: uuid.UUID, caption: str, label: str, code: int, simple: bool) -> ModuleComplectation:
        comp = await self.repo.update_complectation(comp_id, caption, label, code, simple)
        if not comp:
            raise HTTPException(status_code=404, detail="Complectation not found")
        return comp

    async def delete_complectation(self, comp_id: uuid.UUID):
        success = await self.repo.delete_complectation(comp_id)
        if not success:
            raise HTTPException(status_code=404, detail="Complectation not found")

    async def add_complectation_to_device(self, serial: str, comp_id: uuid.UUID):
        await self.repo.add_complectation_to_device(serial, comp_id)
        await self.repo.session.commit()

    async def sum_complectations(self, selected_ids: List[uuid.UUID]) -> str:
        if not selected_ids:
            return "BASE"
            
        complectations = await self.repo.get_complectations_by_ids(selected_ids)
        
        total_code = sum(c.code for c in complectations if c.simple)
        
        # If no simple complectations selected, but some selected_ids were provided,
        # it might be a direct non-simple complectation or just base.
        if total_code == 0 and not complectations:
            return "BASE"
            
        final_comp = await self.repo.get_complectation_by_code(total_code, simple=False)
        if not final_comp:
            # Fallback: if only one complectation and it's not simple, use its label
            if len(complectations) == 1 and not complectations[0].simple:
                return complectations[0].label
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No final complectation found for code sum {total_code}"
            )
            
        return final_comp.label

    def get_versions(self, device_type: DeviceType) -> List[str]:
        try:
            # Check if compiler exists
            if not os.path.exists(settings.COMPILER_PATH):
                return ["v1.0.0", "v1.1.0"] # Dev fallback

            result = subprocess.run(
                [settings.COMPILER_PATH, "--list", device_type.value],
                capture_output=True,
                text=True,
                check=True
            )
            versions = result.stdout.strip().splitlines()
            return versions
        except Exception:
            return ["v1.0.0", "v1.1.0"]

    def compile_firmware(self, device_type: str, serial: str, version: str, final_label: str) -> str:
        output_filename = f"{serial}_{version}_{final_label}.bin"
        output_path = os.path.join(settings.MEDIA_ROOT, "firmware", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if not os.path.exists(settings.COMPILER_PATH):
            # Create a dummy file for dev
            with open(output_path, "wb") as f:
                f.write(b"dummy firmware content")
            return output_path

        try:
            subprocess.run(
                [
                    settings.COMPILER_PATH, 
                    "--type", device_type,
                    "--serial", serial,
                    "--version", version,
                    "--label", final_label,
                    "--output", output_path
                ],
                check=True,
                capture_output=True,
                text=True
            )
            return output_path
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Compilation failed: {e.stderr}"
            )

    async def merge_users_firmware(self, source_email: str, target_email: str):
        source_hash = get_blind_index(source_email)
        target_hash = get_blind_index(target_email)
        
        source_user = await self.repo.get_user_by_email_hash(source_hash)
        target_user = await self.repo.get_user_by_email_hash(target_hash)
        
        if not source_user or not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both users not found"
            )
            
        await self.repo.merge_tokens(source_user.id, target_user.id)
        await self.repo.session.commit()

    async def import_excel(self, file_content: bytes) -> Tuple[int, int, List[str]]:
        import io
        wb = openpyxl.load_workbook(io.BytesIO(file_content))
        ws = wb.active
        
        clients_imported = 0
        devices_imported = 0
        errors = []
        
        # Headers: 0:Client, 1:Serial, 2:Type, 3:Complectation Label, 4:Code
        # Expecting at least Client and Serial
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not any(row):
                continue
            
            client_name = str(row[0]) if row[0] else None
            serial = str(row[1]) if row[1] else None
            dev_type_str = str(row[2]) if len(row) > 2 and row[2] else "OBD"
            comp_label = str(row[3]) if len(row) > 3 and row[3] else None
            
            if not client_name or not serial:
                errors.append(f"Row {row_idx}: Missing client name or serial")
                continue
                
            try:
                # 1. Find or create user
                email = f"imported_{uuid.uuid4().hex[:8]}@wifiobd.ru" # Fallback email
                email_hash = get_blind_index(email)
                
                # Try to see if we already created a user for this client name in this run
                # Simplified: just create a new user or find by name (requires more logic)
                # For now, let's create a user per row or find by some stable identifier if possible.
                # In Dashfirm, we usually link by token.
                
                # Check if device already exists
                device = await self.repo.get_device_by_serial(serial)
                if device:
                    errors.append(f"Row {row_idx}: Device {serial} already exists")
                    continue

                # Create user
                new_user = User(
                    email=encrypt_data(email),
                    email_hash=email_hash,
                    full_name=encrypt_data(client_name),
                    role="customer"
                )
                self.repo.session.add(new_user)
                await self.repo.session.flush()
                clients_imported += 1
                
                # Create token
                token_str = secrets.token_hex(20)
                token_obj = await self.repo.create_token(new_user.id, token_str)
                
                # Create device
                device_type = DeviceType.AFR if dev_type_str.upper() == "AFR" else DeviceType.OBD
                device = await self.repo.create_device(token_obj.id, serial, device_type)
                devices_imported += 1
                
                # Link complectation if label provided
                if comp_label:
                    comp = await self.repo.get_complectation_by_label(comp_label)
                    if comp:
                        await self.repo.add_complectation_to_device(serial, comp.id)
                
                await self.repo.session.commit()
            except Exception as e:
                await self.repo.session.rollback()
                errors.append(f"Row {row_idx}: {str(e)}")
        
        return clients_imported, devices_imported, errors

async def get_firmware_service(repo: FirmwareRepository = Depends(get_firmware_repo)) -> FirmwareService:
    return FirmwareService(repo)
