# Module: products/router | Agent: backend-agent | Task: p3_backend_001
"""
Example FastAPI router implementation following the project's 4-file pattern.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.products.schemas import ProductCreate, ProductResponse
from app.api.v1.products.service import ProductService
from app.core.dependencies import get_product_service, require_role

router = APIRouter(prefix="/products", tags=["products"])

@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))]
)
async def create_product(
    product_in: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    """
    Creates a new product. Only admins can perform this action.
    """
    return await service.create_product(product_in)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service)
):
    """
    Retrieves a product by its ID.
    """
    product = await service.get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product
