# Module: delivery/service | Agent: backend-agent | Task: BE-03_cart_orders_payments (refined)

import json
from typing import List
from app.integrations.cdek import cdek_client
from app.api.v1.delivery.schemas import (
    DeliveryCalculateResponse, CityRead, PickupPointRead,
    DeliveryOptionResponse, PickupPointResponse, AggregatedRateResponse, AllPickupPointsResponse
)
from app.api.v1.delivery.provider import PackageDimensions
from app.api.v1.delivery.aggregator import aggregator
from app.db.redis import get_redis_client
from app.core.logging import logger

class DeliveryService:
    async def get_cities(self, query: str, country_codes: List[str] = ["RU"]) -> List[CityRead]:
        """
        Search for cities and return as CityRead.
        """
        raw_cities = await cdek_client.get_cities(name=query, country_codes=country_codes)
        return [CityRead(**city) for city in raw_cities]

    async def calculate_delivery(
        self, 
        from_city_code: int, 
        to_city_code: int, 
        weight_grams: int, 
        tariff_code: int = 136
    ) -> DeliveryCalculateResponse:
        """
        Calculate delivery and return as DeliveryCalculateResponse.
        """
        result = await cdek_client.calculate_tariff(
            from_city_code=from_city_code,
            to_city_code=to_city_code,
            weight_grams=weight_grams,
            tariff_code=tariff_code
        )
        return DeliveryCalculateResponse(**result)

    async def get_pickup_points(self, city_code: int) -> List[PickupPointRead]:
        """
        Fetch pickup points, clean them up, and cache the cleaned version in Redis.
        Optimized for rapid map interactions by reducing payload size.
        """
        cache_key = f"cdek:pvz_clean:{city_code}"
        cached_pvz = await get_redis_client().get(cache_key)
        
        if cached_pvz:
            pvz_data = json.loads(cached_pvz)
            return [PickupPointRead(**p) for p in pvz_data]

        # Fetch raw data (it might be cached internally in CDEKClient too, but with raw fields)
        raw_points = await cdek_client.get_pickup_points(city_code)
        
        cleaned_points: List[PickupPointRead] = []
        for p in raw_points:
            try:
                # Extract first phone
                phone = ""
                if p.get("phones") and len(p["phones"]) > 0:
                    phone = p["phones"][0].get("number", "")
                
                # Transform to our schema
                cleaned_point = PickupPointRead(
                    code=p["code"],
                    name=p["name"],
                    address=p["location"]["address"],
                    latitude=p["location"]["latitude"],
                    longitude=p["location"]["longitude"],
                    work_time=p["work_time"],
                    phone=phone,
                    note=p.get("note") or p.get("address_comment")
                )
                cleaned_points.append(cleaned_point)
            except (KeyError, ValueError) as e:
                logger.warning("cdek_pvz_parse_error", point_code=p.get("code"), error=str(e))
                continue

        # Cache cleaned data for 6 hours
        await get_redis_client().set(
            cache_key, 
            json.dumps([p.model_dump() for p in cleaned_points]), 
            ex=6*3600
        )
        
        return cleaned_points

    async def calculate_all_providers(
        self,
        from_city_code: int,
        to_city_code: int,
        weight_grams: int,
        length_cm: int = 20,
        width_cm: int = 15,
        height_cm: int = 10,
    ) -> AggregatedRateResponse:
        cache_key = f"delivery:all:{from_city_code}:{to_city_code}:{weight_grams}"
        cached = await get_redis_client().get(cache_key)
        if cached:
            data = json.loads(cached)
            return AggregatedRateResponse(**data)

        dimensions = PackageDimensions(
            weight_grams=weight_grams,
            length_cm=length_cm,
            width_cm=width_cm,
            height_cm=height_cm,
        )
        options = await aggregator.calculate_all(from_city_code, to_city_code, dimensions)
        response = AggregatedRateResponse(
            options=[DeliveryOptionResponse(**opt.__dict__) for opt in options],
            total_providers=len(set(opt.provider for opt in options)),
        )
        await get_redis_client().set(cache_key, json.dumps(response.model_dump()), ex=600)
        return response

    async def get_all_pickup_points(
        self,
        city_code: int,
        provider_filter: str | None = None,
    ) -> AllPickupPointsResponse:
        points = await aggregator.get_all_pickup_points(city_code, provider_filter)
        return AllPickupPointsResponse(
            points=[PickupPointResponse(**p.__dict__) for p in points],
            total=len(points),
        )


delivery_service = DeliveryService()
