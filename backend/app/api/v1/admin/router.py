# Module: api/v1/admin/router.py | Agent: backend-agent | Task: admin_router_complete
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query, HTTPException
from pydantic import BaseModel
from typing import Any, List, Optional
from sqlalchemy import select, func

from app.core.dependencies import require_admin, get_product_repo, get_db
from app.db.models.order import Order, OrderStatus, OrderItem
from app.db.models.product import ProductVariant, Product
from sqlalchemy.ext.asyncio import AsyncSession

# Services & Repositories
from app.api.v1.products.service import ProductService
from app.api.v1.products.repository import ProductRepository
from app.api.v1.products.schemas import ProductCreate, ProductUpdate, ProductRead
from app.api.v1.blog.service import BlogService, get_blog_service
from app.api.v1.blog.repository import BlogRepository, get_blog_repo
from app.api.v1.blog.schemas import BlogPostCreate, BlogPostUpdate
from app.api.v1.orders.service import OrderService
from app.api.v1.orders.repository import OrderRepository
from app.api.v1.users.repository import UserRepository
from app.api.v1.iot.repository import IoTRepository
from app.api.v1.cart.service import CartService
from .pages_router import router as pages_admin_router

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

# ─── Shared guard ────────────────────────────────────────────────────────────
AdminDep = Depends(require_admin)

# ─── Dependencies ─────────────────────────────────────────────────────────────
def get_user_repo(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)

def get_order_repo(session: AsyncSession = Depends(get_db)) -> OrderRepository:
    return OrderRepository(session)

def get_iot_repo(session: AsyncSession = Depends(get_db)) -> IoTRepository:
    return IoTRepository(session)

async def get_admin_order_service(
    order_repo: OrderRepository = Depends(get_order_repo),
    product_repo: ProductRepository = Depends(get_product_repo),
    session: AsyncSession = Depends(get_db)
) -> OrderService:
    # CartService not strictly needed for admin status updates, but required by OrderService constructor
    return OrderService(order_repo, CartService(None, session), product_repo, session)

# ─── Schemas ─────────────────────────────────────────────────────────────────
class SalesAnalytics(BaseModel):
    total_revenue: float
    orders_count: int
    paid_orders_count: int
    top_products: List[dict]

class UserBlockRequest(BaseModel):
    is_active: bool

# ─── Dashboard / Analytics ───────────────────────────────────────────────────
@router.get("/dashboard", response_model=SalesAnalytics)
async def get_dashboard(
    _admin: User = AdminDep,
    session: AsyncSession = Depends(get_db)
) -> Any:
    """Return real sales analytics summary from DB."""
    # Total revenue from paid orders
    revenue_stmt = select(func.sum(Order.total_amount)).where(Order.status.in_([OrderStatus.PAID, OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED]))
    revenue_res = await session.execute(revenue_stmt)
    total_revenue = float(revenue_res.scalar() or 0.0)

    # Orders counts
    count_stmt = select(func.count(Order.id))
    total_orders = (await session.execute(count_stmt)).scalar() or 0
    
    paid_count_stmt = select(func.count(Order.id)).where(Order.status == OrderStatus.PAID)
    paid_orders = (await session.execute(paid_count_stmt)).scalar() or 0

    # Top products aggregation
    top_products_stmt = (
        select(
            Product.name,
            func.sum(OrderItem.quantity).label("sold_quantity")
        )
        .join(OrderItem, ProductVariant.id == OrderItem.product_variant_id)
        .join(Product, Product.id == ProductVariant.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status.in_([OrderStatus.PAID, OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED]))
        .group_by(Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
    )
    top_products_res = await session.execute(top_products_stmt)
    top_products = [{"name": row.name, "sold_quantity": row.sold_quantity} for row in top_products_res.all()]

    return SalesAnalytics(
        total_revenue=total_revenue,
        orders_count=total_orders,
        paid_orders_count=paid_orders,
        top_products=top_products
    )

# ─── Products ────────────────────────────────────────────────────────────────
@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    return await service.create_product(payload)

@router.put("/products/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    return await service.update_product(product_id, payload)

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> None:
    await service.delete_product(product_id)

# ─── Orders ──────────────────────────────────────────────────────────────────
@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: UUID,
    new_status: OrderStatus,
    _admin: User = AdminDep,
    service: OrderService = Depends(get_admin_order_service)
) -> Any:
    return await service.update_order_status(order_id, new_status)

# ─── Blog ────────────────────────────────────────────────────────────────────
@router.post("/blog/posts", status_code=status.HTTP_201_CREATED)
async def create_blog_post(
    body: BlogPostCreate,
    _admin: User = AdminDep,
    service: BlogService = Depends(get_blog_service)
) -> Any:
    return await service.create_post(author_id=_admin.id, data=body)

@router.put("/blog/posts/{post_id}")
async def update_blog_post(
    post_id: UUID,
    body: BlogPostUpdate,
    _admin: User = AdminDep,
    service: BlogService = Depends(get_blog_service)
) -> Any:
    return await service.update_post(post_id, body)

@router.delete("/blog/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog_post(
    post_id: UUID,
    _admin: User = AdminDep,
    service: BlogService = Depends(get_blog_service)
) -> None:
    success = await service.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")

# ─── Customers ───────────────────────────────────────────────────────────────
@router.put("/users/{user_id}/block")
async def block_user(
    user_id: UUID,
    body: UserBlockRequest,
    _admin: User = AdminDep,
    repo: UserRepository = Depends(get_user_repo)
) -> Any:
    user = await repo.update(user_id, is_active=body.is_active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": str(user_id), "is_active": user.is_active}

# ─── IoT monitoring ──────────────────────────────────────────────────────────
@router.get("/iot/devices")
async def list_all_devices(
    _admin: User = AdminDep,
    repo: IoTRepository = Depends(get_iot_repo)
) -> Any:
    devices = await repo.list_all()
    return {"items": [
        {
            "id": str(d.id),
            "device_uid": d.device_uid,
            "name": d.name,
            "model": d.model,
            "user_id": str(d.user_id),
            "last_seen_at": d.last_seen_at.isoformat() if d.last_seen_at else None,
            "is_active": d.is_active
        } for d in devices
    ]}

# ─── Pages ───────────────────────────────────────────────────────────────────
router.include_router(pages_admin_router)
