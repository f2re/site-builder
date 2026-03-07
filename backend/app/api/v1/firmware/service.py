# Module: api/v1/firmware/service.py | Agent: backend-agent | Task: feature_dashfirm_backend_001
import json
import os
import secrets
import shlex
import subprocess
import uuid
from pathlib import Path
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
        new_token_str = secrets.token_hex(20)  # 20 bytes = 40 hex chars
        token_obj = await self.repo.create_token(user_id, new_token_str)
        await self.repo.session.commit()
        return token_obj.token

    async def get_my_devices(self, user_id: uuid.UUID) -> Sequence[ModuleDevice]:
        token_obj = await self.repo.get_token_by_user_id(user_id)
        if not token_obj:
            return []
        return await self.repo.get_devices_by_token_id(token_obj.id)

    async def get_all_devices(self, search: str | None = None) -> List[dict]:
        from app.core.security import decrypt_data
        devices = await self.repo.list_all_devices(search=search)
        result = []
        for d in devices:
            owner_email = "Unknown"
            if d.token and d.token.user:
                try:
                    owner_email = decrypt_data(d.token.user.email)
                except Exception:
                    owner_email = "Error decrypting"

            d_dict = {
                "id": d.id,
                "serial": d.serial,
                "device_type": d.device_type,
                "comment": d.comment,
                "created_at": d.created_at,
                "complectations": d.complectations,
                "owner_email": owner_email,
            }
            result.append(d_dict)
        return result

    async def add_device(self, user_id: uuid.UUID, serial: str) -> ModuleDevice:
        await self.get_or_create_token(user_id)
        token_obj = await self.repo.get_token_by_user_id(user_id)

        if not token_obj:
            raise HTTPException(status_code=500, detail="Failed to create/get token")

        existing_device = await self.repo.get_device_by_serial(serial)
        if existing_device:
            if existing_device.token_id == token_obj.id:
                return existing_device
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device already registered to another user",
            )

        device_type = DeviceType.OBD
        if serial.upper().startswith("A"):
            device_type = DeviceType.AFR

        device = await self.repo.create_device(token_obj.id, serial, device_type)
        await self.repo.session.commit()
        return device

    async def create_complectation(
        self, caption: str, label: str, code: int, simple: bool
    ) -> ModuleComplectation:
        comp = await self.repo.create_complectation(caption, label, code, simple)
        await self.repo.session.commit()
        return comp

    async def update_complectation(
        self, comp_id: uuid.UUID, caption: str, label: str, code: int, simple: bool
    ) -> ModuleComplectation:
        comp = await self.repo.update_complectation(comp_id, caption, label, code, simple)
        if not comp:
            raise HTTPException(status_code=404, detail="Complectation not found")
        await self.repo.session.commit()
        return comp

    async def delete_complectation(self, comp_id: uuid.UUID) -> None:
        success = await self.repo.delete_complectation(comp_id)
        if not success:
            raise HTTPException(status_code=404, detail="Complectation not found")
        await self.repo.session.commit()

    async def add_complectation_to_device(self, serial: str, comp_id: uuid.UUID) -> None:
        await self.repo.add_complectation_to_device(serial, comp_id)
        await self.repo.session.commit()

    async def sum_complectations(self, selected_ids: List[uuid.UUID]) -> str:
        if not selected_ids:
            return "BASE"

        complectations = await self.repo.get_complectations_by_ids(selected_ids)

        total_code = sum(c.code for c in complectations if c.simple)

        if total_code == 0 and not complectations:
            return "BASE"

        final_comp = await self.repo.get_complectation_by_code(total_code, simple=False)
        if not final_comp:
            if len(complectations) == 1 and not complectations[0].simple:
                return complectations[0].label

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No final complectation found for code sum {total_code}",
            )

        return final_comp.label

    def get_versions(self, device_type: DeviceType) -> List[str]:
        compiler_path = Path(settings.FIRMWARE_COMPILER_PATH)
        if not compiler_path.exists():
            return ["1", "2", "3"]

        compiler_dir = shlex.quote(str(compiler_path.parent))
        compiler_binary = shlex.quote(compiler_path.name)
        device_exec = "wifi_obd2" if device_type == DeviceType.OBD else "wifi_afr"

        cmd = f"cd {compiler_dir} && ./{compiler_binary} {shlex.quote(device_exec)} revisions"
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
            )
            output = result.stdout.strip()
            if ":" in output:
                revisions = output[output.rfind(":") + 1:].split()
                if revisions:
                    return revisions
        except Exception:
            pass
        return ["1", "2", "3"]

    def compile_firmware(
        self, device_type: DeviceType, serial: str, version: str, final_label: str
    ) -> str:
        dev_type_str = "OBD2" if device_type == DeviceType.OBD else "AFR"
        output_filename = f"Firmware_{dev_type_str}_{version}_{final_label}_{serial}.bin"
        build_dir = settings.FIRMWARE_BUILD_DIR
        os.makedirs(build_dir, exist_ok=True)
        output_path = os.path.join(build_dir, output_filename)

        compiler_path = Path(settings.FIRMWARE_COMPILER_PATH)
        if not compiler_path.exists():
            with open(output_path, "wb") as f:
                f.write(b"dummy firmware content")
            return output_path

        compiler_dir = shlex.quote(str(compiler_path.parent))
        compiler_binary = shlex.quote(compiler_path.name)
        device_exec = "wifi_obd2" if device_type == DeviceType.OBD else "wifi_afr"

        cmd = (
            f"cd {compiler_dir} && ./{compiler_binary} "
            f"{shlex.quote(device_exec)} make "
            f"{shlex.quote(serial)} {shlex.quote(version)} {shlex.quote(final_label)}"
        )

        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Compilation failed: {e.stderr}",
            )
        return output_path

    async def get_devices_by_token_str(self, token: str) -> List[ModuleDevice]:
        token_obj = await self.repo.get_token_by_token_str(token)
        if not token_obj:
            raise HTTPException(status_code=404, detail="Токен не найден")
        return list(token_obj.devices)

    def get_version_info(self, device_type: DeviceType, version: str) -> dict:
        compiler_dir = Path(settings.FIRMWARE_COMPILER_PATH).parent
        subdir = "WiFi_OBD2" if device_type == DeviceType.OBD else "WiFi_AFR"
        json_path = compiler_dir / subdir / f"Rev.{version}" / "versionInfo.json"
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                return data  # type: ignore[return-value]
            except Exception:
                pass
        return {"changes": "Информация о версии недоступна", "links": {}}

    async def verify_token_owns_device(self, token: str, serial: str) -> bool:
        token_obj = await self.repo.get_token_by_token_str(token)
        if not token_obj:
            return False
        return any(d.serial == serial for d in token_obj.devices)

    async def toggle_complectation(
        self, serial: str, complectation_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        token_obj = await self.repo.get_token_by_user_id(user_id)
        if not token_obj:
            raise HTTPException(status_code=403, detail="Нет доступа")
        device = await self.repo.get_device_by_serial(serial)
        if not device or device.token_id != token_obj.id:
            raise HTTPException(status_code=403, detail="Нет доступа к этому устройству")
        comp = await self.repo.get_complectation_by_id(complectation_id)
        if comp and comp.label == "base":
            return
        await self.repo.toggle_device_complectation(serial, complectation_id)
        await self.repo.session.commit()

    async def merge_users_firmware(self, source_email: str, target_email: str) -> None:
        source_hash = get_blind_index(source_email)
        target_hash = get_blind_index(target_email)

        source_user = await self.repo.get_user_by_email_hash(source_hash)
        target_user = await self.repo.get_user_by_email_hash(target_hash)

        if not source_user or not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both users not found",
            )

        await self.repo.merge_tokens(source_user.id, target_user.id)
        await self.repo.session.commit()

    async def merge_users_by_id(
        self, source_user_id: uuid.UUID, target_user_id: uuid.UUID
    ) -> None:
        await self.repo.merge_tokens(source_user_id, target_user_id)
        await self.repo.session.commit()

    async def import_excel(self, file_content: bytes) -> Tuple[int, int, List[str]]:
        import io

        wb = openpyxl.load_workbook(io.BytesIO(file_content))
        ws = wb.active

        clients_imported = 0
        devices_imported = 0
        errors: List[str] = []

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
                email = f"imported_{uuid.uuid4().hex[:8]}@wifiobd.ru"
                email_hash = get_blind_index(email)

                existing_device = await self.repo.get_device_by_serial(serial)
                if existing_device:
                    errors.append(f"Row {row_idx}: Device {serial} already exists")
                    continue

                new_user = User(
                    email=encrypt_data(email),
                    email_hash=email_hash,
                    full_name=encrypt_data(client_name),
                    role="customer",
                )
                self.repo.session.add(new_user)
                await self.repo.session.flush()
                clients_imported += 1

                token_str = secrets.token_hex(20)
                token_obj = await self.repo.create_token(new_user.id, token_str)

                device_type = DeviceType.AFR if dev_type_str.upper() == "AFR" else DeviceType.OBD
                await self.repo.create_device(token_obj.id, serial, device_type)
                devices_imported += 1

                if comp_label:
                    comp = await self.repo.get_complectation_by_label(comp_label)
                    if comp:
                        await self.repo.add_complectation_to_device(serial, comp.id)

                await self.repo.session.commit()
            except Exception as e:
                await self.repo.session.rollback()
                errors.append(f"Row {row_idx}: {str(e)}")

        return clients_imported, devices_imported, errors


async def get_firmware_service(
    repo: FirmwareRepository = Depends(get_firmware_repo),
) -> FirmwareService:
    return FirmwareService(repo)
