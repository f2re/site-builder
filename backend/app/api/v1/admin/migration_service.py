# Module: api/v1/admin/migration_service.py | Agent: backend-agent | Task: p11_backend_002
import hashlib
import os
import re
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar
from urllib.parse import urlparse
from uuid import UUID, uuid4

import bleach
import httpx
from bs4 import BeautifulSoup, Tag as BSTag
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.security import encrypt_data, get_blind_index
from app.db.models.blog import Author, BlogPost, BlogPostStatus, Tag
from app.db.models.migration import MigrationEntity, MigrationJob, MigrationStatus
from app.db.models.order import Order, OrderItem, OrderStatus
from app.db.models.product import Category, Product, ProductImage, ProductVariant, ProductOptionGroup, ProductOptionValue
from app.db.models.user import User
from app.db.opencart_models import (
    OCCategory,
    OCCategoryDescription,
    OCCustomer,
    OCDevice,
    OCInformation,
    OCInformationDescription,
    OCOrder,
    OCOrderProduct,
    OCProduct,
    OCProductDescription,
    OCProductImage,
    OCProductToCategory,
    OCOption,
    OCOptionDescription,
    OCOptionValue,
    OCOptionValueDescription,
    OCProductOption,
    OCProductOptionValue,
)
from app.db.opencart_session import OCAsyncSessionLocal

from .migration_repository import MigrationRepository

# Blog-category detection keywords (case-insensitive containment check)
BLOG_CATEGORY_KEYWORDS: frozenset[str] = frozenset(
    {
        "новости",
        "статьи",
        "инструкции",
        "blog",
        "news",
        "articles",
        "статья",
        "новость",
        "инструкция",
        "manual",
    }
)

# Allowed HTML tags for bleach strip (empty = strip all tags to plain text)
_BLEACH_ALLOWED_TAGS: list[str] = [
    "p",
    "br",
    "b",
    "i",
    "strong",
    "em",
    "ul",
    "ol",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "div",
    "span",
    "img",
    "a",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "blockquote",
    "code",
    "pre",
    "font",
]

T = TypeVar("T")


class MigrationService:
    def __init__(self, repo: MigrationRepository, session: AsyncSession):
        self.repo = repo
        self.session = session
        self.batch_size = 50

    async def _html_to_tiptap(self, html: str, client: Optional[httpx.AsyncClient] = None) -> Dict[str, Any]:
        """Convert HTML to TipTap JSON format with support for nested tags, images, and sanitization."""
        if not html or not html.strip():
            return {"type": "doc", "content": []}

        soup = BeautifulSoup(html, "lxml")
        content = []

        def add_mark(marks: List[Dict[str, Any]], new_mark: Dict[str, Any]) -> None:
            for m in marks:
                if m["type"] == new_mark["type"]:
                    return
            marks.append(new_mark)

        async def process_children(parent: Any, active_marks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            result = []
            for child in parent.children:
                if isinstance(child, str):
                    text = str(child)
                    if text:
                        node: Dict[str, Any] = {"type": "text", "text": text}
                        if active_marks:
                            node["marks"] = [dict(m) for m in active_marks]
                        result.append(node)
                elif isinstance(child, BSTag) and child.name:
                    if child.name in ["script", "iframe"]:
                        continue

                    new_marks = [dict(m) for m in active_marks]
                    is_inline = False

                    if child.name in ["strong", "b"]:
                        add_mark(new_marks, {"type": "bold"})
                        is_inline = True
                    elif child.name in ["em", "i"]:
                        add_mark(new_marks, {"type": "italic"})
                        is_inline = True
                    elif child.name == "u":
                        add_mark(new_marks, {"type": "underline"})
                        is_inline = True
                    elif child.name == "a":
                        href = child.get("href", "")
                        add_mark(new_marks, {"type": "link", "attrs": {"href": href}})
                        is_inline = True
                    elif child.name in ["span", "font"]:
                        is_inline = True

                    if is_inline:
                        result.extend(await process_children(child, new_marks))
                    elif child.name == "br":
                        result.append({"type": "hardBreak"})
                    elif child.name == "img":
                        src_val = child.get("src", "")
                        src = src_val[0] if isinstance(src_val, list) else (src_val or "")
                        if src and isinstance(src, str) and src.startswith("http") and client:
                            new_src = await self._download_image(client, src, "content")
                            if new_src:
                                src = new_src
                        result.append(
                            {
                                "type": "image",
                                "attrs": {
                                    "src": src,
                                    "alt": child.get("alt", ""),
                                    "title": child.get("title", ""),
                                },
                            }
                        )
                    else:
                        node_result = await process_node(child)
                        if node_result:
                            result.append(node_result)
            return result

        async def process_node(node: Any) -> Optional[Dict[str, Any]]:
            if node.name in ["script", "iframe"]:
                return None

            if node.name in ["p", "div", "blockquote"]:
                type_name = "paragraph" if node.name != "blockquote" else "blockquote"
                inner_content = await process_children(node, [])
                if not inner_content:
                    return None

                # Special handling for blockquote: TipTap usually expects blocks inside
                if type_name == "blockquote":
                    return {"type": type_name, "content": [{"type": "paragraph", "content": inner_content}]}

                return {"type": type_name, "content": inner_content}

            elif node.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(node.name[1])
                return {"type": "heading", "attrs": {"level": level}, "content": await process_children(node, [])}

            elif node.name == "ul":
                items = []
                for child in node.children:
                    if child.name == "li":
                        item_content = await process_children(child, [])
                        if item_content:
                            items.append(
                                {"type": "listItem", "content": [{"type": "paragraph", "content": item_content}]}
                            )
                if not items:
                    return None
                return {"type": "bulletList", "content": items}

            elif node.name == "ol":
                items = []
                for child in node.children:
                    if child.name == "li":
                        item_content = await process_children(child, [])
                        if item_content:
                            items.append(
                                {"type": "listItem", "content": [{"type": "paragraph", "content": item_content}]}
                            )
                if not items:
                    return None
                return {"type": "orderedList", "content": items}

            elif node.name == "img":
                src_val = node.get("src", "")
                src = src_val[0] if isinstance(src_val, list) else (src_val or "")
                if src and isinstance(src, str) and src.startswith("http") and client:
                    new_src = await self._download_image(client, src, "content")
                    if new_src:
                        src = new_src
                return {
                    "type": "image",
                    "attrs": {"src": src, "alt": node.get("alt", ""), "title": node.get("title", "")},
                }

            return None

        body = soup.find("body")
        if body and isinstance(body, BSTag):
            for child in body.children:
                if isinstance(child, str):
                    text = child.strip()
                    if text:
                        content.append({"type": "paragraph", "content": [{"type": "text", "text": text}]})
                elif isinstance(child, BSTag) and child.name:
                    node_result = await process_node(child)
                    if node_result:
                        content.append(node_result)

        if not content:
            text = soup.get_text().strip()
            if text:
                content = [{"type": "paragraph", "content": [{"type": "text", "text": text}]}]

        return {"type": "doc", "content": content}

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
                MigrationEntity.ORDERS,
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
        from app.core.logging import logger  # noqa: PLC0415
        from app.tasks.migration_tasks import run_migration_task  # noqa: PLC0415

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
            await self.session.execute(delete(OrderItem).where(OrderItem.order_id.in_(migrated_order_ids)))

        # 2. Delete migrated orders
        await self.session.execute(delete(Order).where(Order.oc_order_id.is_not(None)))

        # 3-4. Delete migrated products (cascade removes variants + images via DB cascade)
        await self.session.execute(delete(Product).where(Product.oc_product_id.is_not(None)))

        # 5. Delete migrated blog posts
        await self.session.execute(delete(BlogPost).where(BlogPost.oc_product_id.is_not(None)))

        # 6. Delete migrated categories — nullify parent_id on children first to avoid FK error
        migrated_cat_ids_stmt = select(Category.id).where(Category.oc_category_id.is_not(None))
        migrated_cat_ids = [row[0] for row in (await self.session.execute(migrated_cat_ids_stmt)).all()]
        if migrated_cat_ids:
            await self.session.execute(
                update(Category).where(Category.parent_id.in_(migrated_cat_ids)).values(parent_id=None)
            )
            await self.session.execute(delete(Category).where(Category.id.in_(migrated_cat_ids)))

        # 7. Delete migrated (customer) users — preserve admins and superusers
        count_users_stmt = (
            select(func.count()).select_from(User).where(User.role == "customer", User.is_superuser.is_(False))
        )
        deleted_users_count = int((await self.session.execute(count_users_stmt)).scalar() or 0)
        await self.session.execute(delete(User).where(User.role == "customer").where(User.is_superuser.is_(False)))
        logger.info("migration_reset_users_deleted", count=deleted_users_count)

        # 8. Delete all MigrationJob rows
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
            MigrationEntity.ORDERS,
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
                    "error": job_opt.errors[-1] if job_opt.errors else None,
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
                entities_data[ent.value] = {"total": 0, "processed": 0, "status": "PENDING", "error": None}
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

        return {"overall_status": overall_status, "overall_progress": progress, "entities": entities_data}

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
            await self.repo.update_job_status(job_id, MigrationStatus.RUNNING, started_at=datetime.now(timezone.utc))
            await self.session.refresh(job)

        # Initialize total count if needed
        if job.total == 0:
            async with OCAsyncSessionLocal() as oc_session:
                count_stmt = None
                if job.entity == MigrationEntity.USERS:
                    count_stmt = select(func.count()).select_from(OCCustomer)
                elif job.entity in [MigrationEntity.PRODUCTS, MigrationEntity.CATEGORIES]:
                    # Count both information pages and products
                    info_count_stmt = select(func.count()).select_from(OCInformation)
                    info_res = await oc_session.execute(info_count_stmt)
                    info_count = int(info_res.scalar() or 0)

                    prod_count_stmt = select(func.count()).select_from(OCProduct)
                    prod_res = await oc_session.execute(prod_count_stmt)
                    prod_count = int(prod_res.scalar() or 0)

                    job.total = info_count + prod_count
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
                if not should_retrigger:
                    # Users migration complete, now migrate addresses in batches
                    metadata_u: Dict[str, Any] = job.extra_data or {}  # type: ignore[assignment]
                    if not metadata_u.get("addresses_done"):
                        addresses_retrigger = await self.migrate_addresses(job)
                        if addresses_retrigger:
                            should_retrigger = True
                        else:
                            metadata_u["addresses_done"] = True
                            await self.repo.update_job_status(
                                job.id, MigrationStatus.RUNNING, extra_data=metadata_u
                            )
                            await self.session.refresh(job)
                    if not should_retrigger and not metadata_u.get("devices_done"):
                        devices_retrigger = await self.migrate_devices(job)
                        if devices_retrigger:
                            should_retrigger = True
                        else:
                            metadata_u["devices_done"] = True
                            await self.repo.update_job_status(
                                job.id, MigrationStatus.DONE, extra_data=metadata_u
                            )
                            await self.session.refresh(job)
            elif job.entity in [MigrationEntity.PRODUCTS, MigrationEntity.CATEGORIES]:
                # First migrate information pages, then catalog
                metadata: Dict[str, Any] = job.extra_data or {}  # type: ignore[assignment]
                if not metadata.get("information_done"):
                    should_retrigger = await self.migrate_information(job)
                    if not should_retrigger:
                        # Information migration complete, switch to catalog
                        metadata["information_done"] = True
                        await self.repo.update_job_status(
                            job.id, MigrationStatus.RUNNING, last_oc_id=0, extra_data=metadata
                        )
                        await self.session.refresh(job)
                        should_retrigger = await self.migrate_catalog(job)
                else:
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
                job_id, MigrationStatus.FAILED, errors=(job.errors or []) + [error_msg]
            )
            raise

    async def migrate_users(self, job: MigrationJob) -> bool:
        from app.core.logging import logger  # noqa: PLC0415

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
                # Do NOT mark DONE here — run_batch orchestrates addresses/devices after users
                return False

            processed = 0
            skipped = 0
            last_id = job.last_oc_id or 0

            for oc_cust in customers:
                # Idempotency check: use get_blind_index(email)
                email_hash = get_blind_index(oc_cust.email)

                # If email_hash is empty or None (e.g. empty email), generate unique fallback
                if not email_hash:
                    email_hash = hashlib.sha256(str(uuid4()).encode()).hexdigest()

                check_stmt = select(User).where(User.email_hash == email_hash)
                existing = await self.session.execute(check_stmt)
                if existing.scalar_one_or_none():
                    skipped += 1
                    last_id = oc_cust.customer_id
                    continue

                try:
                    new_user = User(
                        email_hash=email_hash,
                        email=encrypt_data(oc_cust.email),
                        email_normalized=oc_cust.email.lower().strip(),
                        full_name=encrypt_data(f"{oc_cust.firstname} {oc_cust.lastname}"),
                        full_name_normalized=f"{oc_cust.firstname} {oc_cust.lastname}".lower().strip(),
                        phone=encrypt_data(oc_cust.telephone) if oc_cust.telephone else None,
                        phone_hash=get_blind_index(oc_cust.telephone) if oc_cust.telephone else None,
                        phone_normalized=oc_cust.telephone.lower().strip() if oc_cust.telephone else None,
                        hashed_password=oc_cust.password,  # Store OC hash as is
                        role="customer",
                        is_active=bool(oc_cust.status),
                        created_at=(
                            oc_cust.date_added.replace(tzinfo=timezone.utc)
                            if oc_cust.date_added
                            else datetime.now(timezone.utc)
                        ),
                    )
                    self.session.add(new_user)
                    await self.session.flush()
                    processed += 1
                except Exception as exc:
                    await self.session.rollback()
                    skipped += 1
                    logger.warning(
                        "migrate_users_skip",
                        oc_customer_id=oc_cust.customer_id,
                        error=str(exc),
                    )

                last_id = oc_cust.customer_id

            # Update job stats
            job.processed += processed
            job.skipped += skipped
            job.last_oc_id = last_id

            await self.session.commit()

            if len(customers) < self.batch_size:
                # Do NOT mark DONE here — run_batch orchestrates addresses/devices after users
                return False
            return True

    async def migrate_addresses(self, job: MigrationJob) -> bool:
        """Migrate customer addresses from OpenCart to delivery_addresses.

        Uses cursor-based pagination via extra_data['addresses_last_id'].
        Returns True if more batches remain, False when complete.
        """
        from app.core.logging import logger  # noqa: PLC0415
        from app.core.security import encrypt_data, get_blind_index  # noqa: PLC0415
        from app.db.models.delivery_address import AddressType, DeliveryAddress, DeliveryProvider  # noqa: PLC0415
        from app.db.opencart_models import OCAddress, OCCustomer  # noqa: PLC0415

        metadata: Dict[str, Any] = job.extra_data or {}  # type: ignore[assignment]
        last_addr_id: int = int(metadata.get("addresses_last_id") or 0)

        async with OCAsyncSessionLocal() as oc_session:
            stmt = (
                select(OCAddress)
                .where(OCAddress.address_id > last_addr_id)
                .order_by(OCAddress.address_id)
                .limit(self.batch_size)
            )
            result = await oc_session.execute(stmt)
            addresses = result.scalars().all()

            if not addresses:
                logger.info("migrate_addresses_complete", processed=0, skipped=0)
                return False

            processed = 0
            skipped = 0
            current_last_id = last_addr_id

            for oc_addr in addresses:
                current_last_id = oc_addr.address_id

                # Check idempotency
                check_stmt = select(DeliveryAddress).where(
                    DeliveryAddress.oc_address_id == oc_addr.address_id
                )
                existing = await self.session.execute(check_stmt)
                if existing.scalar_one_or_none():
                    skipped += 1
                    continue

                # Find customer in OpenCart
                cust_stmt = select(OCCustomer).where(OCCustomer.customer_id == oc_addr.customer_id)
                cust_result = await oc_session.execute(cust_stmt)
                oc_cust = cust_result.scalar_one_or_none()
                if not oc_cust:
                    skipped += 1
                    continue

                # Find user by email_hash
                email_hash = get_blind_index(oc_cust.email)
                user_stmt = select(User).where(User.email_hash == email_hash)
                user_result = await self.session.execute(user_stmt)
                user = user_result.scalar_one_or_none()
                if not user:
                    skipped += 1
                    continue

                try:
                    recipient_name = f"{oc_addr.firstname} {oc_addr.lastname}".strip()
                    full_address = f"{oc_addr.address_1} {oc_addr.address_2 or ''}".strip()

                    new_address = DeliveryAddress(
                        user_id=user.id,
                        name=f"Адрес {oc_addr.address_id}",
                        recipient_name=encrypt_data(recipient_name),
                        recipient_phone=encrypt_data(oc_cust.telephone),
                        recipient_phone_hash=get_blind_index(oc_cust.telephone),
                        full_address=encrypt_data(full_address),
                        address_type=AddressType.COURIER,
                        city=oc_addr.city,
                        postal_code=oc_addr.postcode,
                        provider=DeliveryProvider.MANUAL,
                        pickup_point_code=None,
                        is_default=(oc_addr.address_id == oc_cust.address_id),
                        oc_address_id=oc_addr.address_id,
                    )
                    self.session.add(new_address)
                    await self.session.flush()
                    processed += 1
                except Exception as exc:
                    await self.session.rollback()
                    skipped += 1
                    logger.warning(
                        "migrate_addresses_skip",
                        oc_address_id=oc_addr.address_id,
                        error=str(exc),
                    )

            job.skipped += skipped
            job.processed += processed

            # Persist cursor into extra_data
            metadata["addresses_last_id"] = current_last_id
            job.extra_data = metadata

            await self.session.commit()
            logger.info(
                "migrate_addresses_batch",
                processed=processed,
                skipped=skipped,
                last_addr_id=current_last_id,
            )

            # Retrigger if full batch fetched
            return len(addresses) == self.batch_size

    async def migrate_devices(self, job: MigrationJob) -> bool:
        """Migrate OBD/IoT devices from oc_devices to user_devices.

        Uses cursor-based pagination via extra_data['devices_last_id'].
        Looks up User by email_hash via OCCustomer join (same as migrate_addresses).
        Returns True if more batches remain, False when complete.
        """
        from app.core.logging import logger  # noqa: PLC0415
        from app.core.security import get_blind_index  # noqa: PLC0415
        from app.db.models.user_device import UserDevice  # noqa: PLC0415

        metadata: Dict[str, Any] = job.extra_data or {}  # type: ignore[assignment]
        last_device_id: int = int(metadata.get("devices_last_id") or 0)

        logger.info(
            "migrate_devices_start",
            job_id=str(job.id),
            last_device_id=last_device_id,
            addresses_done=metadata.get("addresses_done"),
            devices_done=metadata.get("devices_done"),
        )

        async with OCAsyncSessionLocal() as oc_session:
            # Сначала посчитаем общее количество записей в oc_devices
            total_stmt = select(func.count()).select_from(OCDevice)
            total_res = await oc_session.execute(total_stmt)
            total_in_oc = int(total_res.scalar() or 0)
            logger.info("migrate_devices_oc_total", total_in_oc_devices=total_in_oc)

            stmt = (
                select(OCDevice)
                .where(OCDevice.device_id > last_device_id)
                .order_by(OCDevice.device_id)
                .limit(self.batch_size)
            )
            result = await oc_session.execute(stmt)
            oc_devices = result.scalars().all()

            logger.info(
                "migrate_devices_fetched",
                fetched=len(oc_devices),
                cursor_from=last_device_id,
                batch_size=self.batch_size,
            )

            if not oc_devices:
                logger.info(
                    "migrate_devices_complete",
                    processed=0,
                    skipped=0,
                    total_in_oc=total_in_oc,
                    reason="no_rows_after_cursor",
                )
                return False

            migrated = 0
            skipped = 0
            errors_count = 0
            current_last_id = last_device_id

            for oc_dev in oc_devices:
                current_last_id = oc_dev.device_id

                logger.info(
                    "migrate_devices_row",
                    oc_device_id=oc_dev.device_id,
                    oc_customer_id=oc_dev.customer_id,
                    device_serial=oc_dev.device_serial,
                    device_name=oc_dev.device_name,
                    device_type=oc_dev.device_type,
                    register_date=str(oc_dev.register_date),
                )

                # Find customer in OpenCart to get email
                cust_stmt = select(OCCustomer).where(OCCustomer.customer_id == oc_dev.customer_id)
                cust_result = await oc_session.execute(cust_stmt)
                oc_cust = cust_result.scalar_one_or_none()
                if not oc_cust:
                    logger.warning(
                        "migrate_devices_no_customer",
                        oc_device_id=oc_dev.device_id,
                        oc_customer_id=oc_dev.customer_id,
                        reason="customer_not_found_in_oc_customer",
                    )
                    skipped += 1
                    continue

                logger.info(
                    "migrate_devices_customer_found",
                    oc_device_id=oc_dev.device_id,
                    oc_customer_id=oc_cust.customer_id,
                    email_preview=oc_cust.email[:3] + "***" if oc_cust.email else "EMPTY",
                    email_empty=not bool(oc_cust.email),
                )

                # Resolve User by email_hash
                email_hash = get_blind_index(oc_cust.email)
                logger.info(
                    "migrate_devices_email_hash",
                    oc_device_id=oc_dev.device_id,
                    email_hash_prefix=email_hash[:8] if email_hash else "NONE",
                )

                user_stmt = select(User).where(User.email_hash == email_hash)
                user_result = await self.session.execute(user_stmt)
                user = user_result.scalar_one_or_none()
                if not user:
                    logger.warning(
                        "migrate_devices_no_user",
                        oc_device_id=oc_dev.device_id,
                        oc_customer_id=oc_dev.customer_id,
                        email_hash_prefix=email_hash[:8] if email_hash else "NONE",
                        reason="user_not_found_by_email_hash_in_new_db",
                    )
                    skipped += 1
                    continue

                logger.info(
                    "migrate_devices_user_found",
                    oc_device_id=oc_dev.device_id,
                    user_id=str(user.id),
                )

                # Build device_uid — use serial if non-empty, else generate
                raw_serial = (oc_dev.device_serial or "").strip()
                if raw_serial:
                    device_uid = raw_serial
                    logger.info("migrate_devices_uid_serial", oc_device_id=oc_dev.device_id, device_uid=device_uid)
                else:
                    device_uid = f"oc-{oc_dev.device_id}-{uuid4().hex[:8]}"
                    logger.info(
                        "migrate_devices_uid_generated",
                        oc_device_id=oc_dev.device_id,
                        device_uid=device_uid,
                        reason="empty_serial",
                    )

                # Ensure registered_at is timezone-aware
                if oc_dev.register_date:
                    if oc_dev.register_date.tzinfo is None:
                        registered_at = oc_dev.register_date.replace(tzinfo=timezone.utc)
                    else:
                        registered_at = oc_dev.register_date
                else:
                    registered_at = datetime.now(timezone.utc)

                try:
                    new_device = UserDevice(
                        user_id=user.id,
                        device_uid=device_uid,
                        name=oc_dev.device_name or None,
                        model=oc_dev.device_type or None,
                        registered_at=registered_at,
                        comment=oc_dev.comment,
                        oc_device_id=oc_dev.device_id,
                        is_active=True,
                    )
                    self.session.add(new_device)
                    await self.session.flush()
                    migrated += 1
                    logger.info(
                        "migrate_devices_ok",
                        oc_device_id=oc_dev.device_id,
                        device_uid=device_uid,
                        user_id=str(user.id),
                    )
                except Exception as exc:
                    await self.session.rollback()
                    err_str = str(exc)
                    # ON CONFLICT SKIP for duplicate device_uid
                    if "unique" in err_str.lower() or "duplicate" in err_str.lower():
                        skipped += 1
                        logger.warning(
                            "migrate_devices_duplicate",
                            oc_device_id=oc_dev.device_id,
                            device_uid=device_uid,
                            error=err_str,
                        )
                    else:
                        errors_count += 1
                        logger.warning(
                            "migrate_devices_error",
                            oc_device_id=oc_dev.device_id,
                            device_uid=device_uid,
                            error=err_str,
                        )

            job.processed += migrated
            job.skipped += skipped
            job.failed += errors_count

            # Persist cursor into extra_data
            metadata["devices_last_id"] = current_last_id
            job.extra_data = metadata

            await self.session.commit()
            logger.info(
                "migrate_devices_batch",
                migrated=migrated,
                skipped=skipped,
                errors=errors_count,
                last_device_id=current_last_id,
                will_retrigger=len(oc_devices) == self.batch_size,
            )

            # Retrigger if full batch fetched
            return len(oc_devices) == self.batch_size

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
                    try:
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
                            blog_check_stmt = select(BlogPost).where(BlogPost.oc_product_id == oc_prod.product_id)
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
                                content_json = await self._html_to_tiptap(cleaned_html, client)

                                new_post = BlogPost(
                                    title=title,
                                    slug=slug,
                                    content_html=cleaned_html,
                                    content_json=content_json,
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
                                        OCCategoryDescription.language_id == settings.OC_LANGUAGE_ID,
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
                                await self.session.flush()
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
                                    bleach.clean(raw_description, tags=[], strip=True) if raw_description else ""
                                )
                                # And preserve HTML version with allowed tags
                                html_description = (
                                    bleach.clean(raw_description, tags=_BLEACH_ALLOWED_TAGS, strip=False)
                                    if raw_description
                                    else ""
                                )
                                # Convert HTML to TipTap JSON
                                content_json = await self._html_to_tiptap(html_description, client)

                                new_prod = Product(
                                    name=name,
                                    slug=slug,
                                    description=plain_description,
                                    description_html=html_description,
                                    content_json=content_json,
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
                                            product=new_prod, url=local_path, is_cover=True, alt=name
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
                                                product=new_prod, url=add_path, is_cover=False, alt=name
                                            )
                                            self.session.add(extra_img)


                                # --- 4f: Product Options ---
                                option_stmt = (
                                    select(OCProductOption, OCOption, OCOptionDescription)
                                    .join(OCOption, OCOption.option_id == OCProductOption.option_id)
                                    .join(OCOptionDescription, OCOptionDescription.option_id == OCOption.option_id)
                                    .where(
                                        OCProductOption.product_id == oc_prod.product_id,
                                        OCOptionDescription.language_id == settings.OC_LANGUAGE_ID
                                    )
                                )
                                option_res = await oc_session.execute(option_stmt)
                                options = option_res.all()
                                
                                for oc_prod_opt, oc_opt, oc_opt_desc in options:
                                    # map type
                                    opt_type = oc_opt.type
                                    if opt_type not in ('select', 'radio', 'checkbox'):
                                        opt_type = 'radio'
                                        
                                    opt_group = ProductOptionGroup(
                                        product=new_prod,
                                        name=oc_opt_desc.name,
                                        type=opt_type,
                                        is_required=oc_prod_opt.required,
                                        sort_order=oc_opt.sort_order
                                    )
                                    self.session.add(opt_group)
                                    await self.session.flush()
                                    
                                    val_stmt = (
                                        select(OCProductOptionValue, OCOptionValue, OCOptionValueDescription)
                                        .join(OCOptionValue, OCOptionValue.option_value_id == OCProductOptionValue.option_value_id)
                                        .join(OCOptionValueDescription, OCOptionValueDescription.option_value_id == OCOptionValue.option_value_id)
                                        .where(
                                            OCProductOptionValue.product_option_id == oc_prod_opt.product_option_id,
                                            OCOptionValueDescription.language_id == settings.OC_LANGUAGE_ID
                                        )
                                        .order_by(OCOptionValue.sort_order)
                                    )
                                    val_res = await oc_session.execute(val_stmt)
                                    
                                    for oc_prod_opt_val, oc_opt_val, oc_opt_val_desc in val_res.all():
                                        price_modifier = oc_prod_opt_val.price if oc_prod_opt_val.price_prefix == '+' else -oc_prod_opt_val.price if oc_prod_opt_val.price_prefix == '-' else oc_prod_opt_val.price
                                        
                                        opt_value = ProductOptionValue(
                                            group_id=opt_group.id,
                                            name=oc_opt_val_desc.name,
                                            price_modifier=price_modifier,
                                            sort_order=oc_opt_val.sort_order
                                        )
                                        self.session.add(opt_value)

                                await self.session.flush()
                                processed += 1

                    except Exception as exc:
                        await self.session.rollback()
                        skipped += 1
                        logger.warning(
                            "migrate_catalog_skip",
                            oc_product_id=oc_prod.product_id,
                            error=str(exc),
                        )

                    last_id = oc_prod.product_id

            # Update job stats
            job.processed += processed
            job.skipped += skipped
            job.last_oc_id = last_id

            await self.session.commit()

            # --- 4e: Meilisearch sync ---
            try:
                from app.tasks.search import sync_products_to_meilisearch_task  # noqa: PLC0415

                sync_products_to_meilisearch_task.delay()
            except Exception:
                pass  # Non-critical

            if len(products) < self.batch_size:
                await self.repo.update_job_status(job.id, MigrationStatus.DONE)
                return False
            return True

    async def migrate_information(self, job: MigrationJob) -> bool:
        """Migrate OCInformation (news/instructions pages) to BlogPost."""
        from app.core.logging import logger  # noqa: PLC0415

        async with OCAsyncSessionLocal() as oc_session:
            stmt = (
                select(OCInformation)
                .where(OCInformation.information_id > (job.last_oc_id or 0))
                .order_by(OCInformation.information_id)
                .limit(self.batch_size)
            )
            result = await oc_session.execute(stmt)
            infos = result.scalars().all()

            if not infos:
                await self.repo.update_job_status(job.id, MigrationStatus.DONE)
                return False

            # Find or create system author
            author_stmt = select(Author).limit(1)
            author_res = await self.session.execute(author_stmt)
            system_author = author_res.scalar_one_or_none()
            if not system_author:
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

            if not system_author:
                logger.warning("migrate_information_no_author")
                await self.repo.update_job_status(job.id, MigrationStatus.FAILED, errors=["No author found"])
                return False

            processed = 0
            skipped = 0

            async with httpx.AsyncClient() as client:
                for oc_info in infos:
                    # Check if already migrated
                    check_stmt = select(BlogPost).where(BlogPost.oc_information_id == oc_info.information_id)
                    existing = await self.session.execute(check_stmt)
                    if existing.scalar_one_or_none():
                        skipped += 1
                        continue

                    # Get description
                    desc_stmt = select(OCInformationDescription).where(
                        OCInformationDescription.information_id == oc_info.information_id,
                        OCInformationDescription.language_id == settings.OC_LANGUAGE_ID,
                    )
                    desc_res = await oc_session.execute(desc_stmt)
                    oc_desc = desc_res.scalar_one_or_none()

                    if not oc_desc:
                        skipped += 1
                        continue

                    title = oc_desc.title
                    slug = self._slugify(title)
                    slug = await self._ensure_unique_slug(BlogPost, slug)

                    # Convert HTML to TipTap
                    raw_html = oc_desc.description or ""
                    cleaned_html = bleach.clean(raw_html, tags=_BLEACH_ALLOWED_TAGS, strip=False)
                    content_json = await self._html_to_tiptap(cleaned_html, client)

                    new_post = BlogPost(
                        title=title,
                        slug=slug,
                        content_html=cleaned_html,
                        content_json=content_json,
                        status=BlogPostStatus.PUBLISHED if oc_info.status else BlogPostStatus.DRAFT,
                        published_at=(
                            oc_info.date_added.replace(tzinfo=timezone.utc)
                            if oc_info.date_added
                            else datetime.now(timezone.utc)
                        ),
                        oc_information_id=oc_info.information_id,
                        author_id=system_author.id,
                    )

                    # Create tags from meta_keyword
                    raw_keywords = oc_desc.meta_keyword or ""
                    tag_names = [t.strip() for t in re.split(r"[,\s]+", raw_keywords) if t.strip()]
                    tag_names.append("информация")

                    for tag_name in set(tag_names):
                        tag_slug = self._slugify(tag_name)
                        tag_stmt = select(Tag).where(Tag.slug == tag_slug)
                        tag_res = await self.session.execute(tag_stmt)
                        tag_obj = tag_res.scalar_one_or_none()
                        if not tag_obj:
                            tag_obj = Tag(name=tag_name, slug=tag_slug)
                            self.session.add(tag_obj)
                            await self.session.flush()
                        new_post.tags.append(tag_obj)

                    self.session.add(new_post)
                    processed += 1

            await self.session.commit()
            last_id = infos[-1].information_id
            await self.repo.update_job_status(
                job.id, MigrationStatus.RUNNING, last_oc_id=last_id, processed=job.processed + processed
            )
            logger.info("migrate_information_batch", processed=processed, skipped=skipped, last_id=last_id)
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
                14: OrderStatus.CANCELLED,
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
                        created_at=(
                            oc_order.date_added.replace(tzinfo=timezone.utc)
                            if oc_order.date_added
                            else datetime.now(timezone.utc)
                        ),
                    )
                    self.session.add(new_order)

                    # Migrate order items
                    item_stmt = select(OCOrderProduct).where(OCOrderProduct.order_id == oc_order.order_id)
                    item_res = await oc_session.execute(item_stmt)
                    oc_items = item_res.scalars().all()

                    for oc_item in oc_items:
                        # Find variant by oc_product_id
                        var_stmt = (
                            select(ProductVariant)
                            .join(Product)
                            .where(Product.oc_product_id == oc_item.product_id)
                        )
                        var_res = await self.session.execute(var_stmt)
                        variant = var_res.scalar_one_or_none()

                        if variant:
                            order_item = OrderItem(
                                order=new_order,
                                product_variant_id=variant.id,
                                quantity=oc_item.quantity,
                                price=oc_item.price,
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
                    OCCategoryDescription.language_id == settings.OC_LANGUAGE_ID,
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
                    is_active=bool(oc_cat.status),
                )
                self.session.add(new_cat)
                await self.session.flush()

                migrated_map[oc_id] = new_cat.id
                return new_cat.id

            for oc_id in oc_id_map:
                await get_or_create_category(oc_id)

            await self.session.commit()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
    async def _download_image(self, client: httpx.AsyncClient, url: str, folder: str) -> Optional[str]:
        from app.core.logging import logger  # noqa: PLC0415

        if not url or not url.strip():
            return None

        try:
            # Parse URL to remove query params
            parsed = urlparse(url)
            clean_path = parsed.path
            basename = os.path.basename(clean_path)

            if not basename:
                logger.warning("image_download_failed", url=url, error="empty basename")
                return None

            # Sanitize basename
            basename = "".join(c for c in basename if c.isalnum() or c in "._-").rstrip()

            # Download image
            response = await client.get(url, timeout=10.0, follow_redirects=True)

            if response.status_code != 200:
                logger.warning("image_download_failed", url=url, error=f"HTTP {response.status_code}")
                return None

            # Validate Content-Type
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                logger.warning("image_download_failed", url=url, error=f"invalid Content-Type: {content_type}")
                return None

            # Validate size
            if len(response.content) == 0:
                logger.warning("image_download_failed", url=url, error="empty content")
                return None

            # Extract extension from basename or Content-Type
            ext = ""
            if "." in basename:
                ext = basename.rsplit(".", 1)[1]
            elif "/" in content_type:
                mime_ext = content_type.split("/")[1].split(";")[0]
                ext = mime_ext if mime_ext in ["jpg", "jpeg", "png", "gif", "webp", "svg"] else "jpg"

            # Generate unique filename
            unique_id = uuid.uuid4().hex[:8]
            if ext:
                filename = f"{unique_id}_{basename}" if "." in basename else f"{unique_id}_{basename}.{ext}"
            else:
                filename = f"{unique_id}_{basename}"

            rel_path = f"{folder}/{filename}"
            full_path = Path(settings.MEDIA_ROOT) / rel_path

            try:
                full_path.parent.mkdir(parents=True, exist_ok=True)
            except PermissionError as perm_err:
                logger.error(
                    "media_permission_error",
                    path=str(full_path.parent),
                    error=str(perm_err),
                    solution="Check Docker volume permissions: ensure /app/media is writable by the container user",
                )
                raise

            # Write file
            with open(full_path, "wb") as f:
                f.write(response.content)

            result_url = f"{settings.MEDIA_URL.rstrip('/')}/{rel_path}"
            logger.info("image_downloaded", url=url, path=rel_path, size=len(response.content))
            return result_url

        except PermissionError:
            raise  # Re-raise to propagate to caller
        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.warning("image_download_failed", url=url, error=str(e))
            raise  # Let tenacity retry
        except Exception as e:
            logger.warning("image_download_failed", url=url, error=str(e))
            return None

    def _slugify(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        return re.sub(r"[-\s]+", "-", text).strip("-")

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
