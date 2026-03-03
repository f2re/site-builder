import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_auth_flow(client: AsyncClient):
    # 1. Register
    reg_payload = {
        "email": "user@example.com",
        "password": "securepassword123",
        "full_name": "Test User"
    }
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    
    # 2. Login
    login_payload = {
        "email": "user@example.com",
        "password": "securepassword123"
    }
    login_resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "user@example.com"
    token = data["access_token"]
    
    # 3. Access Admin (should fail for regular user)
    admin_resp = await client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert admin_resp.status_code == 403

    # 4. Get Profile
    profile_resp = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert profile_resp.status_code == 200
    assert profile_resp.json()["email"] == "user@example.com"
