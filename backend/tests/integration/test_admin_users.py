import pytest
import uuid
from httpx import AsyncClient
from app.db.models.user import User
from app.core.security import create_access_token, get_blind_index

@pytest.mark.asyncio
async def test_get_user_full_details(client: AsyncClient, db_session):
    # Setup Admin
    admin_id = uuid.uuid4()
    admin_email = "admin-test@example.com"
    admin = User(
        id=admin_id,
        email=admin_email,
        email_hash=get_blind_index(admin_email),
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    
    # Setup Test User
    user_id = uuid.uuid4()
    user_email = "test-user@example.com"
    user = User(
        id=user_id,
        email=user_email,
        email_hash=get_blind_index(user_email),
        role="customer",
        is_active=True,
        full_name="Test User"
    )
    db_session.add(user)
    await db_session.commit()
    
    admin_token = create_access_token(subject=str(admin_id), role="admin")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = await client.get(f"/api/v1/admin/users/{user_id}/full", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user_id)
    assert data["email"] == user_email
    assert data["full_name"] == "Test User"
    assert "addresses" in data
    assert "orders" in data
    assert "devices" in data
    assert isinstance(data["addresses"], list)
    assert isinstance(data["orders"], list)
    assert isinstance(data["devices"], list)
