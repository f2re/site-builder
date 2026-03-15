# Module: api/v1/admin/router.py | Agent: backend-agent | Task: admin_devices_crud
import io
import uuid as _uuid_module
import openpyxl
from datetime import date, datetime, timedelta, timezone
from uuid import UUID
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import select, func, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin, get_product_repo, get_db, get_cart_service
from app.db.models.order import Order, OrderStatus, OrderItem
from app.db.models.product import ProductVariant, Product
from app.db.models.user import User
from app.db.models.user_device import UserDevice, DeviceModel
from app.api.v1.auth.schemas import UserResponse
from app.api.v1.admin.schemas import (
    AdminDeviceRead,
    AdminDeviceCreate,
    AdminDeviceUpdate,
    AdminUserFullResponse,
    MigrationJobResponse,
    MigrationStartRequest,
    MigrationStatusResponse,
)
from app.core.security import get_password_hash

# Services & Repositories
from app.api.v1.products.service import ProductService
from app.api.v1.products.repository import ProductRepository
from app.api.v1.products.schemas import (
    ProductCreate, ProductUpdate, ProductRead, ProductPagination,
    CategoryRead, CategoryCreate, CategoryUpdate, ProductImageRead,
    ProductOptionGroupSchema, ProductOptionGroupCreate, ProductOptionGroupUpdate,
    ProductOptionValueSchema, ProductOptionValueCreate, ProductOptionValueUpdate
)
from app.api.v1.blog.service import BlogService, get_blog_service
from app.api.v1.blog.schemas import BlogPostCreate, BlogPostUpdate
from app.integrations.local_storage import storage_client
from app.core.utils import sanitize_filename
from app.api.v1.orders.service import OrderService
from app.api.v1.orders.repository import OrderRepository
from app.api.v1.orders.schemas import OrderRead
from app.api.v1.users.repository import UserRepository, DeliveryAddressRepository
from app.api.v1.iot.repository import IoTRepository
from app.api.v1.cart.service import CartService
from app.api.v1.firmware.service import FirmwareService, get_firmware_service
from app.api.v1.firmware.schemas import (
    AdminAddDeviceRequest,
    ComplectationCreate,
    ComplectationRead,
    DeviceRead,
    ExcelImportResponse,
    MergeByIdRequest,
    UserMergeRequest,
)
from .pages_router import router as pages_admin_router

# Migration
from .migration_service import MigrationService
from .migration_repository import MigrationRepository
from app.db.models.migration import MigrationEntity

from app.core.logging import logger

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
    cart_service: CartService = Depends(get_cart_service),
    session: AsyncSession = Depends(get_db)
) -> OrderService:
    """Dependency factory for admin order management."""
    return OrderService(order_repo, cart_service, product_repo, session)

def get_address_repo(session: AsyncSession = Depends(get_db)) -> DeliveryAddressRepository:
    return DeliveryAddressRepository(session)

def get_migration_repo(session: AsyncSession = Depends(get_db)) -> MigrationRepository:
    return MigrationRepository(session)

def get_migration_service(
    repo: MigrationRepository = Depends(get_migration_repo),
    session: AsyncSession = Depends(get_db)
) -> MigrationService:
    return MigrationService(repo, session)

# ─── Schemas ─────────────────────────────────────────────────────────────────
class DailyStat(BaseModel):
    date: str
    revenue: float
    orders: int

class AttentionStats(BaseModel):
    new_orders: int
    unpaid_orders: int
    to_ship_orders: int
    problem_orders: int

class SalesAnalytics(BaseModel):
    total_revenue: float
    revenue_rub: float          # alias for frontend compatibility
    orders_count: int
    paid_orders_count: int
    users_count: int
    products_count: int
    top_products: List[dict]
    daily_stats: List[DailyStat]
    attention_stats: AttentionStats

class UserBlockRequest(BaseModel):
    is_active: bool

class AdminUserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    role: str = "customer"


class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class DeliveryAddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    recipient_name: str
    recipient_phone: str
    full_address: str
    address_type: str
    city: str
    postal_code: Optional[str] = None
    provider: str
    pickup_point_code: Optional[str] = None
    is_default: bool


class DeliveryAddressCreate(BaseModel):
    name: str
    recipient_name: str
    recipient_phone: str
    full_address: str
    address_type: str
    city: str
    postal_code: Optional[str] = None
    provider: str
    pickup_point_code: Optional[str] = None
    is_default: bool


class DeliveryAddressUpdate(BaseModel):
    name: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    full_address: Optional[str] = None
    address_type: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    provider: Optional[str] = None
    pickup_point_code: Optional[str] = None
    is_default: Optional[bool] = None

# ─── Dashboard / Analytics ───────────────────────────────────────────────────
@router.get("/dashboard", response_model=SalesAnalytics)
@router.get("/stats", response_model=SalesAnalytics)
async def get_dashboard(
    _admin: User = AdminDep,
    session: AsyncSession = Depends(get_db)
) -> SalesAnalytics:
    """Return real sales analytics summary from DB."""
    # Paid statuses for aggregation — use .value to ensure lowercase strings
    # match the PostgreSQL orderstatus enum values
    paid_statuses = [
        OrderStatus.PAID.value,
        OrderStatus.PROCESSING.value,
        OrderStatus.SHIPPED.value,
        OrderStatus.DELIVERED.value,
    ]

    revenue_stmt = select(func.sum(Order.total_amount)).where(Order.status.in_(paid_statuses))
    revenue_res = await session.execute(revenue_stmt)
    total_revenue = float(revenue_res.scalar() or 0.0)

    # Orders counts
    count_stmt = select(func.count(Order.id))
    total_orders = (await session.execute(count_stmt)).scalar() or 0
    
    paid_count_stmt = select(func.count(Order.id)).where(Order.status == OrderStatus.PAID.value)
    paid_orders = (await session.execute(paid_count_stmt)).scalar() or 0

    # Users count
    users_count_stmt = select(func.count(User.id))
    total_users = (await session.execute(users_count_stmt)).scalar() or 0

    # Products count
    products_count_stmt = select(func.count(Product.id)).where(Product.is_active.is_(True))
    products_count_val = (await session.execute(products_count_stmt)).scalar() or 0

    # Daily stats (last 30 days)
    now_utc = datetime.now(timezone.utc)
    # Start of day 30 days ago
    start_date = (now_utc - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    daily_stmt = (
        select(
            func.date(Order.created_at).label("d"),
            func.sum(Order.total_amount).label("rev"),
            func.count(Order.id).label("cnt")
        )
        .where(Order.created_at >= start_date)
        .where(Order.status.in_(paid_statuses))
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
    )
    daily_res = await session.execute(daily_stmt)
    # Normalize between date objects (Postgres) and strings (SQLite)
    daily_map = {str(row.d): {"revenue": float(row.rev or 0), "orders": row.cnt} for row in daily_res.all()}
    
    daily_stats = []
    for i in range(31):
        d = (now_utc - timedelta(days=30-i)).date()
        d_str = d.isoformat()
        stats = daily_map.get(d_str, {"revenue": 0.0, "orders": 0})
        daily_stats.append(DailyStat(date=d_str, revenue=stats["revenue"], orders=stats["orders"]))

    # Attention stats
    attention_stmt = select(Order.status, func.count(Order.id)).group_by(Order.status)
    attention_res = await session.execute(attention_stmt)
    status_counts = {row[0]: row[1] for row in attention_res.all()}
    
    attention_stats = AttentionStats(
        new_orders=status_counts.get(OrderStatus.PENDING.value, 0),
        unpaid_orders=status_counts.get(OrderStatus.PENDING_PAYMENT.value, 0),
        to_ship_orders=status_counts.get(OrderStatus.PAID.value, 0) + status_counts.get(OrderStatus.PROCESSING.value, 0),
        problem_orders=status_counts.get(OrderStatus.CANCELLED.value, 0) + status_counts.get(OrderStatus.REFUNDED.value, 0)
    )

    # Top products aggregation
    top_products_stmt = (
        select(
            Product.name,
            func.sum(OrderItem.quantity).label("sold_quantity")
        )
        .join(ProductVariant, Product.id == ProductVariant.product_id)
        .join(OrderItem, ProductVariant.id == OrderItem.product_variant_id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status.in_(paid_statuses))  # paid_statuses already .value strings
        .group_by(Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
    )
    top_products_res = await session.execute(top_products_stmt)
    top_products = [{"name": row.name, "sold_quantity": row.sold_quantity} for row in top_products_res.all()]

    return SalesAnalytics(
        total_revenue=total_revenue,
        revenue_rub=total_revenue,
        orders_count=total_orders,
        paid_orders_count=paid_orders,
        users_count=total_users,
        products_count=products_count_val,
        top_products=top_products,
        daily_stats=daily_stats,
        attention_stats=attention_stats
    )

# ─── Products ────────────────────────────────────────────────────────────────
@router.get("/products", response_model=ProductPagination)
async def list_products(
    cursor: Optional[str] = None,
    per_page: int = Query(20, ge=1, le=100),
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    return await service.get_products(cursor=cursor, per_page=per_page, active_only=False)

@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: UUID,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    return await service.get_product_detail(product_id)

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

# ─── Product Gallery ───
@router.post("/products/{product_id}/images", response_model=ProductImageRead, status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    product_id: UUID,
    file: UploadFile = File(...),
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    return await service.upload_image(product_id, file)

@router.delete("/products/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image(
    image_id: UUID,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> None:
    await service.delete_image(image_id)

@router.put("/products/{product_id}/images/{image_id}/cover", response_model=ProductImageRead)
async def set_product_cover_image(
    product_id: UUID,
    image_id: UUID,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    return await service.set_cover_image(product_id, image_id)

# ─── Product Option Groups ──────────────────────────────────────────────────
@router.post("/products/{product_id}/option-groups", response_model=ProductOptionGroupSchema, status_code=status.HTTP_201_CREATED)
async def create_product_option_group(
    product_id: UUID,
    payload: ProductOptionGroupCreate,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    result = await service.create_option_group(product_id, payload)
    logger.info("admin_action", admin_id=str(_admin.id), action="create_option_group", target_id=str(result.id))
    return result

@router.put("/products/option-groups/{group_id}", response_model=ProductOptionGroupSchema)
async def update_product_option_group(
    group_id: UUID,
    payload: ProductOptionGroupUpdate,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    result = await service.update_option_group(group_id, payload)
    logger.info("admin_action", admin_id=str(_admin.id), action="update_option_group", target_id=str(group_id))
    return result

@router.delete("/products/option-groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_option_group(
    group_id: UUID,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> None:
    await service.delete_option_group(group_id)
    logger.info("admin_action", admin_id=str(_admin.id), action="delete_option_group", target_id=str(group_id))

@router.post("/products/option-groups/{group_id}/values", response_model=ProductOptionValueSchema, status_code=status.HTTP_201_CREATED)
async def create_product_option_value(
    group_id: UUID,
    payload: ProductOptionValueCreate,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    result = await service.create_option_value(group_id, payload)
    logger.info("admin_action", admin_id=str(_admin.id), action="create_option_value", target_id=str(result.id))
    return result

@router.put("/products/option-values/{value_id}", response_model=ProductOptionValueSchema)
async def update_product_option_value(
    value_id: UUID,
    payload: ProductOptionValueUpdate,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    result = await service.update_option_value(value_id, payload)
    logger.info("admin_action", admin_id=str(_admin.id), action="update_option_value", target_id=str(value_id))
    return result

@router.delete("/products/option-values/{value_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_option_value(
    value_id: UUID,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> None:
    await service.delete_option_value(value_id)
    logger.info("admin_action", admin_id=str(_admin.id), action="delete_option_value", target_id=str(value_id))

# ─── Categories ─────────────────────────────────────────────────────────────
@router.get("/categories", response_model=List[CategoryRead])
async def list_categories(
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    return await service.list_categories(active_only=False)

@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    return await service.create_category(payload)

@router.put("/categories/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> Any:
    return await service.update_category(category_id, payload)

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    _admin: User = AdminDep,
    service: ProductService = Depends()
) -> None:
    await service.delete_category(category_id)

# ─── Orders ──────────────────────────────────────────────────────────────────
@router.get("/orders")
async def list_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    date: Optional[str] = Query(None, description="Filter by date: today, week, month, all"),
    date_from: Optional[date] = Query(None, description="Filter orders from date (inclusive)"),
    date_to: Optional[date] = Query(None, description="Filter orders to date (inclusive)"),
    search: Optional[str] = Query(None, description="Search by order ID, tracking, email, phone, name"),
    include_archived: bool = Query(False, description="Include archived orders in results"),
    _admin: User = AdminDep,
    repo: OrderRepository = Depends(get_order_repo),
) -> Any:
    offset = (page - 1) * per_page
    
    # Handle shorthand date filter
    if date and date != "all":
        now = datetime.now(timezone.utc).date()
        if date == "today":
            date_from = now
        elif date == "week":
            date_from = now - timedelta(days=7)
        elif date == "month":
            date_from = now - timedelta(days=30)

    items, total = await repo.list_all(
        status=status, 
        offset=offset, 
        limit=per_page, 
        date_from=date_from, 
        date_to=date_to,
        search=search,
        include_archived=include_archived
    )
    return {
        "items": [OrderRead.model_validate(o) for o in items],
        "total": total,
        "page": page,
        "per_page": per_page,
    }

@router.get("/orders/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: UUID,
    _admin: User = AdminDep,
    repo: OrderRepository = Depends(get_order_repo),
) -> Any:
    order = await repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderRead.model_validate(order)

@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: UUID,
    new_status: OrderStatus,
    _admin: User = AdminDep,
    service: OrderService = Depends(get_admin_order_service)
) -> Any:
    return await service.update_order_status(order_id, new_status)

@router.post("/orders/{order_id}/archive")
async def archive_order(
    order_id: UUID,
    _admin: User = AdminDep,
    service: OrderService = Depends(get_admin_order_service)
) -> Any:
    return await service.archive_order(order_id)

# ─── Blog ────────────────────────────────────────────────────────────────────
@router.post("/blog/posts", status_code=status.HTTP_201_CREATED)
async def create_blog_post(
    body: BlogPostCreate,
    _admin: User = AdminDep,
    service: BlogService = Depends(get_blog_service)
) -> Any:
    return await service.create_post(data=body, user_id=_admin.id)

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

@router.post("/blog/posts/{post_id}/cover")
async def upload_blog_cover(
    post_id: UUID,
    file: UploadFile = File(...),
    _admin: User = AdminDep,
    service: BlogService = Depends(get_blog_service),
) -> Any:
    """Upload blog post cover image."""
    content = await file.read()
    safe_filename = sanitize_filename(file.filename or "cover.jpg")
    object_name = f"blog/{post_id}/{_uuid_module.uuid4().hex[:8]}_{safe_filename}"
    await storage_client.save_file(
        object_name=object_name,
        data=content,
        content_type=file.content_type or "image/jpeg",
    )
    cover_url = storage_client.get_public_url(object_name)
    await service.update_post(post_id, BlogPostUpdate(cover_image=cover_url))
    return {"cover_url": cover_url}

# ─── Customers ───────────────────────────────────────────────────────────────
@router.get("/users")
async def list_users(
    q: Optional[str] = Query(None, description="Search by name or email"),
    search: Optional[str] = Query(None, description="Deprecated: use q instead"),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _admin: User = AdminDep,
    repo: UserRepository = Depends(get_user_repo)
) -> Any:
    search_term = q or search
    offset = (page - 1) * per_page
    users = await repo.list_users(search_term, role, is_active, offset, per_page)
    total = await repo.count_users(search_term, role, is_active)

    return {
        "items": [UserResponse.model_validate(u) for u in users],
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: AdminUserCreate,
    _admin: User = AdminDep,
    repo: UserRepository = Depends(get_user_repo)
) -> Any:
    # Check if user already exists
    existing_user = await repo.get_by_email(payload.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    hashed_password = get_password_hash(payload.password)
    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hashed_password,
        role=payload.role,
        is_active=True
    )
    created_user = await repo.create(new_user)
    return UserResponse.model_validate(created_user)

@router.get("/users/export")
async def export_users(
    _admin: User = AdminDep,
    repo: UserRepository = Depends(get_user_repo)
) -> StreamingResponse:
    users = await repo.get_all_users_for_export()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Users"
    
    # Headers
    headers = ["ID", "Email", "Full Name", "Role", "Active", "Provider", "Created At"]
    ws.append(headers)
    
    # Data
    for user in users:
        ws.append([
            str(user.id),
            user.email,
            user.full_name or "",
            user.role,
            user.is_active,
            user.auth_provider,
            user.created_at.replace(tzinfo=None) if user.created_at else ""
        ])
    
    # Save to BytesIO
    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)
    
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=users_export.xlsx"}
    )

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


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    _admin: User = AdminDep,
    repo: UserRepository = Depends(get_user_repo)
) -> Any:
    """Get user by ID with decrypted PII fields."""
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.get("/users/{user_id}/full", response_model=AdminUserFullResponse)
async def get_user_full_details(
    user_id: UUID,
    _admin: User = AdminDep,
    user_repo: UserRepository = Depends(get_user_repo),
    addr_repo: DeliveryAddressRepository = Depends(get_address_repo),
    order_repo: OrderRepository = Depends(get_order_repo),
    iot_repo: IoTRepository = Depends(get_iot_repo),
) -> Any:
    """Get comprehensive user details: basic info, addresses, orders, and IoT devices."""
    # 1. Fetch user
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Fetch addresses
    addresses = await addr_repo.list_by_user(user_id)

    # 3. Fetch orders
    orders = await order_repo.get_user_orders(user_id)

    # 4. Fetch IoT devices
    devices_result = await iot_repo.session.execute(
        select(UserDevice).where(UserDevice.user_id == user_id)
    )
    devices = devices_result.scalars().all()

    # Construct the full response
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "role": user.role,
        "created_at": user.created_at,
        "last_login_at": user.last_login_at,
        "last_login_ip": user.last_login_ip,
        "last_login_device": user.last_login_device,
        "addresses": addresses,
        "orders": orders,
        "devices": devices
    }


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    payload: AdminUserUpdate,
    _admin: User = AdminDep,
    repo: UserRepository = Depends(get_user_repo),
    session: AsyncSession = Depends(get_db)
) -> Any:
    """Update user fields. PII fields are encrypted before save. Superadmin demotion protection."""
    target = await repo.get_by_id(user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Superadmin demotion protection: prevent removing admin from last superadmin/admin user
    if payload.role is not None and payload.role != target.role:
        if target.is_superuser or target.role == "admin":
            # Count remaining admins
            admin_count_stmt = select(func.count(User.id)).where(
                User.role == "admin", User.is_active.is_(True)
            )
            admin_count = (await session.execute(admin_count_stmt)).scalar() or 0
            superadmin_count_stmt = select(func.count(User.id)).where(
                User.is_superuser.is_(True), User.is_active.is_(True)
            )
            superadmin_count = (await session.execute(superadmin_count_stmt)).scalar() or 0
            if target.is_superuser and superadmin_count <= 1:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot change role of the last superadmin"
                )
            if target.role == "admin" and not target.is_superuser and admin_count <= 1:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot change role of the last admin"
                )

    update_kwargs: dict = {}
    if payload.full_name is not None:
        update_kwargs["full_name"] = payload.full_name
    if payload.email is not None:
        update_kwargs["email"] = str(payload.email)
    if payload.phone is not None:
        update_kwargs["phone"] = payload.phone
    if payload.role is not None:
        update_kwargs["role"] = payload.role
    if payload.is_active is not None:
        update_kwargs["is_active"] = payload.is_active

    if not update_kwargs:
        return UserResponse.model_validate(target)

    updated = await repo.update(user_id, **update_kwargs)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(updated)


@router.get("/users/{user_id}/addresses")
async def get_user_addresses(
    user_id: UUID,
    _admin: User = AdminDep,
    repo: UserRepository = Depends(get_user_repo),
    addr_repo: DeliveryAddressRepository = Depends(get_address_repo)
) -> Any:
    """Get all delivery addresses for a user."""
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    addresses = await addr_repo.list_by_user(user_id)
    return {"items": [DeliveryAddressResponse.model_validate(a) for a in addresses]}


@router.post("/users/{user_id}/addresses", response_model=DeliveryAddressResponse, status_code=status.HTTP_201_CREATED)
async def create_user_address(
    user_id: UUID,
    payload: DeliveryAddressCreate,
    _admin: User = AdminDep,
    repo: UserRepository = Depends(get_user_repo),
    addr_repo: DeliveryAddressRepository = Depends(get_address_repo)
) -> Any:
    """Create a new delivery address for a user."""
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If is_default is true, unset other defaults
    if payload.is_default:
        from app.db.models.delivery_address import DeliveryAddress
        await addr_repo.session.execute(
            update(DeliveryAddress).where(DeliveryAddress.user_id == user_id).values(is_default=False)
        )

    addr = await addr_repo.create(
        user_id=user_id,
        name=payload.name,
        recipient_name=payload.recipient_name,
        recipient_phone=payload.recipient_phone,
        address_type=payload.address_type,
        full_address=payload.full_address,
        city=payload.city,
        postal_code=payload.postal_code,
        provider=payload.provider,
        pickup_point_code=payload.pickup_point_code,
        is_default=payload.is_default
    )
    return DeliveryAddressResponse.model_validate(addr)


@router.put("/users/{user_id}/addresses/{addr_id}", response_model=DeliveryAddressResponse)
async def update_user_address(
    user_id: UUID,
    addr_id: UUID,
    payload: DeliveryAddressUpdate,
    _admin: User = AdminDep,
    repo: UserRepository = Depends(get_user_repo),
    addr_repo: DeliveryAddressRepository = Depends(get_address_repo)
) -> Any:
    """Update a delivery address for a user."""
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    addr = await addr_repo.get_by_id(addr_id)
    if not addr or addr.user_id != user_id:
        raise HTTPException(status_code=404, detail="Address not found")

    update_kwargs = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_kwargs:
        return DeliveryAddressResponse.model_validate(addr)

    updated = await addr_repo.update(addr_id, **update_kwargs)
    return DeliveryAddressResponse.model_validate(updated)


@router.delete("/users/{user_id}/addresses/{addr_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_address(
    user_id: UUID,
    addr_id: UUID,
    _admin: User = AdminDep,
    repo: UserRepository = Depends(get_user_repo),
    addr_repo: DeliveryAddressRepository = Depends(get_address_repo)
) -> None:
    """Delete a delivery address for a user."""
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    addr = await addr_repo.get_by_id(addr_id)
    if not addr or addr.user_id != user_id:
        raise HTTPException(status_code=404, detail="Address not found")
    await addr_repo.delete(addr_id)

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

# ─── Devices CRUD ────────────────────────────────────────────────────────────
@router.get("/device-models", response_model=List[str])
async def list_device_models(_admin: User = AdminDep) -> List[str]:
    """Return list of allowed device models."""
    return [m.value for m in DeviceModel]


@router.get("/devices", response_model=dict)
async def list_devices(
    user_id: Optional[UUID] = Query(None),
    is_active: Optional[bool] = Query(None),
    model: Optional[DeviceModel] = Query(None, description="Filter by device model"),
    search: Optional[str] = Query(None, description="Search by device_uid or name"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    _admin: User = AdminDep,
    session: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repo)
) -> Any:
    """List all UserDevice records with optional filters and user info."""
    stmt = select(UserDevice).join(User, UserDevice.user_id == User.id)
    if user_id is not None:
        stmt = stmt.where(UserDevice.user_id == user_id)
    if is_active is not None:
        stmt = stmt.where(UserDevice.is_active == is_active)
    if model is not None:
        stmt = stmt.where(UserDevice.model == model)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                UserDevice.device_uid.ilike(pattern),
                UserDevice.name.ilike(pattern),
            )
        )
    
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total: int = int((await session.execute(count_stmt)).scalar() or 0)
    
    offset = (page - 1) * per_page
    
    # We use select(UserDevice, User) to get both
    items_stmt = select(UserDevice, User).join(User, UserDevice.user_id == User.id)
    # Re-apply filters to the new stmt
    if user_id is not None:
        items_stmt = items_stmt.where(UserDevice.user_id == user_id)
    if is_active is not None:
        items_stmt = items_stmt.where(UserDevice.is_active == is_active)
    if model is not None:
        items_stmt = items_stmt.where(UserDevice.model == model)
    if search:
        pattern = f"%{search}%"
        items_stmt = items_stmt.where(
            or_(
                UserDevice.device_uid.ilike(pattern),
                UserDevice.name.ilike(pattern),
            )
        )
    items_stmt = items_stmt.order_by(UserDevice.registered_at.desc()).offset(offset).limit(per_page)
    
    result = await session.execute(items_stmt)
    rows = result.all()
    
    items = []
    for dev, user in rows:
        decrypted_user = user_repo._decrypt_user(user)
        dev_data = AdminDeviceRead.model_validate(dev)
        dev_data.user_email = decrypted_user.email
        dev_data.user_name = decrypted_user.full_name
        items.append(dev_data)

    logger.info("admin_action", admin_id=str(_admin.id), action="list_devices", target_id=None)
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.post("/devices", response_model=AdminDeviceRead, status_code=status.HTTP_201_CREATED)
async def create_device(
    payload: AdminDeviceCreate,
    _admin: User = AdminDep,
    session: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repo)
) -> Any:
    """Create a new device for a user."""
    # Check if user exists
    user = await user_repo.get_by_id(payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if UID is unique
    existing_stmt = select(UserDevice).where(UserDevice.device_uid == payload.device_uid)
    existing = (await session.execute(existing_stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Device with this UID already exists")
    
    new_dev = UserDevice(
        user_id=payload.user_id,
        device_uid=payload.device_uid,
        model=payload.model,
        name=payload.name,
        comment=payload.comment,
        is_active=payload.is_active
    )
    session.add(new_dev)
    await session.commit()
    await session.refresh(new_dev)
    
    # Return with user info
    res = AdminDeviceRead.model_validate(new_dev)
    res.user_email = user.email
    res.user_name = user.full_name
    return res


@router.get("/devices/{device_id}", response_model=AdminDeviceRead)
async def get_device(
    device_id: UUID,
    _admin: User = AdminDep,
    session: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repo)
) -> Any:
    """Get device details by UUID with user info."""
    stmt = select(UserDevice, User).join(User, UserDevice.user_id == User.id).where(UserDevice.id == device_id)
    result = await session.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Device not found")
    
    dev, user = row
    decrypted_user = user_repo._decrypt_user(user)
    res = AdminDeviceRead.model_validate(dev)
    res.user_email = decrypted_user.email
    res.user_name = decrypted_user.full_name
    
    logger.info("admin_action", admin_id=str(_admin.id), action="get_device", target_id=str(device_id))
    return res


@router.patch("/devices/{device_id}", response_model=AdminDeviceRead)
async def update_device(
    device_id: UUID,
    payload: AdminDeviceUpdate,
    _admin: User = AdminDep,
    session: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repo)
) -> Any:
    """Update device fields (name, model, user_id, is_active, comment)."""
    stmt = select(UserDevice, User).join(User, UserDevice.user_id == User.id).where(UserDevice.id == device_id)
    result = await session.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Device not found")
    
    dev, user = row
    update_data = payload.model_dump(exclude_none=True)
    
    if "user_id" in update_data:
        new_user = await user_repo.get_by_id(update_data["user_id"])
        if not new_user:
            raise HTTPException(status_code=404, detail="New user not found")
        user = new_user # for response

    for field, value in update_data.items():
        setattr(dev, field, value)
        
    await session.commit()
    await session.refresh(dev)
    
    decrypted_user = user_repo._decrypt_user(user)
    res = AdminDeviceRead.model_validate(dev)
    res.user_email = decrypted_user.email
    res.user_name = decrypted_user.full_name
    
    logger.info("admin_action", admin_id=str(_admin.id), action="update_device", target_id=str(device_id))
    return res


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: UUID,
    _admin: User = AdminDep,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete a device by UUID."""
    result = await session.execute(select(UserDevice).where(UserDevice.id == device_id))
    dev = result.scalar_one_or_none()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    await session.delete(dev)
    await session.commit()
    logger.info("admin_action", admin_id=str(_admin.id), action="delete_device", target_id=str(device_id))


@router.get("/users/{user_id}/devices", response_model=List[AdminDeviceRead])
async def get_user_devices(
    user_id: UUID,
    _admin: User = AdminDep,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Get all devices for a specific user."""
    result = await session.execute(select(UserDevice).where(UserDevice.user_id == user_id))
    devices = result.scalars().all()
    logger.info("admin_action", admin_id=str(_admin.id), action="list_user_devices", target_id=str(user_id))
    return [AdminDeviceRead.model_validate(d) for d in devices]


# ─── Firmware Admin ──────────────────────────────────────────────────────────
@router.get("/firmware/devices", response_model=List[DeviceRead])
async def list_firmware_devices(
    search: Optional[str] = Query(None, description="Search by serial"),
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    return await service.get_all_devices(search=search)


@router.post("/firmware/devices", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
async def admin_add_device(
    payload: AdminAddDeviceRequest,
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    if payload.user_id:
        return await service.add_device(payload.user_id, payload.serial)
    # No user_id — create anonymous device under admin token
    return await service.add_device(_admin.id, payload.serial)


@router.delete("/firmware/devices/{serial}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_device(
    serial: str,
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service),
) -> None:
    deleted = await service.repo.delete_device(serial)
    await service.repo.session.commit()
    if not deleted:
        raise HTTPException(status_code=404, detail="Device not found")

@router.post("/firmware/complectations", response_model=ComplectationRead, status_code=status.HTTP_201_CREATED)
async def create_complectation(
    payload: ComplectationCreate,
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service)
) -> Any:
    return await service.create_complectation(
        payload.caption, payload.label, payload.code, payload.simple
    )

@router.put("/firmware/complectations/{comp_id}", response_model=ComplectationRead)
async def update_complectation(
    comp_id: UUID,
    payload: ComplectationCreate,
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service)
) -> Any:
    return await service.update_complectation(
        comp_id, payload.caption, payload.label, payload.code, payload.simple
    )

@router.delete("/firmware/complectations/{comp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complectation(
    comp_id: UUID,
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service)
) -> None:
    await service.delete_complectation(comp_id)

@router.post("/firmware/devices/{serial}/complectations/{comp_id}")
async def link_complectation_to_device(
    serial: str,
    comp_id: UUID,
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    await service.add_complectation_to_device(serial, comp_id)
    return {"status": "success"}


@router.post(
    "/firmware/devices/{serial}/complectations/{comp_id}/toggle",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def admin_toggle_complectation(
    serial: str,
    comp_id: UUID,
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service),
) -> None:
    # Admin toggle: no owner check
    await service.repo.toggle_device_complectation(serial, comp_id)
    await service.repo.session.commit()


@router.get("/firmware/duplicates")
async def get_firmware_duplicates(
    _admin: User = AdminDep,
    session: AsyncSession = Depends(get_db),
) -> Any:
    """Return users sharing the same email_hash (potential duplicates)."""
    from sqlalchemy import text

    stmt = text(
        "SELECT email_hash, COUNT(*) AS cnt "
        "FROM users "
        "GROUP BY email_hash "
        "HAVING COUNT(*) > 1"
    )
    result = await session.execute(stmt)
    rows = result.fetchall()
    return {"duplicates": [{"email_hash": r[0], "count": r[1]} for r in rows]}


@router.post("/firmware/merge-users")
async def merge_users_firmware(
    payload: UserMergeRequest,
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    await service.merge_users_firmware(payload.source_email, payload.target_email)
    return {"status": "success"}


@router.post("/firmware/merge")
async def merge_users_by_id(
    payload: MergeByIdRequest,
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service),
) -> Any:
    """Merge source user firmware devices into target user, delete source token."""
    await service.merge_users_by_id(payload.source_user_id, payload.target_user_id)
    return {"status": "success"}

@router.post("/firmware/import", response_model=ExcelImportResponse)
async def import_firmware_excel(
    file: UploadFile = File(...),
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service)
) -> Any:
    content = await file.read()
    clients, devices, errors = await service.import_excel(content)
    return {
        "clients_imported": clients,
        "devices_imported": devices,
        "errors": errors
    }

# ─── Migration ───────────────────────────────────────────────────────────────
@router.post("/migration/start", response_model=List[MigrationJobResponse])
async def start_migration(
    payload: MigrationStartRequest = MigrationStartRequest(),
    _admin: User = AdminDep,
    service: MigrationService = Depends(get_migration_service)
) -> Any:
    """Start migration for specific entity or all entities."""
    return await service.start_migration(payload.entity)

@router.get("/migration/status", response_model=MigrationStatusResponse)
async def get_migration_status(
    _admin: User = AdminDep,
    service: MigrationService = Depends(get_migration_service)
) -> Any:
    """Get overall migration status summary."""
    return await service.get_migration_summary()

@router.post("/migration/pause")
async def pause_all_migrations(
    _admin: User = AdminDep,
    service: MigrationService = Depends(get_migration_service)
) -> Any:
    """Pause all active migration jobs."""
    await service.pause_all()
    return {"status": "paused"}

@router.post("/migration/resume")
async def resume_all_migrations(
    _admin: User = AdminDep,
    service: MigrationService = Depends(get_migration_service)
) -> Any:
    """Resume all paused migration jobs."""
    await service.resume_all()
    return {"status": "resumed"}

@router.post("/migration/{job_id}/pause", response_model=MigrationJobResponse)
async def pause_specific_migration(
    job_id: UUID,
    _admin: User = AdminDep,
    service: MigrationService = Depends(get_migration_service)
) -> Any:
    job = await service.pause_migration(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    return job

@router.post("/migration/{job_id}/resume", response_model=MigrationJobResponse)
async def resume_specific_migration(
    job_id: UUID,
    _admin: User = AdminDep,
    service: MigrationService = Depends(get_migration_service)
) -> Any:
    job = await service.resume_migration(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    return job

@router.delete("/migration/reset/{entity}")
async def reset_migration_entity(
    entity: MigrationEntity,
    _admin: User = AdminDep,
    service: MigrationService = Depends(get_migration_service),
) -> Any:
    """Delete migrated data for a specific entity and its MigrationJob rows.

    Only removes records that originated from OpenCart (oc_*_id IS NOT NULL).
    Returns 422 automatically if entity value is not a valid MigrationEntity.
    """
    return await service.reset_entity(entity)


@router.delete("/migration/reset")
async def reset_migration(
    _admin: User = AdminDep,
    service: MigrationService = Depends(get_migration_service)
) -> Any:
    """Delete all migrated data (products, categories, orders, blog posts) and all MigrationJob rows."""
    return await service.reset_migration()

# ─── Pages ───────────────────────────────────────────────────────────────────
router.include_router(pages_admin_router)
