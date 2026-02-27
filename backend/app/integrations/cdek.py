import httpx
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.db.redis import redis_client
from app.core.logging import logger
from decimal import Decimal
from typing import Dict, Any, List, Optional

class CDEKClient:
    def __init__(self):
        # Determine base URL based on debug mode or settings
        # CDEK v2 usually has different URLs for sandbox and production
        # We prefer using sandbox for DEBUG=True
        self.base_url = "https://api.edu.cdek.ru/v2" if settings.DEBUG else "https://api.cdek.ru/v2"
        self.timeout = 30.0

    async def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

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
                # Token might be invalid, clear cache and retry via tenacity
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
        PVZ list MUST be cached in Redis with TTL 6h: key `cdek:pvz:{city_code}`
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

cdek_client = CDEKClient()
