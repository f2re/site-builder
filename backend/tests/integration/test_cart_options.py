import pytest
import uuid
from httpx import AsyncClient
from app.db.models.product import Product, ProductVariant, ProductOptionGroup, ProductOptionValue
from redis.asyncio import Redis

@pytest.mark.asyncio
async def test_cart_options_flow(client: AsyncClient, db_session, redis_client: Redis):
    # 1. Setup Product with Options
    p_id = uuid.uuid4()
    v_id = uuid.uuid4()
    product = Product(id=p_id, name="Configurable Product", slug="config-prod")
    variant = ProductVariant(id=v_id, product_id=p_id, sku="CONFIG-SKU", price=1000.0, stock_quantity=10)
    
    g_id = uuid.uuid4()
    group = ProductOptionGroup(id=g_id, product_id=p_id, name="Color", is_required=True)
    
    val1_id = uuid.uuid4()
    val1 = ProductOptionValue(id=val1_id, group_id=g_id, name="Red", price_modifier=100.0)
    
    val2_id = uuid.uuid4()
    val2 = ProductOptionValue(id=val2_id, group_id=g_id, name="Blue", price_modifier=200.0)
    
    db_session.add_all([product, variant, group, val1, val2])
    await db_session.commit()

    # Pre-warm Redis stock
    await redis_client.set(f"stock:{v_id}", 10)

    # 2. Add to cart with Red option
    add_resp = await client.post("/api/v1/cart/add", json={
        "product_id": str(v_id),
        "quantity": 1,
        "selected_option_value_ids": [str(val1_id)]
    })
    assert add_resp.status_code == 200
    cart_session = add_resp.cookies.get("cart_session")
    cookies = {"cart_session": cart_session} if cart_session else {}
    
    data = add_resp.json()
    assert len(data["items"]) == 1
    item1 = data["items"][0]
    assert float(item1["price_rub"]) == 1100.0 # 1000 + 100
    item1_id = item1["item_id"]
    
    # 3. Add same variant with Blue option (should be a DIFFERENT item in cart)
    add_resp2 = await client.post("/api/v1/cart/add", json={
        "product_id": str(v_id),
        "quantity": 1,
        "selected_option_value_ids": [str(val2_id)]
    }, cookies=cookies)
    
    assert add_resp2.status_code == 200
    data2 = add_resp2.json()
    assert len(data2["items"]) == 2
    
    # 4. Update quantity of Blue item
    item2 = next(i for i in data2["items"] if i["item_id"] != item1_id)
    item2_id = item2["item_id"]
    assert float(item2["price_rub"]) == 1200.0
    
    update_resp = await client.patch(f"/api/v1/cart/{item2_id}", json={"quantity": 3}, cookies=cookies)
    assert update_resp.status_code == 200
    data3 = update_resp.json()
    item2_updated = next(i for i in data3["items"] if i["item_id"] == item2_id)
    assert item2_updated["quantity"] == 3
    assert float(data3["subtotal_rub"]) == 1100.0 + (1200.0 * 3)

    # 5. Remove item
    remove_resp = await client.delete(f"/api/v1/cart/{item1_id}", cookies=cookies)
    assert remove_resp.status_code == 200
    data4 = remove_resp.json()
    assert len(data4["items"]) == 1
    assert data4["items"][0]["item_id"] == item2_id
