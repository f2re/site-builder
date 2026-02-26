from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
from app.integrations.cdek import cdek_client
from decimal import Decimal
from app.core.logging import logger

router = APIRouter(prefix="/delivery", tags=["Delivery"])

class DeliveryCalculateRequest(BaseModel):
    from_city_code: int = 44 # Default: Moscow
    to_city_code: int
    weight_grams: int = 500 # Default package weight

class DeliveryCalculateResponse(BaseModel):
    cost_rub: Decimal
    days_min: int
    days_max: int
    tariff_code: str

@router.post("/calculate", response_model=DeliveryCalculateResponse)
async def calculate_delivery(data: DeliveryCalculateRequest):
    """
    Calculate shipping cost and delivery days via CDEK v2 API.
    """
    try:
        result = await cdek_client.calculate_tariff(
            from_city_code=data.from_city_code,
            to_city_code=data.to_city_code,
            weight_grams=data.weight_grams
        )
        return result
    except Exception as e:
        logger.error("cdek_calculation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate delivery cost."
        )
