import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.core.logging import logger
from decimal import Decimal
from typing import Dict, Any

class YooMoneyClient:
    """
    YooMoney Quickpay (Quickpay) for individual or Yookassa for corporate.
    This implementation uses Quickpay for individual users (simple form-based payments).
    """
    def __init__(self):
        self.receiver = settings.SMTP_USER # or other email-based identifier
        self.secret = settings.YOOMONEY_SECRET
        self.base_url = "https://yoomoney.ru/quickpay/confirm.xml"

    def create_payment_url(
        self, 
        amount: Decimal, 
        description: str, 
        label: str,
        success_url: str = "https://wifiobd.shop/success"
    ) -> str:
        """
        Construct a Quickpay payment URL.
        - receiver: account number or wallet email
        - quickpay-form: shop
        - targets: description
        - paymentType: PC (YooMoney balance), AC (Bank Card)
        - sum: amount
        - label: order_id (to match in webhook)
        """
        params = {
            "receiver": self.receiver,
            "quickpay-form": "shop",
            "targets": description,
            "paymentType": "AC", # Default to Card
            "sum": str(amount),
            "label": label,
            "successURL": success_url
        }
        
        # In actual implementation, for HTTP POST flow:
        # return f"https://yoomoney.ru/quickpay/confirm.xml?{httpx.QueryParams(params)}"
        
        # Simple redirect URL constructor
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://yoomoney.ru/quickpay/confirm.xml?{query}"

yoomoney_client = YooMoneyClient()
