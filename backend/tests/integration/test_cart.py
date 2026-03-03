import pytest
import uuid
from httpx import AsyncClient
from app.db.models.product import Product, ProductVariant
from redis.asyncio import Redis

@pytest.mark.asyncio
async def test_cart_guest_flow(client: AsyncClient, db_session, redis_client: Redis):
    # 1. Setup Product
    p_id = uuid.uuid4()
    v_id = uuid.uuid4()
    product = Product(id=p_id, name="Test Product", slug="test-cart-prod")
    variant = ProductVariant(id=v_id, product_id=p_id, sku="CART-SKU", price=500.0, stock_quantity=10)
    db_session.add_all([product, variant])
    await db_session.commit()

    # Pre-warm Redis stock
    await redis_client.set(f"stock:{v_id}", 10)

    # 2. Add to cart (Guest)
    add_resp = await client.post("/api/v1/cart/add", json={
        "product_id": str(v_id),
        "quantity": 2
    })
    assert add_resp.status_code == 200
    add_data = add_resp.json()
    assert len(add_data["items"]) == 1
    
    # Extract cart_session cookie
    cart_session = add_resp.cookies.get("cart_session")
    
    # 3. Get Cart
    get_resp = await client.get("/api/v1/cart", cookies={"cart_session": cart_session} if cart_session else {})
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == str(v_id)
    assert data["items"][0]["quantity"] == 2
    assert float(data["subtotal_rub"]) == 1000.0
