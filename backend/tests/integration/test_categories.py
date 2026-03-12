import pytest
import uuid
from httpx import AsyncClient
from app.core.security import create_access_token, get_password_hash, get_blind_index
from app.db.models.user import User

@pytest.mark.anyio
async def test_category_product_count(client: AsyncClient, db_session):
    # 1. Setup Admin
    admin_id = uuid.uuid4()
    email = f"admin-cat-{uuid.uuid4().hex[:6]}@example.com"
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

    # 2. Create Category
    cat_resp = await client.post(
        "/api/v1/admin/categories", 
        json={"name": "Test Category", "slug": f"test-cat-{uuid.uuid4().hex[:6]}"}, 
        headers=headers
    )
    assert cat_resp.status_code == 201
    cat_id = cat_resp.json()["id"]

    # 3. Create active and inactive products in this category
    # Product 1: Active
    p1_data = {
        "name": "Active P",
        "slug": f"active-p-{uuid.uuid4().hex[:6]}",
        "category_id": cat_id,
        "is_active": True,
        "variants": [{"name": "V1", "sku": f"A-{uuid.uuid4().hex[:6]}", "price": 100}]
    }
    await client.post("/api/v1/admin/products", json=p1_data, headers=headers)

    # Product 2: Inactive
    p2_data = {
        "name": "Inactive P",
        "slug": f"inactive-p-{uuid.uuid4().hex[:6]}",
        "category_id": cat_id,
        "is_active": False,
        "variants": [{"name": "V1", "sku": f"I-{uuid.uuid4().hex[:6]}", "price": 100}]
    }
    await client.post("/api/v1/admin/products", json=p2_data, headers=headers)

    # 4. Check category list (Admin: active_only=False)
    list_resp = await client.get("/api/v1/admin/categories", headers=headers)
    assert list_resp.status_code == 200
    cats = list_resp.json()
    test_cat = next(c for c in cats if c["id"] == cat_id)
    # Admin should see BOTH products in count (fixed behavior)
    assert test_cat["product_count"] == 2

    # 5. Check public categories (active_only=True)
    pub_resp = await client.get("/api/v1/products/categories")
    assert pub_resp.status_code == 200
    pub_cats = pub_resp.json()["items"]
    
    def find_in_tree(items, target_id):
        for item in items:
            if item["id"] == target_id:
                return item
            if item.get("children"):
                found = find_in_tree(item["children"], target_id)
                if found:
                    return found
        return None

    pub_test_cat = find_in_tree(pub_cats, cat_id)
    assert pub_test_cat is not None
    # Public should only see ACTIVE product
    assert pub_test_cat["product_count"] == 1
