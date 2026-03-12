import pytest
import uuid
from datetime import datetime, timezone
from httpx import AsyncClient
from app.db.models.order import Order, OrderStatus
from app.db.models.user import User
from app.core.security import create_access_token, get_password_hash, get_blind_index

@pytest.mark.anyio
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
    await db_session.commit()
    
    admin_token = create_access_token(subject=str(admin_id), role="admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Get baseline
    resp0 = await client.get("/api/v1/admin/stats", headers=headers)
    assert resp0.status_code == 200
    base_data = resp0.json()
    base_revenue = float(base_data["total_revenue"])
    base_users = int(base_data["users_count"])

    # Setup Customers
    u1_id = uuid.uuid4()
    u2_id = uuid.uuid4()
    e1, e2 = f"customer1-{u1_id}@test.com", f"customer2-{u2_id}@test.com"
    u1 = User(id=u1_id, email=e1, email_hash=get_blind_index(e1), hashed_password="...", role="customer", is_active=True)
    u2 = User(id=u2_id, email=e2, email_hash=get_blind_index(e2), hashed_password="...", role="customer", is_active=True)
    db_session.add_all([u1, u2])
    await db_session.flush()
    
    # Create Orders
    now = datetime.now(timezone.utc)
    # PAID (counts as revenue)
    o1 = Order(user_id=u1_id, total_amount=1500.0, status=OrderStatus.PAID, created_at=now)
    # DELIVERED (counts as revenue)
    o2 = Order(user_id=u2_id, total_amount=2500.0, status=OrderStatus.DELIVERED, created_at=now)
    # PENDING_PAYMENT (does NOT count for revenue, but counts for attention_stats)
    o3 = Order(user_id=u1_id, total_amount=5000.0, status=OrderStatus.PENDING_PAYMENT, created_at=now)
    # PENDING (counts for attention_stats)
    o4 = Order(user_id=u1_id, total_amount=1000.0, status=OrderStatus.PENDING, created_at=now)
    
    db_session.add_all([o1, o2, o3, o4])
    await db_session.commit()

    resp = await client.get("/api/v1/admin/stats", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    
    # Check relative changes
    assert int(data["users_count"]) - base_users == 2
    assert float(data["total_revenue"]) - base_revenue == 4000.0
    
    # Check attention_stats
    attn = data["attention_stats"]
    assert attn["new_orders"] >= 1
    assert attn["unpaid_orders"] >= 1
    assert attn["to_ship_orders"] >= 1  # PAID counts as to_ship
    
    # Check daily_stats
    daily = data["daily_stats"]
    assert len(daily) == 31  # last 30 days + today
    
    # Find today's stat
    today_str = now.date().isoformat()
    today_stat = next((s for s in daily if s["date"] == today_str), None)
    assert today_stat is not None
    assert today_stat["orders"] >= 2 # o1, o2 are paid/delivered
    assert today_stat["revenue"] >= 4000.0
