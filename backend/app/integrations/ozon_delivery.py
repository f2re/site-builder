# Module: integrations/ozon_delivery | Agent: backend-agent | Task: p11_backend_user_addresses
"""Ozon C2C delivery via pickup points (no API, static data)."""
from app.api.v1.delivery.provider import PickupPoint
from app.api.v1.delivery.city_mapping import CITY_MAPPING


# Static Ozon pickup points (Moscow examples)
OZON_PICKUP_POINTS = [
    PickupPoint(
        provider="ozon",
        code="OZ001",
        name="Ozon ПВЗ Тверская",
        address="г. Москва, ул. Тверская, д. 12",
        latitude=55.764167,
        longitude=37.605278,
        work_time="Пн-Вс 10:00-22:00",
        phone="+7 (495) 123-45-67",
        note="Вход со двора"
    ),
    PickupPoint(
        provider="ozon",
        code="OZ002",
        name="Ozon ПВЗ Арбат",
        address="г. Москва, ул. Арбат, д. 25",
        latitude=55.751244,
        longitude=37.593522,
        work_time="Пн-Вс 09:00-21:00",
        phone="+7 (495) 234-56-78",
        note=None
    ),
    PickupPoint(
        provider="ozon",
        code="OZ003",
        name="Ozon ПВЗ Сокольники",
        address="г. Москва, ул. Русаковская, д. 13",
        latitude=55.789722,
        longitude=37.679167,
        work_time="Пн-Вс 10:00-20:00",
        phone="+7 (495) 345-67-89",
        note="Рядом с метро"
    ),
]


async def get_pickup_points(city_code: int) -> list[PickupPoint]:
    """Get Ozon pickup points for city (static data)."""
    city = CITY_MAPPING.get(city_code)
    if not city:
        return []

    city_name = city["name"].lower()
    if city_name in ["москва", "moscow"]:
        return OZON_PICKUP_POINTS
    return []


def get_tracking_url(tracking_number: str) -> str:
    """Generate Ozon tracking URL."""
    return f"https://www.ozon.ru/my/orderdetails?orderId={tracking_number}"
