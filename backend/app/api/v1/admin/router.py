# Module: api/v1/admin/router.py | Agent: backend-agent | Task: Phase 2 Dashfirm
import io
import openpyxl
from uuid import UUID
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin, get_product_repo, get_db, get_cart_service
from app.db.models.order import Order, OrderStatus, OrderItem
from app.db.models.product import ProductVariant, Product
from app.db.models.user import User
from app.api.v1.auth.schemas import UserResponse
from app.core.security import get_password_hash

# Services & Repositories
from app.api.v1.products.service import ProductService
from app.api.v1.products.repository import ProductRepository
from app.api.v1.products.schemas import (
    ProductCreate, ProductUpdate, ProductRead, ProductPagination,
    CategoryRead, CategoryCreate, CategoryUpdate, ProductImageRead
)
from app.api.v1.blog.service import BlogService, get_blog_service
from app.api.v1.blog.schemas import BlogPostCreate, BlogPostUpdate
from app.api.v1.orders.service import OrderService
from app.api.v1.orders.repository import OrderRepository
from app.api.v1.users.repository import UserRepository
from app.api.v1.iot.repository import IoTRepository
from app.api.v1.cart.service import CartService
from app.api.v1.firmware.service import FirmwareService, get_firmware_service
from app.api.v1.firmware.schemas import (
    DeviceRead, ComplectationCreate, ComplectationRead, 
    UserMergeRequest, ExcelImportResponse
)
from .pages_router import router as pages_admin_router

# Migration
from .migration_service import MigrationService
from .migration_repository import MigrationRepository
from .schemas import MigrationJobResponse, MigrationStartRequest, MigrationStatusResponse

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

def get_migration_repo(session: AsyncSession = Depends(get_db)) -> MigrationRepository:
    return MigrationRepository(session)

def get_migration_service(
    repo: MigrationRepository = Depends(get_migration_repo),
    session: AsyncSession = Depends(get_db)
) -> MigrationService:
    return MigrationService(repo, session)

# ─── Schemas ─────────────────────────────────────────────────────────────────
class SalesAnalytics(BaseModel):
    total_revenue: float
    orders_count: int
    paid_orders_count: int
    users_count: int
    top_products: List[dict]

class UserBlockRequest(BaseModel):
    is_active: bool

class AdminUserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    role: str = "customer"

# ─── Dashboard / Analytics ───────────────────────────────────────────────────
@router.get("/dashboard", response_model=SalesAnalytics)
@router.get("/stats", response_model=SalesAnalytics)
async def get_dashboard(
    _admin: User = AdminDep,
    session: AsyncSession = Depends(get_db)
) -> Any:
    """Return real sales analytics summary from DB."""
    # Paid statuses for aggregation
    paid_statuses = [
        OrderStatus.PAID, 
        OrderStatus.PROCESSING, 
        OrderStatus.SHIPPED, 
        OrderStatus.DELIVERED
    ]
    
    revenue_stmt = select(func.sum(Order.total_amount)).where(Order.status.in_(paid_statuses))
    revenue_res = await session.execute(revenue_stmt)
    total_revenue = float(revenue_res.scalar() or 0.0)

    # Orders counts
    count_stmt = select(func.count(Order.id))
    total_orders = (await session.execute(count_stmt)).scalar() or 0
    
    paid_count_stmt = select(func.count(Order.id)).where(Order.status == OrderStatus.PAID)
    paid_orders = (await session.execute(paid_count_stmt)).scalar() or 0

    # Users count
    users_count_stmt = select(func.count(User.id))
    total_users = (await session.execute(users_count_stmt)).scalar() or 0

    # Top products aggregation
    top_products_stmt = (
        select(
            Product.name,
            func.sum(OrderItem.quantity).label("sold_quantity")
        )
        .join(ProductVariant, Product.id == ProductVariant.product_id)
        .join(OrderItem, ProductVariant.id == OrderItem.product_variant_id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status.in_(paid_statuses))
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
        users_count=total_users,
        top_products=top_products
    )

# ─── Products ────────────────────────────────────────────────────────────────
@router.get("/products", response_model=ProductPagination)
async def list_products(
    cursor: Optional[UUID] = None,
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

# ─── Customers ───────────────────────────────────────────────────────────────
@router.get("/users")
async def list_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _admin: User = AdminDep,
    repo: UserRepository = Depends(get_user_repo)
) -> Any:
    offset = (page - 1) * per_page
    users = await repo.list_users(search, role, is_active, offset, per_page)
    total = await repo.count_users(search, role, is_active)
    
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

# ─── Firmware Admin ──────────────────────────────────────────────────────────
@router.get("/firmware/devices", response_model=List[DeviceRead])
async def list_firmware_devices(
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service)
) -> Any:
    return await service.get_all_devices()

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
    service: FirmwareService = Depends(get_firmware_service)
) -> Any:
    await service.add_complectation_to_device(serial, comp_id)
    return {"status": "success"}

@router.post("/firmware/merge-users")
async def merge_users_firmware(
    payload: UserMergeRequest,
    _admin: User = AdminDep,
    service: FirmwareService = Depends(get_firmware_service)
) -> Any:
    await service.merge_users_firmware(payload.source_email, payload.target_email)
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
@router.post("/migration/start")
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

# ─── Pages ───────────────────────────────────────────────────────────────────
router.include_router(pages_admin_router)
