## Status: DONE

## Completed:
- Добавлен `@dataclass C2CShipmentPayload` и `generate_c2c_payload()` в `backend/app/integrations/ozon_delivery.py`
- Добавлен `@dataclass C2CShipmentPayload` и `generate_c2c_payload()` в `backend/app/integrations/wb_delivery.py`
- Добавлена Pydantic-схема `C2CShipmentResponse` в `backend/app/api/v1/delivery/schemas.py`
- Добавлен endpoint `GET /api/v1/delivery/orders/{order_id}/c2c-shipment` в `backend/app/api/v1/delivery/router.py`
- Обновлён API-контракт в `.claude/agents/contracts/api_contracts.md`

## Artifacts:
- `backend/app/integrations/ozon_delivery.py` — C2CShipmentPayload dataclass + generate_c2c_payload (5-шаговая инструкция, deeplink https://www.ozon.ru/my/profile?utm_source=wifiobd&order={order_id})
- `backend/app/integrations/wb_delivery.py` — C2CShipmentPayload dataclass + generate_c2c_payload (7-шаговая инструкция через Профиль → Сервисы → WB Track, deeplink https://www.wildberries.ru/lk/track)
- `backend/app/api/v1/delivery/schemas.py` — добавлена C2CShipmentResponse
- `backend/app/api/v1/delivery/router.py` — новый endpoint с require_admin, 404/400 guards
- `.claude/agents/contracts/api_contracts.md` — секция GET /api/v1/delivery/orders/{order_id}/c2c-shipment

## Implementation Notes:
- Существующий код PickupPoint / OZON_PICKUP_POINTS / WB_PICKUP_POINTS / get_pickup_points / get_tracking_url не тронут
- Тип `payload` в router.py аннотирован как `OzonC2CPayload | WbC2CPayload` для корректного прохождения mypy (два разных класса с идентичной структурой)
- Данные получателя извлекаются из `order.user.name` / `order.user.phone` (lazy selectin уже настроен в OrderRepository.get_by_id)
- pvz_code = `order.tracking_number or "Не выбран"`, pvz_address = `order.shipping_address or "Не указан"`
- declared_value = `order.total_amount`

## Contracts Verified:
- Pydantic schemas: OK (model_config = ConfigDict(from_attributes=True))
- DI via Depends: OK (require_admin, get_db)
- No Any in type hints: OK
- ruff: 0 errors
- mypy: 0 issues
- pytest tests/unit/: 24 passed

## Next:
- frontend-agent: endpoint GET /api/v1/delivery/orders/{order_id}/c2c-shipment готов к интеграции (контракт в api_contracts.md)

## Blockers:
- none
