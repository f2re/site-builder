# Module: api/v1/products/service.py | Agent: backend-agent | Task: product_service_crud
import bleach
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from fastapi import Depends, HTTPException, status

from app.api.v1.products.repository import ProductRepository, get_product_repo
from app.api.v1.products.schemas import (
    ProductPagination, 
    ProductRead, 
    CategoryTreeRead,
    ProductCreate,
    ProductUpdate
)
from app.db.models.product import Product
from app.tasks.search import index_product_task, remove_product_from_index_task

class ProductService:
    def __init__(self, repo: ProductRepository = Depends(get_product_repo)):
        self.repo = repo

    async def get_products(
        self,
        category_id: Optional[UUID] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        cursor: Optional[UUID] = None,
        per_page: int = 20,
    ) -> ProductPagination:
        items, next_cursor = await self.repo.list_products(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            cursor=cursor,
            per_page=per_page
        )
        return ProductPagination(
            items=items,
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
        product_dict = data.model_dump()
        if product_dict.get("description"):
            product_dict["description"] = bleach.clean(product_dict["description"])
        
        product = Product(**product_dict)
        created_product = await self.repo.create(product)
        
        # Refresh to ensure we have all fields for indexing (though for new product it's mostly same)
        # Prepare data for search indexing
        index_data = {
            "id": str(created_product.id),
            "name": created_product.name,
            "slug": created_product.slug,
            "description": created_product.description,
            "category_id": str(created_product.category_id) if created_product.category_id else None,
            "is_active": created_product.is_active
        }
        index_product_task.delay(index_data)
        
        return ProductRead.model_validate(created_product)

    async def update_product(self, product_id: UUID, data: ProductUpdate) -> ProductRead:
        """
        Update product, sanitize description, and update search index.
        """
        update_data = data.model_dump(exclude_unset=True)
        if "description" in update_data and update_data["description"]:
            update_data["description"] = bleach.clean(update_data["description"])
            
        updated_product = await self.repo.update(product_id, **update_data)
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
            
        # Update search index
        index_data = {
            "id": str(updated_product.id),
            "name": updated_product.name,
            "slug": updated_product.slug,
            "description": updated_product.description,
            "category_id": str(updated_product.category_id) if updated_product.category_id else None,
            "is_active": updated_product.is_active
        }
        index_product_task.delay(index_data)
        
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
