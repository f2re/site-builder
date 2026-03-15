import pytest
from uuid import uuid4

@pytest.mark.anyio
async def test_create_static_page(client, admin_token):
    payload = {
        "title": "Test Page",
        "slug": "test-page",
        "content": "<h1>Test</h1>",
        "is_active": True
    }
    
    response = await client.post(
        "/api/v1/admin/pages",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["slug"] == payload["slug"]
    assert "created_at" in data
    assert "updated_at" in data

@pytest.mark.anyio
async def test_update_static_page(client, admin_token):
    # Create page first
    create_payload = {
        "title": "Initial Title",
        "slug": "initial-slug",
        "content": "Initial content"
    }
    create_resp = await client.post(
        "/api/v1/admin/pages",
        json=create_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_resp.status_code == 200
    page_id = create_resp.json()["id"]
    
    # Update it
    update_payload = {
        "title": "Updated Title",
        "content": "Updated content"
    }
    response = await client.patch(
        f"/api/v1/admin/pages/{page_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert "updated_at" in data
