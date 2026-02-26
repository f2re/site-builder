import httpx
import json
from app.tasks.celery_app import celery_app
from app.db.redis import redis_client
from app.core.logging import logger

@celery_app.task(name="tasks.update_cbr_rates")
def update_cbr_rates():
    """Fetch currency rates from CBR and store them in Redis."""
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        with httpx.Client() as client:
            response = client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # Store full response for general use
            redis_client.set("cbr:rates:full", json.dumps(data), ex=3600*2)
            
            # Store simplified rates
            rates = {
                "USD": data["Valute"]["USD"]["Value"],
                "EUR": data["Valute"]["EUR"]["Value"],
                "CNY": data["Valute"]["CNY"]["Value"]
            }
            redis_client.set("cbr:rates", json.dumps(rates), ex=3600*2)
            
            logger.info("cbr_rates_updated", rates=rates)
            return rates
            
    except Exception as e:
        logger.error("cbr_rates_update_failed", error=str(e))
        raise
