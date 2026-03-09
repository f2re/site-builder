# Module: tests/integration/test_user_addresses_api | Agent: testing-agent | Task: p11_testing_addresses_tracking
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_addresses_empty(client: AsyncClient, admin_token: str):
    """List addresses returns empty array for new user."""
    response = await client.get(
        "/api/v1/users/me/addresses",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_address(client: AsyncClient, admin_token: str):
    """Create new delivery address."""
    payload = {
        "name": "Home",
        "recipient_name": "John Doe",
        "recipient_phone": "+79991234567",
        "address_type": "home",
        "full_address": "123 Main St",
        "city": "Moscow",
        "postal_code": "101000",
        "provider": "cdek",
        "pickup_point_code": None,
        "is_default": True
    }
    response = await client.post(
        "/api/v1/users/me/addresses",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Home"
    assert data["recipient_phone"] == "+79991234567"
    assert data["is_default"] is True


@pytest.mark.asyncio
async def test_create_address_invalid_phone(client: AsyncClient, admin_token: str):
    """Create address with invalid phone fails."""
    payload = {
        "name": "Home",
        "recipient_name": "John",
        "recipient_phone": "invalid",
        "address_type": "home",
        "full_address": "Addr",
        "city": "Moscow",
        "provider": "cdek",
        "is_default": False
    }
    response = await client.post(
        "/api/v1/users/me/addresses",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_address(client: AsyncClient, admin_token: str):
    """Update existing address."""
    create_payload = {
        "name": "Old",
        "recipient_name": "John",
        "recipient_phone": "+79991111111",
        "address_type": "home",
        "full_address": "Old Addr",
        "city": "Moscow",
        "provider": "cdek",
        "is_default": False
    }
    create_resp = await client.post(
        "/api/v1/users/me/addresses",
        json=create_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    addr_id = create_resp.json()["id"]

    update_payload = {"name": "New"}
    response = await client.patch(
        f"/api/v1/users/me/addresses/{addr_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New"


@pytest.mark.asyncio
async def test_delete_address(client: AsyncClient, admin_token: str):
    """Delete address."""
    create_payload = {
        "name": "ToDelete",
        "recipient_name": "John",
        "recipient_phone": "+79991111111",
        "address_type": "home",
        "full_address": "Addr",
        "city": "Moscow",
        "provider": "cdek",
        "is_default": False
    }
    create_resp = await client.post(
        "/api/v1/users/me/addresses",
        json=create_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    addr_id = create_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/users/me/addresses/{addr_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204

    list_resp = await client.get(
        "/api/v1/users/me/addresses",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert len(list_resp.json()) == 0


@pytest.mark.asyncio
async def test_set_default_address(client: AsyncClient, admin_token: str):
    """Set address as default."""
    await client.post(
        "/api/v1/users/me/addresses",
        json={
            "name": "A1", "recipient_name": "N1", "recipient_phone": "+79991111111",
            "address_type": "home", "full_address": "Addr1", "city": "Moscow",
            "provider": "cdek", "is_default": True
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    addr2 = await client.post(
        "/api/v1/users/me/addresses",
        json={
            "name": "A2", "recipient_name": "N2", "recipient_phone": "+79992222222",
            "address_type": "home", "full_address": "Addr2", "city": "Moscow",
            "provider": "cdek", "is_default": False
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    addr2_id = addr2.json()["id"]
    response = await client.post(
        f"/api/v1/users/me/addresses/{addr2_id}/set-default",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_default"] is True
