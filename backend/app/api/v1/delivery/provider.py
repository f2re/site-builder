# Module: delivery/provider | Agent: backend-agent | Task: p10_backend_delivery_providers
from typing import Protocol, runtime_checkable
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PackageDimensions:
    weight_grams: int
    length_cm: int = 20
    width_cm: int = 15
    height_cm: int = 10


@dataclass
class DeliveryOption:
    provider: str
    provider_label: str
    service_type: str
    service_name: str
    cost_rub: Decimal
    days_min: int
    days_max: int
    tariff_code: str
    logo_url: str


@dataclass
class PickupPoint:
    provider: str
    code: str
    name: str
    address: str
    latitude: float
    longitude: float
    work_time: str
    phone: str
    note: str | None = None


@dataclass
class ShipmentResult:
    provider: str
    tracking_number: str
    status: str
    raw: dict


@runtime_checkable
class DeliveryProvider(Protocol):
    async def calculate_rate(
        self,
        from_city_code: int,
        to_city_code: int,
        dimensions: PackageDimensions,
    ) -> list[DeliveryOption]: ...

    async def get_pickup_points(
        self,
        city_code: int,
    ) -> list[PickupPoint]: ...

    async def create_shipment(
        self,
        order_id: str,
        option: DeliveryOption,
    ) -> ShipmentResult: ...
