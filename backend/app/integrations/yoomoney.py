import hmac
import hashlib
import datetime
from decimal import Decimal
from typing import Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings

class YooMoneyClient:
    """
    YooMoney (YooKassa API v3) integration.
    Unified endpoint for Sandbox and Production: https://api.yookassa.ru/v3
    """
    def __init__(self):
        self.shop_id = settings.YOOMONEY_SHOP_ID
        self.secret_key = settings.YOOMONEY_SECRET
        self.base_url = "https://api.yookassa.ru/v3"
        self.timeout = 30.0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def create_payment(
        self, 
        amount: Decimal, 
        order_id: str, 
        return_url: str, 
        description: str
    ) -> Dict[str, Any]:
        """
        Create a payment using YooKassa API.
        Response schema: { payment_url: str, payment_id: str, expires_at: datetime }
        """
        idempotency_key = f"order_{order_id}"
        payload = {
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description,
            "metadata": {
                "order_id": order_id
            }
        }
        
        async with httpx.AsyncClient(
            auth=(self.shop_id, self.secret_key), 
            timeout=self.timeout
        ) as client:
            response = await client.post(
                f"{self.base_url}/payments",
                json=payload,
                headers={"Idempotence-Key": idempotency_key}
            )
            response.raise_for_status()
            data = response.json()
            
            # YooKassa returns Z at the end of datetime strings
            expires_at_str = data.get("expires_at", "")
            if expires_at_str:
                expires_at = datetime.datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
            else:
                # Fallback if expires_at is missing
                expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)

            return {
                "payment_url": data["confirmation"]["confirmation_url"],
                "payment_id": data["id"],
                "expires_at": expires_at
            }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment details from YooKassa.
        """
        async with httpx.AsyncClient(
            auth=(self.shop_id, self.secret_key), 
            timeout=self.timeout
        ) as client:
            response = await client.get(f"{self.base_url}/payments/{payment_id}")
            response.raise_for_status()
            return response.json()

    @staticmethod
    def verify_webhook_signature(secret: str, body: bytes, signature: str) -> bool:
        """
        Verify YooMoney/YooKassa webhook signature.
        Contract: HMAC — compare_digest, not ==
        """
        expected_signature = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)

yoomoney_client = YooMoneyClient()
