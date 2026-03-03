import pytest
import uuid
from httpx import AsyncClient
from app.core.security import create_access_token, get_password_hash, get_blind_index
from app.db.models.user import User
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_rich_product_flow(client: AsyncClient, db_session):
    # 1. Setup Admin
    admin_id = uuid.uuid4()
    email = "admin-rich@example.com"
    admin = User(
        id=admin_id,
        email=email,
        email_hash=get_blind_index(email),
        hashed_password=get_password_hash("password"), 
        role="admin", 
        is_active=True
    )
    db_session.add(admin)
    await db_session.commit()
    
    admin_token = create_access_token(subject=str(admin_id), role="admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Create Rich Product
    content_json = {
        "type": "doc", 
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "This is a rich description test."}]}
        ]
    }
    product_data = {
        "name": "Rich Product Test",
        "slug": "rich-product-test",
        "content_json": content_json,
        "category_id": None,
        "variants": [{"name": "Default", "sku": "RICH-TEST-001", "price": 1000.0, "stock_quantity": 10}],
        "meta_title": "Custom Title",
        "meta_description": "" # Should be auto-generated
    }
    
    with patch("app.tasks.search.index_product_task.delay") as mock_index:
        resp = await client.post("/api/v1/admin/products", json=product_data, headers=headers)
        assert resp.status_code == 201
        product_id = resp.json()["id"]
        assert mock_index.called

    # 3. Upload image (Mock MinIO)
    with patch("app.api.v1.products.service.minio_client") as mock_minio:
        from unittest.mock import AsyncMock
        mock_minio.put_object = AsyncMock(return_value=None)
        mock_minio.get_public_url.return_value = "https://media.test/test.jpg"
        mock_minio.media_bucket = "media" # needed because it's accessed in service
        
        file_content = b"fake-image-binary"
        files = {"file": ("test.jpg", file_content, "image/jpeg")}
        img_resp = await client.post(f"/api/v1/admin/products/{product_id}/images", files=files, headers=headers)
        
        assert img_resp.status_code == 201
        image_id = img_resp.json()["id"]
        image_url = img_resp.json()["url"]
        assert image_url == "https://media.test/test.jpg"

    # 4. Set as cover
    cover_resp = await client.put(f"/api/v1/admin/products/{product_id}/images/{image_id}/cover", headers=headers)
    assert cover_resp.status_code == 200

    # 5. Verify SEO and Content
    get_resp = await client.get("/api/v1/products/rich-product-test")
    assert get_resp.status_code == 200
    data = get_resp.json()
    
    assert data["content_json"] == content_json
    assert data["og_image_url"] == "https://media.test/test.jpg"
    # Auto-generated meta_description check
    assert "This is a rich description test" in data["meta_description"]
