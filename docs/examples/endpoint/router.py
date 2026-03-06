# Эталонный router — копируй этот паттерн для новых endpoint'ов
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import get_current_user, get_db
from app.api.v1.products.service import ProductService
from app.api.v1.products.schemas import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    service: ProductService = Depends(),
):
    product = await service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return product