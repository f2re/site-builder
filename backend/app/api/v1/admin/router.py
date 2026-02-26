# Module: api/v1/admin/router.py | Agent: backend-agent | Task: stage2_rbac
"""
Admin panel API — accessible only to users with role='admin' or is_superuser=True.

Sections:
  GET  /admin/dashboard          — sales analytics summary
  ---  Products ---
  GET  /admin/products           — list all products (stub)
  POST /admin/products           — create product (stub)
  PUT  /admin/products/{id}      — update product (stub)
  DEL  /admin/products/{id}      — delete product (stub)
  PUT  /admin/products/{id}/stock — update stock / availability
  ---  Orders ---
  GET  /admin/orders             — list orders with filters
  PUT  /admin/orders/{id}/status — manually change order status
  ---  Blog ---
  GET  /admin/blog/posts         — list blog posts (all statuses)
  POST /admin/blog/posts         — create blog post
  PUT  /admin/blog/posts/{id}    — update blog post
  DEL  /admin/blog/posts/{id}    — delete blog post
  GET  /admin/blog/comments      — list pending comments
  PUT  /admin/blog/comments/{id}/approve — approve comment
  DEL  /admin/blog/comments/{id}         — reject/delete comment
  ---  Customers ---
  GET  /admin/users              — list all users
  PUT  /admin/users/{id}/block   — block/unblock user
  ---  IoT ---
  GET  /admin/iot/devices        — all registered devices
  GET  /admin/iot/status         — Redis queue lengths & latency
"""
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel
from typing import Any

from app.core.dependencies import require_admin
from app.db.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

# ─── Shared guard ────────────────────────────────────────────────────────────
AdminDep = Depends(require_admin)


# ─── Schemas (inline, will be moved to admin/schemas.py in next iterations) ──

class SalesAnalytics(BaseModel):
    total_revenue: float
    orders_count: int
    paid_orders_count: int
    top_products: list[dict]


class StockUpdateRequest(BaseModel):
    quantity: int


class OrderStatusUpdateRequest(BaseModel):
    status: str  # pending | paid | processing | shipped | delivered | cancelled


class BlogPostCreate(BaseModel):
    title: str
    slug: str
    content: str
    status: str = "draft"  # draft | published | archived
    meta_title: str | None = None
    meta_description: str | None = None


class BlogPostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    status: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None


class UserBlockRequest(BaseModel):
    is_active: bool


# ─── Dashboard / Analytics ───────────────────────────────────────────────────

@router.get("/dashboard", response_model=SalesAnalytics)
async def get_dashboard(
    _admin: User = AdminDep,
) -> Any:
    """
    Return sales analytics summary.
    TODO: replace stub with real DB aggregation via OrderRepository.
    """
    return SalesAnalytics(
        total_revenue=0.0,
        orders_count=0,
        paid_orders_count=0,
        top_products=[],
    )


# ─── Products ────────────────────────────────────────────────────────────────

@router.get("/products")
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _admin: User = AdminDep,
) -> Any:
    """List all products (paginated). TODO: wire ProductRepository."""
    return {"items": [], "total": 0, "page": page, "per_page": per_page}


@router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: dict,
    _admin: User = AdminDep,
) -> Any:
    """Create a new product. TODO: wire ProductService."""
    return {"detail": "stub — product creation not yet implemented"}


@router.put("/products/{product_id}")
async def update_product(
    product_id: UUID,
    payload: dict,
    _admin: User = AdminDep,
) -> Any:
    """Update product data. TODO: wire ProductService."""
    return {"detail": "stub — product update not yet implemented", "id": str(product_id)}


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    _admin: User = AdminDep,
) -> None:
    """Delete a product. TODO: wire ProductService."""
    return


@router.put("/products/{product_id}/stock")
async def update_stock(
    product_id: UUID,
    body: StockUpdateRequest,
    _admin: User = AdminDep,
) -> Any:
    """Update product stock / availability. TODO: wire InventoryService + Redis."""
    return {"product_id": str(product_id), "new_quantity": body.quantity}


# ─── Orders ──────────────────────────────────────────────────────────────────

@router.get("/orders")
async def list_orders(
    order_status: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _admin: User = AdminDep,
) -> Any:
    """List all orders. TODO: wire OrderRepository with filters."""
    return {"items": [], "total": 0, "page": page, "per_page": per_page}


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: UUID,
    body: OrderStatusUpdateRequest,
    _admin: User = AdminDep,
) -> Any:
    """Manually change order status. TODO: wire OrderService + Celery notifications."""
    return {"order_id": str(order_id), "status": body.status}


# ─── Blog ────────────────────────────────────────────────────────────────────

@router.get("/blog/posts")
async def list_blog_posts(
    post_status: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _admin: User = AdminDep,
) -> Any:
    """List blog posts (all statuses: draft, published, archived). TODO: wire BlogRepository."""
    return {"items": [], "total": 0, "page": page, "per_page": per_page}


@router.post("/blog/posts", status_code=status.HTTP_201_CREATED)
async def create_blog_post(
    body: BlogPostCreate,
    _admin: User = AdminDep,
) -> Any:
    """Create a blog post. TODO: wire BlogService + Meilisearch indexing."""
    return {"detail": "stub — blog post creation not yet implemented", "slug": body.slug}


@router.put("/blog/posts/{post_id}")
async def update_blog_post(
    post_id: UUID,
    body: BlogPostUpdate,
    _admin: User = AdminDep,
) -> Any:
    """Update a blog post. TODO: wire BlogService."""
    return {"detail": "stub — blog post update not yet implemented", "id": str(post_id)}


@router.delete("/blog/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog_post(
    post_id: UUID,
    _admin: User = AdminDep,
) -> None:
    """Delete a blog post. TODO: wire BlogService."""
    return


@router.get("/blog/comments")
async def list_pending_comments(
    _admin: User = AdminDep,
) -> Any:
    """List comments pending moderation. TODO: wire CommentRepository."""
    return {"items": []}


@router.put("/blog/comments/{comment_id}/approve")
async def approve_comment(
    comment_id: UUID,
    _admin: User = AdminDep,
) -> Any:
    """Approve a pending comment. TODO: wire CommentService."""
    return {"comment_id": str(comment_id), "status": "approved"}


@router.delete("/blog/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    _admin: User = AdminDep,
) -> None:
    """Reject / delete a comment. TODO: wire CommentService."""
    return


# ─── Customers ───────────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _admin: User = AdminDep,
) -> Any:
    """List all customers. TODO: wire UserRepository with pagination."""
    return {"items": [], "total": 0, "page": page, "per_page": per_page}


@router.put("/users/{user_id}/block")
async def block_user(
    user_id: UUID,
    body: UserBlockRequest,
    _admin: User = AdminDep,
) -> Any:
    """Block or unblock a user. TODO: wire UserRepository."""
    return {"user_id": str(user_id), "is_active": body.is_active}


# ─── IoT monitoring ──────────────────────────────────────────────────────────

@router.get("/iot/devices")
async def list_all_devices(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _admin: User = AdminDep,
) -> Any:
    """List all registered IoT/OBD2 devices across all users. TODO: wire DeviceRepository."""
    return {"items": [], "total": 0, "page": page, "per_page": per_page}


@router.get("/iot/status")
async def iot_status(
    _admin: User = AdminDep,
) -> Any:
    """
    Redis queue lengths, stream lag, last event timestamps.
    TODO: wire RedisClient to query XLEN / XINFO on IoT streams.
    """
    return {
        "redis_stream_iot_data": {"length": 0, "lag": 0},
        "active_devices": 0,
    }
