import pytest
import uuid
from httpx import AsyncClient
from app.core.security import create_access_token, get_password_hash, get_blind_index
from app.db.models.user import User
from unittest.mock import patch, AsyncMock, MagicMock
import base64

# 1x1 black pixel PNG
VALID_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)

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

    # 3. Upload image (Mock storage_client AND the celery task)
    mock_storage = MagicMock()
    mock_storage.save_file = AsyncMock(return_value=None)
    mock_storage.read_file = AsyncMock(return_value=VALID_PNG)
    mock_storage.get_public_url.return_value = "https://media.test/test.jpg"
    mock_storage.delete_file = AsyncMock(return_value=None)
    
    with patch("app.api.v1.products.service.storage_client", mock_storage), \
         patch("app.tasks.media.process_image_variants.delay") as mock_task:
        
        files = {"file": ("test.png", VALID_PNG, "image/png")}
        img_resp = await client.post(f"/api/v1/admin/products/{product_id}/images", files=files, headers=headers)
        
        assert img_resp.status_code == 201
        image_id = img_resp.json()["id"]
        assert mock_task.called
        
    # 4. Set as cover
    cover_resp = await client.put(f"/api/v1/admin/products/{product_id}/images/{image_id}/cover", headers=headers)
    assert cover_resp.status_code == 200

    # 5. Verify SEO and Content
    get_resp = await client.get("/api/v1/products/rich-product-test")
    assert get_resp.status_code == 200
    data = get_resp.json()
    
    assert data["content_json"] == content_json
    # Auto-generated meta_description check
    assert "This is a rich description test" in data["meta_description"]
    
    # Verify image exists in DB (even if formats are empty because task was mocked)
    from app.db.models.product import ProductImage
    from sqlalchemy import select
    stmt = select(ProductImage).where(ProductImage.id == uuid.UUID(image_id))
    result = await db_session.execute(stmt)
    img_db = result.scalar_one()
    assert img_db is not None

