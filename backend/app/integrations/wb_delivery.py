# Module: integrations/wb_delivery | Agent: backend-agent | Task: p16_backend_c2c_shipment
"""Wildberries C2C delivery via pickup points (no API, static data)."""
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
    """Generate C2C shipment payload for Wildberries (no public API — via mobile app)."""
    deeplink = "https://www.wildberries.ru/lk/track"
    instructions = [
        "Откройте приложение Wildberries на смартфоне",
        "Перейдите в раздел Профиль (иконка справа внизу)",
        "Выберите: Сервисы → WB Track",
        "Нажмите «Отправить посылку»",
        f"Введите данные получателя: {recipient_name}, {recipient_phone}",
        f"Выберите ПВЗ получения: {pvz_code} — {pvz_address}",
        f"Объявите ценность: {declared_value} руб., вес: {weight_kg} кг"
        + (f", комментарий: {comment}" if comment else ""),
    ]
    return C2CShipmentPayload(
        provider="wb",
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


def get_tracking_url(tracking_number: str) -> str:
    """Generate Wildberries tracking URL."""
    return f"https://www.wildberries.ru/lk/myorders/delivery?id={tracking_number}"
