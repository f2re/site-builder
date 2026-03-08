# Module: integrations/pochta | Agent: backend-agent | Task: p10_backend_delivery_providers
import httpx
import json
from decimal import Decimal
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.db.redis import redis_client
from app.core.logging import logger
from app.api.v1.delivery.provider import DeliveryOption, PickupPoint, PackageDimensions, ShipmentResult
from app.api.v1.delivery.city_mapping import CITY_MAPPING


class PochtaClient:
    def __init__(self):
        self.base_url = "https://otpravka-api.pochta.ru/1.0"
        self.timeout = 30.0

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"AccessToken {settings.POCHTA_API_TOKEN}",
            "X-User-Authorization": f"Basic {settings.POCHTA_USER_AUTHORIZATION}",
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
        if not settings.POCHTA_API_TOKEN:
            return []

        cache_key = f"pochta:rate:{from_city_code}:{to_city_code}:{dimensions.weight_grams}"
        cached = await redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            return [DeliveryOption(**opt) for opt in data]

        from_city = CITY_MAPPING.get(from_city_code)
        to_city = CITY_MAPPING.get(to_city_code)
        if not from_city or not to_city:
            logger.warning("pochta_city_not_mapped", from_code=from_city_code, to_code=to_city_code)
            return []

        payload = {
            "index-from": from_city["postal_code"],
            "index-to": to_city["postal_code"],
            "mail-type": "ONLINE_PARCEL",
            "mail-category": "ORDINARY",
            "mass": dimensions.weight_grams,
        }

        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.post("/tariff", json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()

        options = [
            DeliveryOption(
                provider="pochta",
                provider_label="Почта России",
                service_type="courier",
                service_name="Посылка онлайн",
                cost_rub=Decimal(str(data["total-rate"] / 100)),
                days_min=data.get("delivery-time", {}).get("min-days", 3),
                days_max=data.get("delivery-time", {}).get("max-days", 7),
                tariff_code="ONLINE_PARCEL",
                logo_url="/img/delivery/pochta.svg",
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
        if not settings.POCHTA_API_TOKEN:
            raise ValueError("POCHTA_API_TOKEN not configured")

        payload = {"order-num": order_id}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.post("/user/shipment", json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()

        return ShipmentResult(
            provider="pochta",
            tracking_number=data.get("barcode", ""),
            status="created",
            raw=data,
        )


pochta_client = PochtaClient()
