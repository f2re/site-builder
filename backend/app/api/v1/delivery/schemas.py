# Module: delivery/schemas | Agent: backend-agent | Task: BE-03_cart_orders_payments (refined)

from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional, List

class DeliveryCalculateResponse(BaseModel):
    cost_rub: Decimal
    days_min: int
    days_max: int
    tariff_code: str

    model_config = ConfigDict(from_attributes=True)

class CityRead(BaseModel):
    code: int
    city: str
    fias_guid: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PickupPointRead(BaseModel):
    code: str
    name: str
    address: str
    latitude: float
    longitude: float
    work_time: str
    phone: str
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DeliveryOptionResponse(BaseModel):
    provider: str
    provider_label: str
    service_type: str
    service_name: str
    cost_rub: Decimal
    days_min: int
    days_max: int
    tariff_code: str
    logo_url: str
    model_config = ConfigDict(from_attributes=True)


class PickupPointResponse(BaseModel):
    provider: str
    code: str
    name: str
    address: str
    latitude: float
    longitude: float
    work_time: str
    phone: str
    note: str | None = None
    model_config = ConfigDict(from_attributes=True)


class AggregatedRateRequest(BaseModel):
    from_city_code: int = 44
    to_city_code: int
    weight_grams: int = 500
    length_cm: int = 20
    width_cm: int = 15
    height_cm: int = 10


class AggregatedRateResponse(BaseModel):
    options: list[DeliveryOptionResponse]
    total_providers: int
    model_config = ConfigDict(from_attributes=True)


class AllPickupPointsResponse(BaseModel):
    points: list[PickupPointResponse]
    total: int
    model_config = ConfigDict(from_attributes=True)


class C2CShipmentResponse(BaseModel):
    provider: str
    order_id: str
    recipient_name: str
    recipient_phone: str
    pvz_code: str
    pvz_address: str
    declared_value: Decimal
    weight_kg: float
    comment: str
    deeplink: str
    instructions: List[str]
    model_config = ConfigDict(from_attributes=True)
