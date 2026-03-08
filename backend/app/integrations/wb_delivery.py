# Module: integrations/wb_delivery | Agent: backend-agent | Task: p11_backend_user_addresses
"""Wildberries C2C delivery via pickup points (no API, static data)."""
from app.api.v1.delivery.provider import PickupPoint
from app.api.v1.delivery.city_mapping import CITY_MAPPING


# Static WB pickup points (Moscow examples)
WB_PICKUP_POINTS = [
    PickupPoint(
        provider="wb",
        code="WB001",
        name="WB ПВЗ Ленинский проспект",
        address="г. Москва, Ленинский проспект, д. 45",
        latitude=55.707222,
        longitude=37.587778,
        work_time="Пн-Вс 09:00-21:00",
        phone="+7 (495) 456-78-90",
        note=None
    ),
    PickupPoint(
        provider="wb",
        code="WB002",
        name="WB ПВЗ Кутузовский",
        address="г. Москва, Кутузовский проспект, д. 36",
        latitude=55.741667,
        longitude=37.535556,
        work_time="Пн-Вс 10:00-22:00",
        phone="+7 (495) 567-89-01",
        note="2 этаж"
    ),
    PickupPoint(
        provider="wb",
        code="WB003",
        name="WB ПВЗ Таганская",
        address="г. Москва, ул. Таганская, д. 17",
        latitude=55.740556,
        longitude=37.653611,
        work_time="Пн-Вс 09:00-20:00",
        phone="+7 (495) 678-90-12",
        note="Вход с торца здания"
    ),
]


async def get_pickup_points(city_code: int) -> list[PickupPoint]:
    """Get Wildberries pickup points for city (static data)."""
    city = CITY_MAPPING.get(city_code)
    if not city:
        return []

    city_name = city["name"].lower()
    if city_name in ["москва", "moscow"]:
        return WB_PICKUP_POINTS
    return []
