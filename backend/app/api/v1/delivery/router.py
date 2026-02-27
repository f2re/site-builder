from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from app.integrations.cdek import cdek_client
from decimal import Decimal
from app.core.logging import logger

router = APIRouter(prefix="/delivery", tags=["Delivery"])

class DeliveryCalculateResponse(BaseModel):
    cost_rub: Decimal
    days_min: int
    days_max: int
    tariff_code: str

@router.get("/calculate", response_model=DeliveryCalculateResponse)
async def calculate_delivery(
    from_city_code: int = Query(44, description="From city code (default Moscow)"),
    to_city_code: int = Query(..., description="To city code"),
    weight_grams: int = Query(500, description="Weight in grams"),
    tariff_code: int = Query(136, description="CDEK tariff code")
):
    """
    Calculate shipping cost and delivery days via CDEK v2 API.
    Response schema: { cost_rub: Decimal, days_min: int, days_max: int, tariff_code: str }
    """
    try:
        result = await cdek_client.calculate_tariff(
            from_city_code=from_city_code,
            to_city_code=to_city_code,
            weight_grams=weight_grams,
            tariff_code=tariff_code
        )
        return result
    except Exception as e:
        logger.error("cdek_calculation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate delivery cost: {str(e)}"
        )

@router.get("/pickup-points")
async def get_pickup_points(city_code: int = Query(..., description="City code for PVZ")):
    """
    Get PVZ (Pickup Points) for a given city.
    Results are cached for 6 hours in Redis.
    """
    try:
        points = await cdek_client.get_pickup_points(city_code)
        return points
    except Exception as e:
        logger.error("cdek_pvz_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pickup points: {str(e)}"
        )
