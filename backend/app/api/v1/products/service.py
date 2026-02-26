# Module: api/v1/products/service.py | Agent: backend-agent | Task: phase3_backend_catalog
from typing import List, Optional, Any
from uuid import UUID
from decimal import Decimal
from fastapi import Depends, HTTPException, status

from app.api.v1.products.repository import ProductRepository, get_product_repo
from app.api.v1.products.schemas import ProductPagination, ProductRead, CategoryTreeRead

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
