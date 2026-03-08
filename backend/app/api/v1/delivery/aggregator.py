# Module: delivery/aggregator | Agent: backend-agent | Task: p11_backend_user_addresses
import asyncio
from app.api.v1.delivery.provider import DeliveryOption, PickupPoint, PackageDimensions
from app.integrations.cdek import cdek_client
from app.integrations.pochta import pochta_client
from app.integrations import ozon_delivery, wb_delivery
from app.core.logging import logger


class CdekAdapter:
    """Adapter для cdek_client под Protocol DeliveryProvider."""

    async def calculate_rate(
        self,
        from_city_code: int,
        to_city_code: int,
        dimensions: PackageDimensions,
    ) -> list[DeliveryOption]:
        try:
            result = await cdek_client.calculate_tariff(
                from_city_code=from_city_code,
                to_city_code=to_city_code,
                weight_grams=dimensions.weight_grams,
                tariff_code=136
            )
            return [
                DeliveryOption(
                    provider="cdek",
                    provider_label="СДЭК",
                    service_type="pickup",
                    service_name="СДЭК до ПВЗ",
                    cost_rub=result["cost_rub"],
                    days_min=result["days_min"],
                    days_max=result["days_max"],
                    tariff_code=result["tariff_code"],
                    logo_url="/img/delivery/cdek.svg",
                )
            ]
        except Exception as e:
            logger.warning("cdek_adapter_error", error=str(e))
            return []

    async def get_pickup_points(self, city_code: int) -> list[PickupPoint]:
        try:
            raw_points = await cdek_client.get_pickup_points(city_code)
            points = []
            for p in raw_points:
                phone = ""
                if p.get("phones") and len(p["phones"]) > 0:
                    phone = p["phones"][0].get("number", "")

                points.append(
                    PickupPoint(
                        provider="cdek",
                        code=p["code"],
                        name=p["name"],
                        address=p["location"]["address"],
                        latitude=p["location"]["latitude"],
                        longitude=p["location"]["longitude"],
                        work_time=p["work_time"],
                        phone=phone,
                        note=p.get("note") or p.get("address_comment"),
                    )
                )
            return points
        except Exception as e:
            logger.warning("cdek_adapter_pvz_error", error=str(e))
            return []


class DeliveryAggregator:
    def __init__(self):
        self.cdek = CdekAdapter()
        self.providers_with_rate = {
            "cdek": self.cdek,
            "pochta": pochta_client,
        }
        self.providers_pvz = {
            "cdek": self.cdek,
            "pochta": pochta_client,
            "ozon": ozon_delivery,
            "wb": wb_delivery,
        }

    async def calculate_all(
        self,
        from_city_code: int,
        to_city_code: int,
        dimensions: PackageDimensions,
    ) -> list[DeliveryOption]:
        tasks = [
            self._safe_calculate(provider, from_city_code, to_city_code, dimensions, name)
            for name, provider in self.providers_with_rate.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        options = []
        for result in results:
            options.extend(result)
        return sorted(options, key=lambda x: x.cost_rub)

    async def get_all_pickup_points(
        self,
        city_code: int,
        provider_filter: str | None = None,
    ) -> list[PickupPoint]:
        if provider_filter:
            if provider_filter not in self.providers_pvz:
                return []
            provider = self.providers_pvz[provider_filter]
            return await self._safe_get_pvz(provider, city_code, provider_filter)

        tasks = [
            self._safe_get_pvz(provider, city_code, name)
            for name, provider in self.providers_pvz.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        points = []
        for result in results:
            points.extend(result)
        return points

    async def _safe_calculate(self, client, from_code, to_code, dimensions, provider_name):
        try:
            return await client.calculate_rate(from_code, to_code, dimensions)
        except Exception as e:
            logger.warning("delivery_provider_error", provider=provider_name, error=str(e))
            return []

    async def _safe_get_pvz(self, client, city_code, provider_name):
        try:
            return await client.get_pickup_points(city_code)
        except Exception as e:
            logger.warning("delivery_pvz_error", provider=provider_name, error=str(e))
            return []


aggregator = DeliveryAggregator()
