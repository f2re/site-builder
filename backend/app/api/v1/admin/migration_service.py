# Module: api/v1/admin/migration_service.py | Agent: backend-agent | Task: p10_backend_migration_fixes
import bleach
import httpx
import os
import re
import traceback
from uuid import UUID
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any, Type, TypeVar

from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import encrypt_data, get_blind_index
from app.db.opencart_session import OCAsyncSessionLocal
from app.db.opencart_models import (
    OCCustomer, OCProduct, OCProductDescription,
    OCCategory, OCCategoryDescription, OCOrder, OCOrderProduct,
    OCProductToCategory, OCProductImage,
)
from app.db.models.user import User
from app.db.models.product import Category, Product, ProductVariant, ProductImage
from app.db.models.order import Order, OrderItem, OrderStatus
from app.db.models.blog import Author, BlogPost, BlogPostStatus, Tag
from app.db.models.migration import MigrationJob, MigrationStatus, MigrationEntity
from .migration_repository import MigrationRepository

# Blog-category detection keywords (case-insensitive containment check)
BLOG_CATEGORY_KEYWORDS: frozenset[str] = frozenset({
    "новости", "статьи", "инструкции", "blog", "news", "articles", "статья", "новость", "инструкция", "manual",
})

# Allowed HTML tags for bleach strip (empty = strip all tags to plain text)
_BLEACH_ALLOWED_TAGS: list[str] = [
    "p", "br", "b", "i", "strong", "em", "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6", 
    "div", "span", "img", "a", "table", "thead", "tbody", "tr", "th", "td", "blockquote", "code", "pre"
]

T = TypeVar("T")

class MigrationService:
    def __init__(self, repo: MigrationRepository, session: AsyncSession):
        self.repo = repo
        self.session = session
        self.batch_size = 50

    async def start_migration(self, entity: Optional[MigrationEntity] = None) -> List[MigrationJob]:
        """Start migration for one or all entities."""
        if entity:
            entities = [entity]
        else:
            # All entities in recommended order
            entities = [
                MigrationEntity.USERS, 
                MigrationEntity.CATEGORIES, 
                MigrationEntity.PRODUCTS, 
                MigrationEntity.ORDERS
            ]
        
        jobs = []
        for ent in entities:
            active_job = await self.repo.get_active_job_by_entity(ent)
            if active_job:
                # If it's PAUSED or FAILED, we might want to restart it
                if active_job.status in [MigrationStatus.PAUSED, MigrationStatus.FAILED]:
                    await self.repo.update_job_status(active_job.id, MigrationStatus.PENDING)
                jobs.append(active_job)
                # Re-dispatch if PENDING
                if active_job.status == MigrationStatus.PENDING:
                    self._dispatch_task(active_job.id)
            else:
                new_job = await self.repo.create_job(ent)
                jobs.append(new_job)
                self._dispatch_task(new_job.id)

        return jobs

    def _dispatch_task(self, job_id: UUID) -> None:
        """Trigger Celery task for the job."""
        from app.tasks.migration_tasks import run_migration_task  # noqa: PLC0415
        from app.core.logging import logger  # noqa: PLC0415
        try:
            run_migration_task.delay(str(job_id))
            logger.info("migration_task_dispatched", job_id=str(job_id))
        except Exception as exc:
            logger.warning("migration_task_dispatch_failed", job_id=str(job_id), error=str(exc))

    async def get_all_jobs(self) -> List[MigrationJob]:
        return await self.repo.get_all_jobs()

    async def get_job(self, job_id: UUID) -> Optional[MigrationJob]:
        return await self.repo.get_job_by_id(job_id)

    async def pause_migration(self, job_id: UUID) -> Optional[MigrationJob]:
        return await self.repo.update_job_status(job_id, MigrationStatus.PAUSED)

    async def resume_migration(self, job_id: UUID) -> Optional[MigrationJob]:
        job = await self.repo.update_job_status(job_id, MigrationStatus.PENDING)
        if job:
            self._dispatch_task(job.id)
        return job

    async def pause_all(self) -> None:
        """Pause all running or pending jobs."""
        stmt = (
            update(MigrationJob)
            .where(MigrationJob.status.in_([MigrationStatus.RUNNING, MigrationStatus.PENDING]))
            .values(status=MigrationStatus.PAUSED)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def resume_all(self) -> None:
        """Resume all paused jobs."""
        # Find all paused jobs
        stmt = select(MigrationJob).where(MigrationJob.status == MigrationStatus.PAUSED)
        res = await self.session.execute(stmt)
        jobs = res.scalars().all()
        for job in jobs:
            await self.repo.update_job_status(job.id, MigrationStatus.PENDING)
            self._dispatch_task(job.id)
        await self.session.commit()

    async def reset_migration(self) -> Dict[str, str]:
        """Delete all migrated data and all MigrationJob rows.

        Deletion order (respects FK constraints):
        1. OrderItem rows linked to migrated orders
        2. Order rows where oc_order_id IS NOT NULL
        3. ProductImage rows for migrated products (cascade via product FK, but explicit for safety)
        4. ProductVariant rows for migrated products (cascade via product FK)
        5. Product rows where oc_product_id IS NOT NULL
        6. BlogPost rows where oc_product_id IS NOT NULL
        7. Category rows where oc_category_id IS NOT NULL (nullify children first)
        8. MigrationJob rows (all)
        """
        from app.core.logging import logger  # noqa: PLC0415

        # 1. Delete OrderItem rows for migrated orders
        migrated_order_ids_stmt = select(Order.id).where(Order.oc_order_id.is_not(None))
        migrated_order_ids = [row[0] for row in (await self.session.execute(migrated_order_ids_stmt)).all()]
        if migrated_order_ids:
            await self.session.execute(
                delete(OrderItem).where(OrderItem.order_id.in_(migrated_order_ids))
            )

        # 2. Delete migrated orders
        await self.session.execute(
            delete(Order).where(Order.oc_order_id.is_not(None))
        )

        # 3-4. Delete migrated products (cascade removes variants + images via DB cascade)
        await self.session.execute(
            delete(Product).where(Product.oc_product_id.is_not(None))
        )

        # 5. Delete migrated blog posts
        await self.session.execute(
            delete(BlogPost).where(BlogPost.oc_product_id.is_not(None))
        )

        # 6. Delete migrated categories — nullify parent_id on children first to avoid FK error
        migrated_cat_ids_stmt = select(Category.id).where(Category.oc_category_id.is_not(None))
        migrated_cat_ids = [row[0] for row in (await self.session.execute(migrated_cat_ids_stmt)).all()]
        if migrated_cat_ids:
            await self.session.execute(
                update(Category)
                .where(Category.parent_id.in_(migrated_cat_ids))
                .values(parent_id=None)
            )
            await self.session.execute(
                delete(Category).where(Category.id.in_(migrated_cat_ids))
            )

        # 7. Delete all MigrationJob rows
        await self.session.execute(delete(MigrationJob))

        await self.session.commit()
        logger.info("migration_reset_complete")
        return {"status": "ok", "message": "Migration data cleared"}

    async def get_migration_summary(self) -> Dict[str, Any]:
        """Get summary compatible with frontend MigrationStatus interface."""
        jobs = await self.get_all_jobs()
        # Group by entity, take latest job per entity
        entity_jobs: Dict[MigrationEntity, MigrationJob] = {}
        for job in sorted(jobs, key=lambda x: x.updated_at or datetime.min.replace(tzinfo=timezone.utc)):
            entity_jobs[job.entity] = job
        
        entities_data = {}
        total_items = 0
        processed_items = 0
        
        required_entities = [
            MigrationEntity.USERS, 
            MigrationEntity.CATEGORIES, 
            MigrationEntity.PRODUCTS, 
            MigrationEntity.ORDERS
        ]
        
        any_running = False
        any_paused = False
        any_failed = False
        all_completed = True
        any_started = False
        
        for ent in required_entities:
            job_opt: Optional[MigrationJob] = entity_jobs.get(ent)
            if job_opt:
                any_started = True
                status_str = job_opt.status.value.upper()
                if status_str == "DONE":
                    status_str = "COMPLETED"
                
                entities_data[ent.value] = {
                    "total": job_opt.total,
                    "processed": job_opt.processed,
                    "status": status_str,
                    "error": job_opt.errors[-1] if job_opt.errors else None
                }
                total_items += job_opt.total
                processed_items += job_opt.processed
                
                if job_opt.status == MigrationStatus.RUNNING:
                    any_running = True
                if job_opt.status == MigrationStatus.PAUSED:
                    any_paused = True
                if job_opt.status == MigrationStatus.FAILED:
                    any_failed = True
                if job_opt.status != MigrationStatus.DONE:
                    all_completed = False
            else:
                entities_data[ent.value] = {
                    "total": 0,
                    "processed": 0,
                    "status": "PENDING",
                    "error": None
                }
                all_completed = False

        overall_status = "IDLE"
        if any_running:
            overall_status = "RUNNING"
        elif any_paused:
            overall_status = "PAUSED"
        elif any_failed:
            overall_status = "FAILED"
        elif all_completed and any_started:
            overall_status = "COMPLETED"
        
        progress = (processed_items / total_items * 100) if total_items > 0 else 0
        if all_completed and any_started:
            progress = 100.0
        
        return {
            "overall_status": overall_status,
            "overall_progress": progress,
            "entities": entities_data
        }

    async def run_batch(self, job_id: UUID) -> None:
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
            should_retrigger = False
            if job.entity == MigrationEntity.USERS:
                should_retrigger = await self.migrate_users(job)
            elif job.entity in [MigrationEntity.PRODUCTS, MigrationEntity.CATEGORIES]:
                should_retrigger = await self.migrate_catalog(job)
            elif job.entity == MigrationEntity.ORDERS:
                should_retrigger = await self.migrate_orders(job)
            else:
                await self.repo.update_job_status(job_id, MigrationStatus.DONE)
            
            # Re-trigger if more data and still running
            if should_retrigger:
                await self.session.refresh(job)
                if job.status == MigrationStatus.RUNNING:
                    self._dispatch_task(job.id)
            
        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            await self.repo.update_job_status(
                job_id, 
                MigrationStatus.FAILED, 
                errors=(job.errors or []) + [error_msg]
            )
            raise

    async def migrate_users(self, job: MigrationJob) -> bool:
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
                return False

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
                return False
            return True

    async def migrate_catalog(self, job: MigrationJob) -> bool:
        from app.core.logging import logger  # noqa: PLC0415

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
                return False

            processed = 0
            skipped = 0
            last_id = job.last_oc_id or 0

            # Get category mapping oc_id -> our_uuid
            cat_stmt = select(Category.oc_category_id, Category.id).where(Category.oc_category_id.is_not(None))
            cat_res = await self.session.execute(cat_stmt)
            cat_map = {row[0]: row[1] for row in cat_res.all()}

            # --- 4a: Build blog_category_oc_ids set ---
            blog_category_oc_ids: set[int] = set()
            cat_desc_stmt = select(OCCategoryDescription).where(
                OCCategoryDescription.language_id == settings.OC_LANGUAGE_ID
            )
            cat_desc_res = await oc_session.execute(cat_desc_stmt)
            for cat_desc in cat_desc_res.scalars().all():
                name_lower = cat_desc.name.lower()
                if any(kw in name_lower for kw in BLOG_CATEGORY_KEYWORDS):
                    blog_category_oc_ids.add(cat_desc.category_id)

            # Find first Author for blog posts (required NOT NULL field)
            system_author: Optional[Author] = None
            author_stmt = select(Author).limit(1)
            author_res = await self.session.execute(author_stmt)
            system_author = author_res.scalar_one_or_none()
            if system_author is None:
                # Try to find first admin user and create author profile
                admin_stmt = select(User).where(User.role == "admin").limit(1)
                admin_res = await self.session.execute(admin_stmt)
                admin_user = admin_res.scalar_one_or_none()
                if admin_user:
                    system_author = Author(
                        user_id=admin_user.id,
                        display_name=admin_user.full_name or "System",
                    )
                    self.session.add(system_author)
                    await self.session.flush()

            async with httpx.AsyncClient() as client:
                for oc_prod in products:
                    # Get description
                    desc_stmt = select(OCProductDescription).where(
                        OCProductDescription.product_id == oc_prod.product_id,
                        OCProductDescription.language_id == settings.OC_LANGUAGE_ID,
                    )
                    desc_res = await oc_session.execute(desc_stmt)
                    oc_desc = desc_res.scalar_one_or_none()

                    # Get all category links for this product
                    link_stmt = select(OCProductToCategory.category_id).where(
                        OCProductToCategory.product_id == oc_prod.product_id
                    )
                    link_res = await oc_session.execute(link_stmt)
                    oc_cat_ids: list[int] = [row[0] for row in link_res.all()]

                    # --- 4b: Route to BlogPost or Product ---
                    is_blog = any(cid in blog_category_oc_ids for cid in oc_cat_ids)

                    if is_blog:
                        # Blog idempotency check
                        blog_check_stmt = select(BlogPost).where(
                            BlogPost.oc_product_id == oc_prod.product_id
                        )
                        existing_blog = await self.session.execute(blog_check_stmt)
                        if existing_blog.scalar_one_or_none():
                            skipped += 1
                        elif system_author is None:
                            logger.warning(
                                "migrate_catalog_skip_blog_no_author",
                                oc_product_id=oc_prod.product_id,
                            )
                            skipped += 1
                        else:
                            title = oc_desc.name if oc_desc else f"Post {oc_prod.product_id}"
                            slug = self._slugify(title)
                            slug = await self._ensure_unique_slug(BlogPost, slug)

                            cover_image: Optional[str] = None
                            if oc_prod.image:
                                image_url = f"{settings.OC_SITE_URL.rstrip('/')}/image/{oc_prod.image}"
                                cover_image = await self._download_image(client, image_url, "blog")

                            # Preserve more HTML for blog posts
                            raw_html = oc_desc.description or "" if oc_desc else ""
                            cleaned_html = bleach.clean(raw_html, tags=_BLEACH_ALLOWED_TAGS, strip=False)

                            new_post = BlogPost(
                                title=title,
                                slug=slug,
                                content_html=cleaned_html,
                                content_json={},
                                status=(
                                    BlogPostStatus.PUBLISHED if oc_prod.status else BlogPostStatus.DRAFT
                                ),
                                published_at=(
                                    oc_prod.date_added.replace(tzinfo=timezone.utc)
                                    if oc_prod.date_added
                                    else datetime.now(timezone.utc)
                                ),
                                oc_product_id=oc_prod.product_id,
                                author_id=system_author.id,
                                cover_image=cover_image,
                            )

                            # Parse tags from meta_keyword
                            raw_keywords = (oc_desc.meta_keyword or "") if oc_desc else ""
                            tag_names: list[str] = [
                                t.strip() for t in re.split(r"[,\s]+", raw_keywords) if t.strip()
                            ]
                            tag_names.append("импорт")
                            
                            # Add category name as tag
                            for oc_cid in oc_cat_ids:
                                cat_desc_stmt2 = select(OCCategoryDescription).where(
                                    OCCategoryDescription.category_id == oc_cid,
                                    OCCategoryDescription.language_id == settings.OC_LANGUAGE_ID
                                )
                                cat_desc_res2 = await oc_session.execute(cat_desc_stmt2)
                                cd2 = cat_desc_res2.scalar_one_or_none()
                                if cd2:
                                    tag_names.append(cd2.name)

                            for tag_name in set(tag_names):
                                tag_slug = self._slugify(tag_name)
                                tag_stmt = select(Tag).where(Tag.slug == tag_slug)
                                tag_res = await self.session.execute(tag_stmt)
                                tag_obj = tag_res.scalar_one_or_none()
                                if tag_obj is None:
                                    tag_obj = Tag(name=tag_name, slug=tag_slug)
                                    self.session.add(tag_obj)
                                    await self.session.flush()
                                new_post.tags.append(tag_obj)

                            self.session.add(new_post)
                            processed += 1

                    else:
                        # Idempotency check: use oc_product_id
                        prod_check_stmt = select(Product).where(Product.oc_product_id == oc_prod.product_id)
                        existing = await self.session.execute(prod_check_stmt)
                        if existing.scalar_one_or_none():
                            skipped += 1
                        else:
                            name = oc_desc.name if oc_desc else f"Product {oc_prod.product_id}"
                            slug = self._slugify(name)
                            slug = await self._ensure_unique_slug(Product, slug)

                            # --- 4d: bleach for plain-text description ---
                            raw_description = oc_desc.description if oc_desc else ""
                            plain_description: Optional[str] = (
                                bleach.clean(raw_description, tags=[], strip=True)
                                if raw_description
                                else ""
                            )
                            # And preserve HTML version with allowed tags
                            html_description = (
                                bleach.clean(raw_description, tags=_BLEACH_ALLOWED_TAGS, strip=False)
                                if raw_description
                                else ""
                            )

                            new_prod = Product(
                                name=name,
                                slug=slug,
                                description=plain_description,
                                description_html=html_description,
                                meta_title=oc_desc.meta_title if oc_desc else None,
                                meta_description=oc_desc.meta_description if oc_desc else None,
                                oc_product_id=oc_prod.product_id,
                                is_active=bool(oc_prod.status),
                                created_at=(
                                    oc_prod.date_added.replace(tzinfo=timezone.utc)
                                    if oc_prod.date_added
                                    else datetime.now(timezone.utc)
                                ),
                            )

                            # Set category from first linked oc category
                            for oc_cat_id in oc_cat_ids:
                                if oc_cat_id in cat_map:
                                    new_prod.category_id = cat_map[oc_cat_id]
                                    break

                            self.session.add(new_prod)

                            # Add default variant
                            variant = ProductVariant(
                                product=new_prod,
                                sku=oc_prod.sku or f"OC-{oc_prod.product_id}",
                                price=oc_prod.price,
                                stock_quantity=oc_prod.quantity,
                                name="Default",
                            )
                            self.session.add(variant)

                            # Download cover image
                            if oc_prod.image:
                                image_url = f"{settings.OC_SITE_URL.rstrip('/')}/image/{oc_prod.image}"
                                local_path = await self._download_image(client, image_url, "products")
                                if local_path:
                                    img_obj = ProductImage(
                                        product=new_prod,
                                        url=local_path,
                                        is_cover=True,
                                        alt=name,
                                    )
                                    self.session.add(img_obj)

                            # --- 4c: Additional images from oc_product_image ---
                            add_imgs_stmt = (
                                select(OCProductImage)
                                .where(OCProductImage.product_id == oc_prod.product_id)
                                .order_by(OCProductImage.sort_order)
                            )
                            add_imgs_res = await oc_session.execute(add_imgs_stmt)
                            for oc_img in add_imgs_res.scalars().all():
                                if oc_img.image:
                                    add_url = f"{settings.OC_SITE_URL.rstrip('/')}/image/{oc_img.image}"
                                    add_path = await self._download_image(client, add_url, "products")
                                    if add_path:
                                        extra_img = ProductImage(
                                            product=new_prod,
                                            url=add_path,
                                            is_cover=False,
                                            alt=name,
                                        )
                                        self.session.add(extra_img)

                            processed += 1

                    last_id = oc_prod.product_id

            # Update job stats
            job.processed += processed
            job.skipped += skipped
            job.last_oc_id = last_id

            await self.session.commit()

            # --- 4e: Meilisearch sync ---
            try:
                from app.tasks.search_index import sync_products_to_meilisearch  # noqa: PLC0415
                sync_products_to_meilisearch.delay()
            except Exception:
                pass  # Non-critical

            if len(products) < self.batch_size:
                await self.repo.update_job_status(job.id, MigrationStatus.DONE)
                return False
            return True

    async def migrate_orders(self, job: MigrationJob) -> bool:
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
                return False

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
                return False
            return True


    async def _migrate_categories(self) -> None:
        """Migrate all categories recursively if they don't exist"""
        async with OCAsyncSessionLocal() as oc_session:
            stmt = select(OCCategory).order_by(OCCategory.parent_id, OCCategory.sort_order)
            result = await oc_session.execute(stmt)
            oc_categories = result.scalars().all()
            
            oc_id_map = {cat.category_id: cat for cat in oc_categories}
            migrated_map: Dict[int, UUID] = {}
            
            existing_stmt = select(Category).where(Category.oc_category_id.is_not(None))
            existing_res = await self.session.execute(existing_stmt)
            for cat in existing_res.scalars().all():
                if cat.oc_category_id is not None:
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

    async def _ensure_unique_slug(self, model: Type[T], slug: str) -> str:
        orig_slug = slug
        counter = 1
        while True:
            # We assume model has a .slug attribute
            stmt = select(model).where(model.slug == slug)  # type: ignore[attr-defined]
            res = await self.session.execute(stmt)
            if not res.scalar_one_or_none():
                return slug
            slug = f"{orig_slug}-{counter}"
            counter += 1
