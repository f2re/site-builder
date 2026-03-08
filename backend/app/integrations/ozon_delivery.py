# Module: integrations/ozon_delivery | Agent: backend-agent | Task: p16_backend_c2c_shipment
"""Ozon C2C delivery via pickup points (no API, static data)."""
from dataclasses import dataclass, field
from decimal import Decimal

from app.api.v1.delivery.provider import PickupPoint
from app.api.v1.delivery.city_mapping import CITY_MAPPING


@dataclass
class C2CShipmentPayload:
    provider: str
    order_id: str
    recipient_name: str
    recipient_phone: str
    pvz_code: str
    pvz_address: str
    declared_value: Decimal
    weight_kg: float
    comment: str
    deeplink: str
    instructions: list[str] = field(default_factory=list)


def generate_c2c_payload(
    order_id: str,
    recipient_name: str,
    recipient_phone: str,
    pvz_code: str,
    pvz_address: str,
    declared_value: Decimal,
    weight_kg: float = 0.5,
    comment: str = "",
) -> C2CShipmentPayload:
    """Generate C2C shipment payload for Ozon (no public API — via mobile app)."""
    deeplink = f"https://www.ozon.ru/my/profile?utm_source=wifiobd&order={order_id}"
    instructions = [
        "Откройте приложение Ozon на смартфоне",
        "Перейдите: Профиль → Мои заказы → Отправить посылку",
        f"Введите данные получателя: {recipient_name}, {recipient_phone}",
        f"Выберите ПВЗ получения: {pvz_code} — {pvz_address}",
        f"Укажите объявленную ценность: {declared_value} руб., вес: {weight_kg} кг"
        + (f", комментарий: {comment}" if comment else ""),
    ]
    return C2CShipmentPayload(
        provider="ozon",
        order_id=order_id,
        recipient_name=recipient_name,
        recipient_phone=recipient_phone,
        pvz_code=pvz_code,
        pvz_address=pvz_address,
        declared_value=declared_value,
        weight_kg=weight_kg,
        comment=comment,
        deeplink=deeplink,
        instructions=instructions,
    )


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
