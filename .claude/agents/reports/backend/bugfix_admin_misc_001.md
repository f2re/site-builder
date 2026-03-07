## Status: DONE

## Completed:
- BUG-ADM-BE-01: GET /blog/posts/{slug} теперь принимает `current_user: Optional[User] = Depends(get_optional_current_user)`, вычисляет `is_admin` и передаёт в `service.get_post_detail`. В сервисе добавлена проверка: если пост в статусе DRAFT или ARCHIVED и пользователь не admin — возвращается HTTPException(404).
- BUG-ADM-BE-02: В `list_products` добавлен `outerjoin(Category, Product.category_id == Category.id)` и `Category.name.label("category_name")` в SELECT. В результирующий dict добавлен ключ `category_name`. В `ProductShortRead` добавлено поле `category_name: Optional[str] = None`.
- BUG-ADM-BE-03: Изменена логика формирования `price_display`: если цена целая — выводится без копеек (`str(int(price))`), иначе с точностью до 2 знаков, при отсутствии цены — "0".

## Artifacts:
- backend/app/api/v1/blog/router.py
- backend/app/api/v1/blog/service.py
- backend/app/api/v1/products/repository.py
- backend/app/api/v1/products/schemas.py

## Contracts Verified:
- Pydantic schemas: OK
- DI via Depends: OK
- ruff: OK
- mypy: OK

## Next:
- none

## Blockers:
- none
