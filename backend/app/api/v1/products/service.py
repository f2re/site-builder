# Module: api/v1/products/service.py | Agent: backend-agent | Task: BE-01
import bleach
import uuid
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from fastapi import Depends, HTTPException, status, UploadFile

from pydantic import TypeAdapter
from app.core.logging import logger
from app.api.v1.products.repository import ProductRepository, get_product_repo
from app.api.v1.products.schemas import (
    ProductPagination,
    ProductRead,
    CategoryTreeRead,
    CategoryRead,
    CategoryCreate,
    CategoryUpdate,
    ProductCreate,
    ProductUpdate,
    ProductShortRead,
    ProductImageRead
)
from app.db.models.product import Product, ProductImage, ProductVariant, Category
from app.tasks.search import index_product_task, remove_product_from_index_task
from app.core.utils import generate_slug, extract_text_from_tiptap
from app.integrations.local_storage import storage_client

# Allowed tags and attributes for sanitization
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS | {
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'hr', 'div', 'span', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
}
ALLOWED_ATTRS = bleach.sanitizer.ALLOWED_ATTRIBUTES | {
    'img': ['src', 'alt', 'width', 'height', 'title', 'class'],
    'a': ['href', 'title', 'target', 'class'],
    '*': ['class', 'id', 'style']
}

class ProductService:
    def __init__(self, repo: ProductRepository = Depends(get_product_repo)):
        self.repo = repo

    async def get_products(
        self,
        category_id: Optional[UUID] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        is_featured: Optional[bool] = None,
        cursor: Optional[str] = None,
        per_page: int = 20,
        active_only: bool = True,
    ) -> ProductPagination:
        items, next_cursor = await self.repo.list_products(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            is_featured=is_featured,
            cursor=cursor,
            per_page=per_page,
            active_only=active_only
        )
        return ProductPagination(
            items=TypeAdapter(List[ProductShortRead]).validate_python(items),
            next_cursor=next_cursor,
            per_page=per_page
        )

    async def get_product_detail(self, product_id: UUID) -> ProductRead:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return ProductRead.model_validate(product)

    async def get_product_by_slug(self, slug: str) -> ProductRead:
        product = await self.repo.get_by_slug(slug)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return ProductRead.model_validate(product)

    async def get_categories_tree(self) -> List[CategoryTreeRead]:
        categories = await self.repo.get_categories_tree()
        return [CategoryTreeRead.model_validate(cat) for cat in categories]

    async def list_categories(self, active_only: bool = False) -> List[CategoryRead]:
        categories = await self.repo.list_categories(active_only=active_only)
        return [CategoryRead.model_validate(cat) for cat in categories]

    async def create_category(self, data: CategoryCreate) -> CategoryRead:
        category_dict = data.model_dump()
        category_dict["slug"] = generate_slug(data.name, data.slug)
        category = Category(**category_dict)
        created = await self.repo.create_category(category)
        await self.repo.session.commit()
        return CategoryRead.model_validate(created)

    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> CategoryRead:
        update_data = data.model_dump(exclude_unset=True)
        if "slug" in update_data:
            update_data["slug"] = generate_slug(update_data.get("name", ""), update_data["slug"])
        elif "name" in update_data:
            update_data["slug"] = generate_slug(update_data["name"])
            
        updated = await self.repo.update_category(category_id, **update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        await self.repo.session.commit()
        return CategoryRead.model_validate(updated)

    async def delete_category(self, category_id: UUID) -> None:
        success = await self.repo.delete_category(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        await self.repo.session.commit()

    async def create_product(self, data: ProductCreate) -> ProductRead:
        """
        Create a new product, sanitize description, and index in search.
        """
        product_dict = data.model_dump(exclude={"images", "variants"})
        product_dict["slug"] = generate_slug(data.name, data.slug)
        
        if product_dict.get("description"):
            product_dict["description"] = bleach.clean(product_dict["description"])
        
        if product_dict.get("description_html"):
            product_dict["description_html"] = bleach.clean(
                product_dict["description_html"],
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRS
            )
        
        product = Product(**product_dict)
        
        # Handle images
        if data.images:
            product.images = [ProductImage(**img.model_dump()) for img in data.images]
            
        # Handle variants
        if data.variants:
            product.variants = [ProductVariant(**var.model_dump()) for var in data.variants]
        
        # Apply Auto-SEO before creation
        self._apply_auto_seo(product)
            
        created_product = await self.repo.create(product)
        await self.repo.session.commit()
        
        # Reload with relationships to avoid MissingGreenlet during validation
        loaded_product = await self.repo.get_by_id(created_product.id)
        if not loaded_product:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Product could not be reloaded after creation"
            )
        
        # Prepare data for search indexing
        self._trigger_indexing(loaded_product)
        
        return ProductRead.model_validate(loaded_product)

    async def update_product(self, product_id: UUID, data: ProductUpdate) -> ProductRead:
        """
        Update product, sanitize description, and update search index.
        """
        update_data = data.model_dump(exclude_unset=True)
        
        if "slug" in update_data:
            update_data["slug"] = generate_slug(update_data.get("name", ""), update_data["slug"])
        elif "name" in update_data:
            update_data["slug"] = generate_slug(update_data["name"])

        if "description" in update_data and update_data["description"]:
            update_data["description"] = bleach.clean(update_data["description"])
            
        if "description_html" in update_data and update_data["description_html"]:
            update_data["description_html"] = bleach.clean(
                update_data["description_html"],
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRS
            )
            
        updated_product = await self.repo.update(product_id, **update_data)
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Apply Auto-SEO logic
        # We need to reload to have access to current fields for logic
        self._apply_auto_seo(updated_product)
        
        await self.repo.session.commit()
            
        # Reload with relationships
        loaded_product = await self.repo.get_by_id(updated_product.id)
        if not loaded_product:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Product could not be reloaded after update"
            )
        
        # Update search index
        self._trigger_indexing(loaded_product)
        
        return ProductRead.model_validate(loaded_product)

    async def delete_product(self, product_id: UUID) -> None:
        """
        Delete product and remove from search index.
        """
        success = await self.repo.delete(product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        await self.repo.session.commit()

        # Remove from search index (non-critical — log and continue on failure)
        try:
            remove_product_from_index_task.delay(str(product_id))
        except Exception as exc:
            logger.warning("search_index_removal_failed", product_id=str(product_id), error=str(exc))

    def _apply_auto_seo(self, product: Product) -> None:
        """Apply automatic SEO data if fields are empty."""
        if not product.meta_description and product.content_json:
            product.meta_description = extract_text_from_tiptap(product.content_json, 250)
            
        if not product.og_image_url and product.images:
            cover = next((img for img in product.images if img.is_cover), None)
            if not cover and product.images:
                cover = product.images[0]
            if cover:
                product.og_image_url = cover.url

    def _trigger_indexing(self, product: Product) -> None:
        index_data = {
            "id": str(product.id),
            "name": product.name,
            "slug": product.slug,
            "description": product.description,
            "category_id": str(product.category_id) if product.category_id else None,
            "is_active": product.is_active,
            "is_featured": product.is_featured
        }
        try:
            index_product_task.apply_async(args=[index_data], ignore_result=True)
        except Exception as exc:
            logger.warning("search_index_task_failed", product_id=index_data["id"], error=str(exc))

    # ─── Image Management ───
    async def upload_image(self, product_id: UUID, file: UploadFile) -> ProductImageRead:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        content = await file.read()
        object_name = f"products/{product_id}/{uuid.uuid4().hex[:8]}_{file.filename}"

        await storage_client.save_file(
            object_name=object_name,
            data=content,
            content_type=file.content_type or "image/jpeg"
        )

        url = storage_client.get_public_url(object_name)

        # Check if this is the first image, if so, make it cover
        is_cover = len(product.images) == 0

        new_image = await self.repo.add_image(product_id, url, alt=product.name, is_cover=is_cover)
        await self.repo.session.commit()

        return ProductImageRead.model_validate(new_image)

    async def delete_image(self, image_id: UUID) -> None:
        image = await self.repo.delete_image(image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Optional: remove from MinIO
        # object_name = image.url.split("/media/")[-1]
        # await minio_client.remove_object(minio_client.media_bucket, object_name)
        
        await self.repo.session.commit()

    async def set_cover_image(self, product_id: UUID, image_id: UUID) -> ProductImageRead:
        image = await self.repo.set_cover_image(product_id, image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found or not belonging to product")
        
        # Re-apply Auto-SEO to update og_image_url if it was empty
        product = await self.repo.get_by_id(product_id)
        if product:
            self._apply_auto_seo(product)
            
        await self.repo.session.commit()
        return ProductImageRead.model_validate(image)
