from typing import Any, Dict, List, Optional
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException, status

from app.api.v1.products.schemas import (
    ProductPagination,
    ProductRead,
    CategoryTreeRead
)
from app.api.v1.products.repository import ProductRepository, get_product_repo
from app.integrations.meilisearch import meilisearch_provider

router = APIRouter(prefix="/products", tags=["Catalog"])

@router.get("/search", response_model=Dict[str, Any])
async def search_products(
    q: str = Query("", description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    filter: Optional[List[str]] = Query(None),
    sort: Optional[List[str]] = Query(None),
):
    """
    Search products using Meilisearch.
    """
    try:
        results = await meilisearch_provider.search(
            index_name="products",
            query=q,
            limit=limit,
            offset=offset,
            filter=filter,
            sort=sort,
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Meilisearch error: {str(e)}"
        )

@router.get("/", response_model=ProductPagination)
async def list_products(
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    min_price: Optional[Decimal] = Query(None, description="Filter by minimum price"),
    max_price: Optional[Decimal] = Query(None, description="Filter by maximum price"),
    cursor: Optional[UUID] = Query(None, description="Cursor for pagination (Product ID)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    repo: ProductRepository = Depends(get_product_repo)
):
    """
    Get a paginated list of products with filters.
    """
    items, next_cursor = await repo.list_products(
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        cursor=cursor,
        per_page=per_page
    )
    return {
        "items": items,
        "next_cursor": next_cursor,
        "per_page": per_page
    }

@router.get("/categories", response_model=List[CategoryTreeRead])
async def get_categories_tree(
    repo: ProductRepository = Depends(get_product_repo)
):
    """
    Get categories as a tree structure.
    """
    return await repo.get_categories_tree()

@router.get("/{slug}", response_model=ProductRead)
async def get_product_by_slug(
    slug: str,
    repo: ProductRepository = Depends(get_product_repo)
):
    """
    Get product details by slug.
    """
    product = await repo.get_by_slug(slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.get("/id/{product_id}", response_model=ProductRead)
async def get_product_by_id(
    product_id: UUID,
    repo: ProductRepository = Depends(get_product_repo)
):
    """
    Get product details by ID.
    """
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product
