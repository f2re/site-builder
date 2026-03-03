import pytest
import uuid
from httpx import AsyncClient
from app.db.models.order import Order, OrderStatus
from app.db.models.user import User
from app.core.security import create_access_token, get_password_hash, get_blind_index

@pytest.mark.asyncio
async def test_admin_stats_aggregation(client: AsyncClient, db_session):
    # Setup Admin
    admin_id = uuid.uuid4()
    admin_email = "admin-stats-test@example.com"
    admin = User(
        id=admin_id,
        email=admin_email,
        email_hash=get_blind_index(admin_email),
        hashed_password=get_password_hash("password"), 
        role="admin", 
        is_active=True
    )
    db_session.add(admin)
    
    # Setup Customers
    u1_id = uuid.uuid4()
    u2_id = uuid.uuid4()
    e1, e2 = "customer1@test.com", "customer2@test.com"
    u1 = User(id=u1_id, email=e1, email_hash=get_blind_index(e1), hashed_password="...", role="customer", is_active=True)
    u2 = User(id=u2_id, email=e2, email_hash=get_blind_index(e2), hashed_password="...", role="customer", is_active=True)
    db_session.add_all([u1, u2])
    await db_session.flush()
    
    # Create Orders
    # PAID (counts as revenue)
    o1 = Order(user_id=u1_id, total_amount=1500.0, status=OrderStatus.PAID)
    # DELIVERED (counts as revenue)
    o2 = Order(user_id=u2_id, total_amount=2500.0, status=OrderStatus.DELIVERED)
    # PENDING (does NOT count)
    o3 = Order(user_id=u1_id, total_amount=5000.0, status=OrderStatus.PENDING_PAYMENT)
    
    db_session.add_all([o1, o2, o3])
    await db_session.commit()

    admin_token = create_access_token(subject=str(admin_id), role="admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = await client.get("/api/v1/admin/stats", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    
    # Total users: admin + 2 customers = 3
    assert data["users_count"] >= 3
    # Total revenue: 1500 + 2500 = 4000
    assert float(data["total_revenue"]) == 4000.0
    # Orders count: 3
    assert data["orders_count"] == 3
