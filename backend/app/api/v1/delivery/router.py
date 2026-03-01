# Module: delivery/router | Agent: backend-agent | Task: BE-03_cart_orders_payments (refined)

from fastapi import APIRouter, HTTPException, status, Query
from app.api.v1.delivery.service import delivery_service
from app.api.v1.delivery.schemas import DeliveryCalculateResponse, CityRead, PickupPointRead
from typing import List
from app.core.logging import logger

router = APIRouter(prefix="/delivery", tags=["Delivery"])

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
        return await delivery_service.calculate_delivery(
            from_city_code=from_city_code,
            to_city_code=to_city_code,
            weight_grams=weight_grams,
            tariff_code=tariff_code
        )
    except Exception as e:
        logger.error("cdek_calculation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate delivery cost: {str(e)}"
        )

@router.get("/pickup-points", response_model=List[PickupPointRead])
async def get_pickup_points(city_code: int = Query(..., description="City code for PVZ")):
    """
    Get PVZ (Pickup Points) for a given city.
    Optimized: Returns only necessary fields (address, work_time, phone, note, coordinates).
    Results are cached in Redis for 6 hours.
    """
    try:
        return await delivery_service.get_pickup_points(city_code)
    except Exception as e:
        logger.error("cdek_pvz_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pickup points: {str(e)}"
        )

@router.get("/cities", response_model=List[CityRead])
async def search_cities(
    query: str = Query(..., min_length=2, description="City name to search for"),
    country_codes: List[str] = Query(["RU"], description="Country codes (ISO 3166-1 alpha-2)")
):
    """
    Search for cities by name via CDEK API.
    """
    try:
        return await delivery_service.get_cities(query=query, country_codes=country_codes)
    except Exception as e:
        logger.error("cdek_city_search_error", error=str(e), query=query)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search cities: {str(e)}"
        )
