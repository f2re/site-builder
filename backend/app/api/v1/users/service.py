# Module: api/v1/users/service.py | Agent: backend-agent | Task: p11_backend_user_addresses
import re
from uuid import UUID
from fastapi import HTTPException, status


def validate_phone_e164(phone: str) -> str:
    """Validate phone in E.164 format (+[country][number])."""
    pattern = r'^\+[1-9]\d{1,14}$'
    if not re.match(pattern, phone):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Phone must be in E.164 format (e.g., +79991234567)"
        )
    return phone


class DeliveryAddressService:
    def __init__(self, repo):
        self.repo = repo

    async def create_address(self, user_id: UUID, name: str, recipient_name: str, recipient_phone: str,
                             address_type: str, full_address: str, city: str, postal_code: str | None,
                             provider: str, pickup_point_code: str | None, is_default: bool):
        """Create address with validation."""
        validate_phone_e164(recipient_phone)

        if is_default:
            await self.repo.set_default(user_id, None)

        return await self.repo.create(
            user_id=user_id,
            name=name,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            address_type=address_type,
            full_address=full_address,
            city=city,
            postal_code=postal_code,
            provider=provider,
            pickup_point_code=pickup_point_code,
            is_default=is_default
        )

    async def update_address(self, address_id: UUID, **kwargs):
        """Update address with validation."""
        if "recipient_phone" in kwargs and kwargs["recipient_phone"]:
            validate_phone_e164(kwargs["recipient_phone"])
        return await self.repo.update(address_id, **kwargs)
