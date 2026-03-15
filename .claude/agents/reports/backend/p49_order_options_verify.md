## Status: DONE
## Completed:
- Verified OrderItem.selected_options column exists in model (JSON/JSONB, server_default="[]")
- Verified order creation copies selected_options from cart items (service.py line 81)
- Verified cart price calculation includes option price_modifier (cart/service.py lines 70-72)
- Verified OrderItemRead schema includes selected_options: List[dict] = []
- Verified admin GET /orders/{id} returns options via selectinload chain in repository
- Fixed: email notification now includes order items with selected options and price modifiers
- Updated order_created.html template to display items table with options

## Analysis:
### What was already working:
1. OrderItem.selected_options -- column exists, correct type (JSON/JSONB)
2. Order creation -- copies selected_options from cart item via item.get("selected_options", [])
3. Price -- cart calculates item_price = variant.price + sum(modifiers), order stores this in OrderItem.price
4. total_amount -- uses cart subtotal_rub which already includes option modifiers
5. OrderItemRead schema -- already has selected_options: List[dict] = []
6. Admin API -- repo.get_by_id() uses selectinload for items, OrderRead includes OrderItemRead with options

### What was missing (fixed):
1. Email context -- send_email_task did NOT pass order items to template
2. Email template -- order_created.html did NOT display items or their options

## Artifacts:
- backend/app/api/v1/orders/service.py (updated email context with items and options)
- backend/app/templates/email/order_created.html (updated with items table and options display)

## Contracts Verified:
- Pydantic schemas: OK (OrderItemRead.selected_options exists)
- DI via Depends: OK
- ruff: OK
- mypy: OK

## Next:
- Frontend can rely on OrderItemRead.selected_options being populated in all order responses
- Email notifications now include full item breakdown with option names and price modifiers

## Blockers:
- none
