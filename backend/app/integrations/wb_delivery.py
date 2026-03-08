# Module: integrations/wb_delivery | Agent: backend-agent | Task: p10_backend_delivery_providers
import httpx
import json
from decimal import Decimal
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.db.redis import redis_client
from app.api.v1.delivery.provider import DeliveryOption, PickupPoint, PackageDimensions, ShipmentResult
from app.api.v1.delivery.city_mapping import CITY_MAPPING


class WBDeliveryClient:
    def __init__(self):
        self.base_url = "https://marketplace-api.wildberries.ru"
        self.timeout = 30.0

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": settings.WB_API_KEY,
            "Content-Type": "application/json",
        }

    async def calculate_rate(
        self,
        from_city_code: int,
        to_city_code: int,
        dimensions: PackageDimensions,
    ) -> list[DeliveryOption]:
        if not settings.WB_API_KEY:
            return []

        weight_kg = dimensions.weight_grams / 1000
        if weight_kg <= 0.5:
            cost = Decimal("99")
        elif weight_kg <= 1.0:
            cost = Decimal("150")
        elif weight_kg <= 3.0:
            cost = Decimal("250")
        else:
            cost = Decimal("350")

        return [
            DeliveryOption(
                provider="wildberries",
                provider_label="Wildberries",
                service_type="pickup",
                service_name="WB доставка до ПВЗ",
                cost_rub=cost,
                days_min=2,
                days_max=5,
                tariff_code="WB_PICKUP",
                logo_url="/img/delivery/wildberries.svg",
            )
        ]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def get_pickup_points(self, city_code: int) -> list[PickupPoint]:
        if not settings.WB_API_KEY:
            return []

        cache_key = f"wb:warehouses:{city_code}"
        cached = await redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            return [PickupPoint(**p) for p in data]

        city = CITY_MAPPING.get(city_code)
        if not city:
            return []

        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.get("/api/v3/warehouses", headers=self._get_headers())
            response.raise_for_status()
            data = response.json()

        points = []
        for wh in data:
            if city["name"].lower() in wh.get("city", "").lower():
                points.append(
                    PickupPoint(
                        provider="wildberries",
                        code=str(wh["id"]),
                        name=wh["name"],
                        address=wh["address"],
                        latitude=wh.get("latitude", 0.0),
                        longitude=wh.get("longitude", 0.0),
                        work_time=wh.get("workTime", ""),
                        phone=wh.get("phone", ""),
                        note=None,
                    )
                )

        await redis_client.set(cache_key, json.dumps([p.__dict__ for p in points]), ex=3600)
        return points

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def create_shipment(self, order_id: str, option: DeliveryOption) -> ShipmentResult:
        if not settings.WB_API_KEY:
            raise ValueError("WB_API_KEY not configured")

        payload = {"name": order_id}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.post("/api/v3/supplies", json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()

        return ShipmentResult(
            provider="wildberries",
            tracking_number=data.get("id", ""),
            status="created",
            raw=data,
        )


wb_client = WBDeliveryClient()
