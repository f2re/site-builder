# Module: tests/unit/test_delivery_address_service | Agent: testing-agent | Task: p11_testing_addresses_tracking
import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from app.api.v1.users.service import validate_phone_e164, DeliveryAddressService


def test_validate_phone_e164_valid():
    """Valid E.164 phone passes."""
    assert validate_phone_e164("+79991234567") == "+79991234567"
    assert validate_phone_e164("+12025551234") == "+12025551234"


def test_validate_phone_e164_invalid():
    """Invalid E.164 phone raises HTTPException."""
    with pytest.raises(HTTPException) as exc:
        validate_phone_e164("89991234567")
    assert exc.value.status_code == 422

    with pytest.raises(HTTPException):
        validate_phone_e164("invalid")


@pytest.mark.anyio
async def test_service_create_address_validates_phone():
    """Service validates phone before creating."""
    repo = AsyncMock()
    service = DeliveryAddressService(repo)

    with pytest.raises(HTTPException) as exc:
        await service.create_address(
            user_id="user-id",
            name="Home",
            recipient_name="John",
            recipient_phone="invalid-phone",
            address_type="home",
            full_address="Addr",
            city="Moscow",
            postal_code=None,
            provider="cdek",
            pickup_point_code=None,
            is_default=False
        )
    assert exc.value.status_code == 422


@pytest.mark.anyio
async def test_service_create_default_unsets_others():
    """Service unsets other defaults when is_default=True."""
    repo = AsyncMock()
    repo.create = AsyncMock(return_value={"id": "new-addr"})
    service = DeliveryAddressService(repo)

    await service.create_address(
        user_id="user-id",
        name="Home",
        recipient_name="John",
        recipient_phone="+79991234567",
        address_type="home",
        full_address="Addr",
        city="Moscow",
        postal_code=None,
        provider="cdek",
        pickup_point_code=None,
        is_default=True
    )

    repo.set_default.assert_called_once_with("user-id", None)
    repo.create.assert_called_once()
