# Module: delivery/schemas | Agent: backend-agent | Task: BE-03_cart_orders_payments (refined)

from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional

class DeliveryCalculateResponse(BaseModel):
    cost_rub: Decimal
    days_min: int
    days_max: int
    tariff_code: str
    
    model_config = ConfigDict(from_attributes=True)

class CityRead(BaseModel):
    code: int
    city: str
    fias_guid: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class PickupPointRead(BaseModel):
    code: str
    name: str
    address: str
    latitude: float
    longitude: float
    work_time: str
    phone: str
    note: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
