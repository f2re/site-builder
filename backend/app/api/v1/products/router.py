from typing import Any, Dict, List, Optional
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException, status

from app.api.v1.products.schemas import (
    CategoryListResponse,
    ProductPagination,
    ProductRead,
    ProductPriceCalculationRequest,
    ProductPriceCalculationResponse
)
from app.api.v1.products.service import ProductService
from app.integrations.meilisearch import meilisearch_provider

router = APIRouter(prefix="/products", tags=["Catalog"])

@router.post("/calculate-price", response_model=ProductPriceCalculationResponse)
async def calculate_product_price(
    data: ProductPriceCalculationRequest,
    service: ProductService = Depends()
):
    """
    Calculate final product price based on selected options.
    """
    return await service.calculate_price(data)

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

@router.get("", response_model=ProductPagination)
async def list_products(
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    category_slug: Optional[str] = Query(None, description="Filter by category slug"),
    min_price: Optional[Decimal] = Query(None, description="Filter by minimum price"),
    max_price: Optional[Decimal] = Query(None, description="Filter by maximum price"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination (created_at,id)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    service: ProductService = Depends(),
) -> ProductPagination:
    """
    Get a paginated list of products with filters.
    """
    return await service.get_products(
        category_id=category_id,
        category_slug=category_slug,
        min_price=min_price,
        max_price=max_price,
        is_featured=is_featured,
        cursor=cursor,
        per_page=per_page,
    )

@router.get("/categories", response_model=CategoryListResponse)
async def get_categories_tree(
    service: ProductService = Depends(),
) -> CategoryListResponse:
    """
    Get categories as a tree structure.
    """
    categories = await service.get_categories_tree()
    return CategoryListResponse(items=categories)

@router.get("/{slug}", response_model=ProductRead)
async def get_product_by_slug(
    slug: str,
    service: ProductService = Depends()
):
    """
    Get product details by slug.
    """
    return await service.get_product_by_slug(slug)

@router.get("/id/{product_id}", response_model=ProductRead)
async def get_product_by_id(
    product_id: UUID,
    service: ProductService = Depends()
):
    """
    Get product details by ID.
    """
    return await service.get_product_detail(product_id)
