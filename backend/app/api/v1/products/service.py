# Module: api/v1/products/service.py | Agent: backend-agent | Task: BE-01
import bleach
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from fastapi import Depends, HTTPException, status

from pydantic import TypeAdapter
from app.api.v1.products.repository import ProductRepository, get_product_repo
from app.api.v1.products.schemas import (
    ProductPagination, 
    ProductRead, 
    CategoryTreeRead,
    ProductCreate,
    ProductUpdate,
    ProductShortRead
)
from app.db.models.product import Product, ProductImage, ProductVariant
from app.tasks.search import index_product_task, remove_product_from_index_task

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
        cursor: Optional[UUID] = None,
        per_page: int = 20,
    ) -> ProductPagination:
        items, next_cursor = await self.repo.list_products(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            is_featured=is_featured,
            cursor=cursor,
            per_page=per_page
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

    async def create_product(self, data: ProductCreate) -> ProductRead:
        """
        Create a new product, sanitize description, and index in search.
        """
        product_dict = data.model_dump(exclude={"images", "variants"})
        
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
            
        created_product = await self.repo.create(product)
        
        # Prepare data for search indexing
        self._trigger_indexing(created_product)
        
        return ProductRead.model_validate(created_product)

    async def update_product(self, product_id: UUID, data: ProductUpdate) -> ProductRead:
        """
        Update product, sanitize description, and update search index.
        """
        update_data = data.model_dump(exclude_unset=True)
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
            
        # Update search index
        self._trigger_indexing(updated_product)
        
        return ProductRead.model_validate(updated_product)

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
        
        # Remove from search index
        remove_product_from_index_task.delay(str(product_id))

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
        index_product_task.delay(index_data)
