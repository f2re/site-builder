# Module: api/v1/admin/migration_service.py | Agent: backend-agent | Task: BE-03_cart_orders_payments
import httpx
import os
import re
import traceback
from uuid import UUID
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import encrypt_data, get_blind_index
from app.db.opencart_session import OCAsyncSessionLocal
from app.db.opencart_models import (
    OCCustomer, OCProduct, OCProductDescription, 
    OCCategory, OCCategoryDescription, OCOrder, OCOrderProduct,
    OCProductToCategory
)
from app.db.models.user import User
from app.db.models.product import Category, Product, ProductVariant, ProductImage
from app.db.models.order import Order, OrderItem, OrderStatus
from app.db.models.migration import MigrationJob, MigrationStatus, MigrationEntity
from .migration_repository import MigrationRepository

class MigrationService:
    def __init__(self, repo: MigrationRepository, session: AsyncSession):
        self.repo = repo
        self.session = session
        self.batch_size = 50

    async def start_migration(self, entity: MigrationEntity) -> MigrationJob:
        # Check if there is an active job for this entity
        active_job = await self.repo.get_active_job_by_entity(entity)
        if active_job:
            return active_job
            
        return await self.repo.create_job(entity)

    async def get_all_jobs(self) -> List[MigrationJob]:
        return await self.repo.get_all_jobs()

    async def get_job(self, job_id: UUID) -> Optional[MigrationJob]:
        return await self.repo.get_job_by_id(job_id)

    async def pause_migration(self, job_id: UUID) -> Optional[MigrationJob]:
        return await self.repo.update_job_status(job_id, MigrationStatus.PAUSED)

    async def resume_migration(self, job_id: UUID) -> Optional[MigrationJob]:
        return await self.repo.update_job_status(job_id, MigrationStatus.PENDING)

    async def run_batch(self, job_id: UUID):
        """
        Main logic for running a migration batch.
        This is called by Celery tasks.
        """
        job = await self.repo.get_job_by_id(job_id)
        if not job or job.status not in [MigrationStatus.PENDING, MigrationStatus.RUNNING]:
            return

        # Set job as running
        if job.status == MigrationStatus.PENDING:
            await self.repo.update_job_status(
                job_id, 
                MigrationStatus.RUNNING, 
                started_at=datetime.now(timezone.utc)
            )
            await self.session.refresh(job)

        # Initialize total count if needed
        if job.total == 0:
            async with OCAsyncSessionLocal() as oc_session:
                count_stmt = None
                if job.entity == MigrationEntity.USERS:
                    count_stmt = select(func.count()).select_from(OCCustomer)
                elif job.entity in [MigrationEntity.PRODUCTS, MigrationEntity.CATEGORIES]:
                    count_stmt = select(func.count()).select_from(OCProduct)
                elif job.entity == MigrationEntity.ORDERS:
                    count_stmt = select(func.count()).select_from(OCOrder)
                
                if count_stmt is not None:
                    count_res = await oc_session.execute(count_stmt)
                    job.total = int(count_res.scalar() or 0)
                    await self.session.commit()

        try:
            if job.entity == MigrationEntity.USERS:
                await self.migrate_users(job)
            elif job.entity in [MigrationEntity.PRODUCTS, MigrationEntity.CATEGORIES]:
                await self.migrate_catalog(job)
            elif job.entity == MigrationEntity.ORDERS:
                await self.migrate_orders(job)
            else:
                await self.repo.update_job_status(job_id, MigrationStatus.DONE)
            
        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            await self.repo.update_job_status(
                job_id, 
                MigrationStatus.FAILED, 
                errors=(job.errors or []) + [error_msg]
            )
            raise

    async def migrate_users(self, job: MigrationJob):
        async with OCAsyncSessionLocal() as oc_session:
            stmt = (
                select(OCCustomer)
                .where(OCCustomer.customer_id > (job.last_oc_id or 0))
                .order_by(OCCustomer.customer_id)
                .limit(self.batch_size)
            )
            result = await oc_session.execute(stmt)
            customers = result.scalars().all()

            if not customers:
                await self.repo.update_job_status(job.id, MigrationStatus.DONE)
                return

            processed = 0
            skipped = 0
            last_id = job.last_oc_id or 0

            for oc_cust in customers:
                # Idempotency check: use get_blind_index(email)
                email_hash = get_blind_index(oc_cust.email)
                check_stmt = select(User).where(User.email_hash == email_hash)
                existing = await self.session.execute(check_stmt)
                if existing.scalar_one_or_none():
                    skipped += 1
                else:
                    new_user = User(
                        email_hash=email_hash,
                        email=encrypt_data(oc_cust.email),
                        full_name=encrypt_data(f"{oc_cust.firstname} {oc_cust.lastname}"),
                        phone=encrypt_data(oc_cust.telephone) if oc_cust.telephone else None,
                        phone_hash=get_blind_index(oc_cust.telephone) if oc_cust.telephone else None,
                        hashed_password=oc_cust.password,  # Store OC hash as is
                        role="customer",
                        is_active=bool(oc_cust.status),
                        created_at=oc_cust.date_added.replace(tzinfo=timezone.utc) if oc_cust.date_added else datetime.now(timezone.utc)
                    )
                    self.session.add(new_user)
                    processed += 1
                
                last_id = oc_cust.customer_id

            # Update job stats
            job.processed += processed
            job.skipped += skipped
            job.last_oc_id = last_id
            
            await self.session.commit()
            
            if len(customers) < self.batch_size:
                await self.repo.update_job_status(job.id, MigrationStatus.DONE)

    async def migrate_catalog(self, job: MigrationJob):
        # 1. Handle hierarchical categories first (recursive)
        await self._migrate_categories()

        # 2. Fetch batch of oc_product
        async with OCAsyncSessionLocal() as oc_session:
            stmt = (
                select(OCProduct)
                .where(OCProduct.product_id > (job.last_oc_id or 0))
                .order_by(OCProduct.product_id)
                .limit(self.batch_size)
            )
            result = await oc_session.execute(stmt)
            products = result.scalars().all()

            if not products:
                await self.repo.update_job_status(job.id, MigrationStatus.DONE)
                return

            processed = 0
            skipped = 0
            last_id = job.last_oc_id or 0

            # Get category mapping oc_id -> our_uuid
            cat_stmt = select(Category.oc_category_id, Category.id).where(Category.oc_category_id.is_not(None))
            cat_res = await self.session.execute(cat_stmt)
            cat_map = {row[0]: row[1] for row in cat_res.all()}

            async with httpx.AsyncClient() as client:
                for oc_prod in products:
                    # Idempotency check: use oc_product_id
                    prod_check_stmt = select(Product).where(Product.oc_product_id == oc_prod.product_id)
                    existing = await self.session.execute(prod_check_stmt)
                    if existing.scalar_one_or_none():
                        skipped += 1
                    else:
                        # Get description
                        desc_stmt = select(OCProductDescription).where(
                            OCProductDescription.product_id == oc_prod.product_id,
                            OCProductDescription.language_id == settings.OC_LANGUAGE_ID
                        )
                        desc_res = await oc_session.execute(desc_stmt)
                        oc_desc = desc_res.scalar_one_or_none()
                        
                        name = oc_desc.name if oc_desc else f"Product {oc_prod.product_id}"
                        slug = self._slugify(name)
                        slug = await self._ensure_unique_slug(Product, slug)

                        new_prod = Product(
                            name=name,
                            slug=slug,
                            description=oc_desc.description if oc_desc else None,
                            description_html=oc_desc.description if oc_desc else None,
                            meta_title=oc_desc.meta_title if oc_desc else None,
                            meta_description=oc_desc.meta_description if oc_desc else None,
                            oc_product_id=oc_prod.product_id,
                            is_active=bool(oc_prod.status),
                            created_at=oc_prod.date_added.replace(tzinfo=timezone.utc) if oc_prod.date_added else datetime.now(timezone.utc)
                        )
                        
                        # Set category
                        link_stmt = select(OCProductToCategory.category_id).where(
                            OCProductToCategory.product_id == oc_prod.product_id
                        )
                        link_res = await oc_session.execute(link_stmt)
                        oc_cat_id = link_res.scalar()
                        if oc_cat_id and oc_cat_id in cat_map:
                            new_prod.category_id = cat_map[oc_cat_id]

                        self.session.add(new_prod)
                        
                        # Add default variant
                        variant = ProductVariant(
                            product=new_prod,
                            sku=oc_prod.sku or f"OC-{oc_prod.product_id}",
                            price=oc_prod.price,
                            stock_quantity=oc_prod.quantity,
                            name="Default"
                        )
                        self.session.add(variant)

                        # Download images via httpx to settings.MEDIA_ROOT / "products"
                        if oc_prod.image:
                            image_url = f"{settings.OC_SITE_URL.rstrip('/')}/image/{oc_prod.image}"
                            local_path = await self._download_image(client, image_url, "products")
                            if local_path:
                                img_obj = ProductImage(
                                    product=new_prod,
                                    url=local_path,
                                    is_cover=True,
                                    alt=name
                                )
                                self.session.add(img_obj)

                        processed += 1
                    
                    last_id = oc_prod.product_id

            # Update job stats
            job.processed += processed
            job.skipped += skipped
            job.last_oc_id = last_id
            
            await self.session.commit()
            
            if len(products) < self.batch_size:
                await self.repo.update_job_status(job.id, MigrationStatus.DONE)

    async def migrate_orders(self, job: MigrationJob):
        async with OCAsyncSessionLocal() as oc_session:
            stmt = (
                select(OCOrder)
                .where(OCOrder.order_id > (job.last_oc_id or 0))
                .order_by(OCOrder.order_id)
                .limit(self.batch_size)
            )
            result = await oc_session.execute(stmt)
            orders = result.scalars().all()

            if not orders:
                await self.repo.update_job_status(job.id, MigrationStatus.DONE)
                return

            processed = 0
            skipped = 0
            last_id = job.last_oc_id or 0

            # Status mapping: OC 1->PENDING, 2->PROCESSING, 5->DELIVERED, 7/14->CANCELLED.
            status_map = {
                1: OrderStatus.PENDING,
                2: OrderStatus.PROCESSING,
                5: OrderStatus.DELIVERED,
                7: OrderStatus.CANCELLED,
                14: OrderStatus.CANCELLED
            }

            for oc_order in orders:
                # Idempotency check: use oc_order_id
                order_check_stmt = select(Order).where(Order.oc_order_id == oc_order.order_id)
                existing = await self.session.execute(order_check_stmt)
                if existing.scalar_one_or_none():
                    skipped += 1
                else:
                    # Link to migrated users and products
                    email_hash = get_blind_index(oc_order.email)
                    user_stmt = select(User).where(User.email_hash == email_hash)
                    user_res = await self.session.execute(user_stmt)
                    user = user_res.scalar_one_or_none()
                    
                    new_order = Order(
                        user_id=user.id if user else None,
                        status=status_map.get(oc_order.order_status_id, OrderStatus.PENDING),
                        total_amount=oc_order.total,
                        currency=oc_order.currency_code,
                        shipping_address=f"{oc_order.shipping_address_1}, {oc_order.shipping_city}, {oc_order.shipping_country}",
                        oc_order_id=oc_order.order_id,
                        created_at=oc_order.date_added.replace(tzinfo=timezone.utc) if oc_order.date_added else datetime.now(timezone.utc)
                    )
                    self.session.add(new_order)
                    
                    # Migrate order items
                    item_stmt = select(OCOrderProduct).where(OCOrderProduct.order_id == oc_order.order_id)
                    item_res = await oc_session.execute(item_stmt)
                    oc_items = item_res.scalars().all()
                    
                    for oc_item in oc_items:
                        # Find variant by oc_product_id
                        var_stmt = select(ProductVariant).join(Product).where(Product.oc_product_id == oc_item.product_id)
                        var_res = await self.session.execute(var_stmt)
                        variant = var_res.scalar_one_or_none()
                        
                        if variant:
                            order_item = OrderItem(
                                order=new_order,
                                product_variant_id=variant.id,
                                quantity=oc_item.quantity,
                                price=oc_item.price
                            )
                            self.session.add(order_item)

                    processed += 1
                
                last_id = oc_order.order_id

            # Update job stats
            job.processed += processed
            job.skipped += skipped
            job.last_oc_id = last_id
            
            await self.session.commit()
            
            if len(orders) < self.batch_size:
                await self.repo.update_job_status(job.id, MigrationStatus.DONE)

    async def _migrate_categories(self):
        """Migrate all categories recursively if they don't exist"""
        async with OCAsyncSessionLocal() as oc_session:
            stmt = select(OCCategory).order_by(OCCategory.parent_id, OCCategory.sort_order)
            result = await oc_session.execute(stmt)
            oc_categories = result.scalars().all()
            
            oc_id_map = {cat.category_id: cat for cat in oc_categories}
            migrated_map = {}
            
            existing_stmt = select(Category).where(Category.oc_category_id.is_not(None))
            existing_res = await self.session.execute(existing_stmt)
            for cat in existing_res.scalars().all():
                migrated_map[cat.oc_category_id] = cat.id

            async def get_or_create_category(oc_id: int) -> Optional[UUID]:
                if oc_id == 0:
                    return None
                if oc_id in migrated_map:
                    return migrated_map[oc_id]
                
                oc_cat = oc_id_map.get(oc_id)
                if not oc_cat:
                    return None
                
                parent_uuid = await get_or_create_category(oc_cat.parent_id)
                
                desc_stmt = select(OCCategoryDescription).where(
                    OCCategoryDescription.category_id == oc_id,
                    OCCategoryDescription.language_id == settings.OC_LANGUAGE_ID
                )
                desc_res = await oc_session.execute(desc_stmt)
                oc_desc = desc_res.scalar_one_or_none()
                
                name = oc_desc.name if oc_desc else f"Category {oc_id}"
                slug = self._slugify(name)
                slug = await self._ensure_unique_slug(Category, slug)
                
                new_cat = Category(
                    name=name,
                    slug=slug,
                    oc_category_id=oc_id,
                    parent_id=parent_uuid,
                    is_active=bool(oc_cat.status)
                )
                self.session.add(new_cat)
                await self.session.flush()
                
                migrated_map[oc_id] = new_cat.id
                return new_cat.id

            for oc_id in oc_id_map:
                await get_or_create_category(oc_id)
            
            await self.session.commit()

    async def _download_image(self, client: httpx.AsyncClient, url: str, folder: str) -> Optional[str]:
        try:
            filename = os.path.basename(url)
            if not filename:
                return None
            filename = "".join(c for c in filename if c.isalnum() or c in "._-").rstrip()
            
            rel_path = f"{folder}/{filename}"
            full_path = Path(settings.MEDIA_ROOT) / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if not full_path.exists():
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    with open(full_path, "wb") as f:
                        f.write(response.content)
                else:
                    return None
            return f"{settings.MEDIA_URL.rstrip('/')}/{rel_path}"
        except Exception:
            return None

    def _slugify(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        return re.sub(r'[-\s]+', '-', text).strip('-')

    async def _ensure_unique_slug(self, model, slug: str) -> str:
        orig_slug = slug
        counter = 1
        while True:
            stmt = select(model).where(model.slug == slug)
            res = await self.session.execute(stmt)
            if not res.scalar_one_or_none():
                return slug
            slug = f"{orig_slug}-{counter}"
            counter += 1
