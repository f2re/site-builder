# Module: delivery/router | Agent: backend-agent | Task: p16_backend_c2c_shipment

import dataclasses
from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.delivery.schemas import (
    AllPickupPointsResponse,
    AggregatedRateRequest,
    AggregatedRateResponse,
    C2CShipmentResponse,
    CityRead,
    DeliveryCalculateResponse,
    PickupPointRead,
)
from app.api.v1.delivery.service import delivery_service
from app.api.v1.orders.repository import OrderRepository
from app.core.dependencies import require_admin
from app.core.logging import logger
from app.db.models.user import User
from app.db.session import get_db
from app.integrations import ozon_delivery, wb_delivery
from app.integrations.ozon_delivery import C2CShipmentPayload as OzonC2CPayload
from app.integrations.wb_delivery import C2CShipmentPayload as WbC2CPayload

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


@router.post("/calculate-all", response_model=AggregatedRateResponse)
async def calculate_all_providers(body: AggregatedRateRequest) -> AggregatedRateResponse:
    """
    Получить тарифы от всех доступных провайдеров доставки параллельно.
    Кэшируется в Redis на 10 минут.
    """
    try:
        return await delivery_service.calculate_all_providers(
            from_city_code=body.from_city_code,
            to_city_code=body.to_city_code,
            weight_grams=body.weight_grams,
            length_cm=body.length_cm,
            width_cm=body.width_cm,
            height_cm=body.height_cm,
        )
    except Exception as e:
        logger.error("aggregated_delivery_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate delivery from all providers: {str(e)}"
        )


@router.get("/pickup-points-all", response_model=AllPickupPointsResponse)
async def get_all_pickup_points(
    city_code: int = Query(..., description="City code for PVZ"),
    provider: str = Query(None, description="Фильтр по провайдеру: cdek|pochta|ozon|wildberries")
) -> AllPickupPointsResponse:
    """
    Получить ПВЗ от всех провайдеров для города.
    """
    try:
        return await delivery_service.get_all_pickup_points(city_code, provider)
    except Exception as e:
        logger.error("aggregated_pvz_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pickup points from all providers: {str(e)}"
        )


@router.get("/orders/{order_id}/c2c-shipment", response_model=C2CShipmentResponse)
async def get_c2c_shipment(
    order_id: UUID,
    _admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> C2CShipmentResponse:
    """
    Сгенерировать карточку отправки C2C для Ozon или WB.
    Доступно только администраторам.
    """
    repo = OrderRepository(session)
    order = await repo.get_by_id(order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    provider = (order.delivery_provider or "").lower()
    if provider not in ("ozon", "wb"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider is not C2C (ozon/wb)",
        )

    # Resolve recipient data from order
    recipient_name: str = "Имя не указано"
    recipient_phone: str = "Телефон не указан"
    if order.user is not None:
        if order.user.name:
            recipient_name = order.user.name
        if order.user.phone:
            recipient_phone = order.user.phone

    pvz_code: str = order.tracking_number or "Не выбран"
    pvz_address: str = order.shipping_address or "Не указан"
    declared_value: Decimal = order.total_amount

    c2c_payload: OzonC2CPayload | WbC2CPayload
    if provider == "ozon":
        c2c_payload = ozon_delivery.generate_c2c_payload(
            order_id=str(order.id),
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            pvz_code=pvz_code,
            pvz_address=pvz_address,
            declared_value=declared_value,
        )
    else:
        c2c_payload = wb_delivery.generate_c2c_payload(
            order_id=str(order.id),
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            pvz_code=pvz_code,
            pvz_address=pvz_address,
            declared_value=declared_value,
        )

    return C2CShipmentResponse(**dataclasses.asdict(c2c_payload))
