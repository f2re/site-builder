# Module: tests/integration/test_addresses.py | Agent: backend-agent | Task: p11_backend_user_addresses
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_address_management(client: AsyncClient):
    # 1. Register & Login
    reg_payload = {
        "email": "addr_user@example.com",
        "password": "securepassword123",
        "full_name": "Addr User"
    }
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "addr_user@example.com",
        "password": "securepassword123"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Add address
    addr_payload = {
        "name": "My Home",
        "recipient_name": "Addr User",
        "recipient_phone": "+79991234567",
        "address_type": "home",
        "full_address": "Moscow, Tverskaya str, 1",
        "city": "Moscow",
        "provider": "cdek",
        "is_default": True
    }
    create_resp = await client.post("/api/v1/users/me/addresses", json=addr_payload, headers=headers)
    assert create_resp.status_code == 201
    addr_data = create_resp.json()
    assert addr_data["name"] == "My Home"
    assert addr_data["recipient_phone"] == "+79991234567"
    addr_id = addr_data["id"]

    # 3. List addresses
    list_resp = await client.get("/api/v1/users/me/addresses", headers=headers)
    assert list_resp.status_code == 200
    addresses = list_resp.json()
    assert len(addresses) == 1
    assert addresses[0]["id"] == addr_id
    assert addresses[0]["name"] == "My Home"

    # 4. Update address
    update_payload = {"name": "Work Address"}
    patch_resp = await client.patch(f"/api/v1/users/me/addresses/{addr_id}", json=update_payload, headers=headers)
    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == "Work Address"

    # 5. Set default (create second address first)
    addr2_payload = {
        "name": "Alt Home",
        "recipient_name": "Addr User",
        "recipient_phone": "+79991234567",
        "address_type": "home",
        "full_address": "Moscow, Arbat str, 10",
        "city": "Moscow",
        "provider": "cdek",
        "is_default": False
    }
    create2_resp = await client.post("/api/v1/users/me/addresses", json=addr2_payload, headers=headers)
    addr2_id = create2_resp.json()["id"]
    
    # Set second as default
    def_resp = await client.post(f"/api/v1/users/me/addresses/{addr2_id}/set-default", headers=headers)
    assert def_resp.status_code == 200
    assert def_resp.json()["is_default"] is True
    
    # Verify first is no longer default
    list_resp2 = await client.get("/api/v1/users/me/addresses", headers=headers)
    addresses2 = list_resp2.json()
    # Sorted by is_default DESC, so addr2 (id2) should be first
    assert addresses2[0]["id"] == addr2_id
    assert addresses2[0]["is_default"] is True
    assert addresses2[1]["id"] == addr_id
    assert addresses2[1]["is_default"] is False

    # 6. Delete address
    del_resp = await client.delete(f"/api/v1/users/me/addresses/{addr_id}", headers=headers)
    assert del_resp.status_code == 204
    
    # 7. Verify only one left
    list_resp3 = await client.get("/api/v1/users/me/addresses", headers=headers)
    assert len(list_resp3.json()) == 1
    assert list_resp3.json()[0]["id"] == addr2_id
