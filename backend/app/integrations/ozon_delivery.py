# Module: integrations/ozon_delivery | Agent: backend-agent | Task: p10_backend_delivery_providers
import httpx
import json
from decimal import Decimal
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.db.redis import redis_client
from app.core.logging import logger
from app.api.v1.delivery.provider import DeliveryOption, PickupPoint, PackageDimensions, ShipmentResult
from app.api.v1.delivery.city_mapping import CITY_MAPPING


class OzonDeliveryClient:
    def __init__(self):
        self.base_url = "https://api-seller.ozon.ru"
        self.timeout = 30.0

    def _get_headers(self) -> dict[str, str]:
        return {
            "Client-Id": settings.OZON_CLIENT_ID,
            "Api-Key": settings.OZON_API_KEY,
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def calculate_rate(
        self,
        from_city_code: int,
        to_city_code: int,
        dimensions: PackageDimensions,
    ) -> list[DeliveryOption]:
        if not settings.OZON_CLIENT_ID:
            return []

        cache_key = f"ozon:rate:{to_city_code}:{dimensions.weight_grams}"
        cached = await redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            return [DeliveryOption(**opt) for opt in data]

        to_city = CITY_MAPPING.get(to_city_code)
        if not to_city:
            logger.warning("ozon_city_not_mapped", to_code=to_city_code)
            return []

        payload = {
            "to_location": {"city_name": to_city["name"]},
            "weight": dimensions.weight_grams,
            "dimensions": {
                "length": dimensions.length_cm,
                "width": dimensions.width_cm,
                "height": dimensions.height_cm,
            }
        }

        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.post("/v2/posting/fbs/delivery-price", json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()

        options = [
            DeliveryOption(
                provider="ozon",
                provider_label="Ozon",
                service_type="pickup",
                service_name="Ozon доставка",
                cost_rub=Decimal(str(data.get("price", 0))),
                days_min=data.get("min_days", 2),
                days_max=data.get("max_days", 5),
                tariff_code="FBS",
                logo_url="/img/delivery/ozon.svg",
            )
        ]

        await redis_client.set(cache_key, json.dumps([opt.__dict__ for opt in options]), ex=600)
        return options

    async def get_pickup_points(self, city_code: int) -> list[PickupPoint]:
        return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def create_shipment(self, order_id: str, option: DeliveryOption) -> ShipmentResult:
        if not settings.OZON_CLIENT_ID:
            raise ValueError("OZON_CLIENT_ID not configured")

        payload = {"posting_number": order_id}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.post("/v2/posting/fbs/ship", json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()

        return ShipmentResult(
            provider="ozon",
            tracking_number=data.get("result", {}).get("posting_number", ""),
            status="created",
            raw=data,
        )


ozon_client = OzonDeliveryClient()
