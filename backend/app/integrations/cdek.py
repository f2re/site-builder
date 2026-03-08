import httpx
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.db.redis import redis_client
from app.core.logging import logger
from decimal import Decimal
from typing import Dict, Any, List

class CDEKClient:
    """
    CDEK API v2 client with automatic token management and retry logic.
    """
    def __init__(self):
        # Sandbox: https://api.edu.cdek.ru/v2
        # Production: https://api.cdek.ru/v2
        self.base_url = "https://api.edu.cdek.ru/v2" if settings.DEBUG else "https://api.cdek.ru/v2"
        self.timeout = 30.0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def get_token(self) -> str:
        """
        OAuth2 token with Redis caching.
        Contract: CDEK OAuth2 token stored ONLY in Redis (`cdek:token`), NOT in DB or logs.
        """
        token = await redis_client.get("cdek:token")
        if token:
            return token.decode("utf-8") if isinstance(token, bytes) else token

        logger.info("cdek_auth_request", client_id=settings.CDEK_CLIENT_ID)
        
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.post(
                "/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.CDEK_CLIENT_ID,
                    "client_secret": settings.CDEK_CLIENT_SECRET,
                }
            )
            response.raise_for_status()
            data = response.json()
            
            token = data["access_token"]
            expires_in = data.get("expires_in", 3600)
            
            # Store in redis with 1-minute buffer
            await redis_client.set("cdek:token", token, ex=int(expires_in) - 60)
            return token

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def search_cities(self, query: str, country_codes: List[str] = ["RU"]) -> List[Dict[str, Any]]:
        """
        Search for cities by name via CDEK API.
        """
        token = await self.get_token()
        
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.get(
                "/location/cities",
                params={
                    "city": query,
                    "country_codes": ",".join(country_codes),
                    "size": 20
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 401:
                await redis_client.delete("cdek:token")
                response.raise_for_status()
                
            response.raise_for_status()
            return response.json()

    # Keep get_cities as alias or just replace it. 
    # The router currently uses get_cities.
    async def get_cities(self, name: str, country_codes: List[str] = ["RU"]) -> List[Dict[str, Any]]:
        return await self.search_cities(query=name, country_codes=country_codes)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def calculate_tariff(
        self, 
        from_city_code: int, 
        to_city_code: int, 
        weight_grams: int,
        tariff_code: int = 136 # Default to Warehouse-Warehouse (PVZ)
    ) -> Dict[str, Any]:
        """
        Calculate delivery cost.
        Response schema: { cost_rub: Decimal, days_min: int, days_max: int, tariff_code: str }
        """
        token = await self.get_token()
        
        payload = {
            "tariff_code": tariff_code,
            "from_location": {"code": from_city_code},
            "to_location": {"code": to_city_code},
            "packages": [{"weight": weight_grams}]
        }
        
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.post(
                "/calculator/tariff",
                json=payload,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 401:
                await redis_client.delete("cdek:token")
                response.raise_for_status()
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "cost_rub": Decimal(str(data["total_sum"])),
                "days_min": data["period_min"],
                "days_max": data["period_max"],
                "tariff_code": str(tariff_code)
            }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def get_pickup_points(self, city_code: int) -> List[Dict[str, Any]]:
        """
        PVZ list cached in Redis with TTL 6h: key `cdek:pvz:{city_code}`
        """
        cache_key = f"cdek:pvz:{city_code}"
        cached_pvz = await redis_client.get(cache_key)
        if cached_pvz:
            return json.loads(cached_pvz)

        token = await self.get_token()
        
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.get(
                "/deliverypoints",
                params={"city_code": city_code, "type": "ALL"},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 401:
                await redis_client.delete("cdek:token")
                response.raise_for_status()
            
            response.raise_for_status()
            pvz_list = response.json()
            
            await redis_client.set(cache_key, json.dumps(pvz_list), ex=6*3600)
            return pvz_list

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create delivery order in CDEK.
        
        The order_data MUST be a dict compatible with CDEK API v2 POST /orders.
        Example mapping from internal Order model:
        {
            "type": 1,
            "number": str(order.id),
            "tariff_code": order.tariff_code,
            "recipient": {
                "name": order.user.full_name,
                "phones": [{"number": order.user.phone}]
            },
            "to_location": {
                "code": order.city_code,
                "address": order.shipping_address
            },
            "packages": [
                {
                    "number": "pack-1",
                    "weight": total_weight,
                    "items": [
                        {"name": item.product.name, "ware_key": item.sku, "payment": {"value": 0}, ...}
                    ]
                }
            ]
        }
        """
        token = await self.get_token()
        
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.post(
                "/orders",
                json=order_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 401:
                await redis_client.delete("cdek:token")
                response.raise_for_status()
                
            response.raise_for_status()
            return response.json()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def get_order_status(self, cdek_number: str) -> Dict[str, Any]:
        """
        Get order status and full info.
        """
        token = await self.get_token()
        
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.get(
                f"/orders/{cdek_number}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 401:
                await redis_client.delete("cdek:token")
                response.raise_for_status()
                
            response.raise_for_status()
            return response.json()

    def get_tracking_url(self, tracking_number: str) -> str:
        """Generate CDEK tracking URL."""
        return f"https://www.cdek.ru/ru/tracking?order_id={tracking_number}"


cdek_client = CDEKClient()
