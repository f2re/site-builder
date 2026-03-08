## Status: DONE

## Completed:
- Added `UserAdminUpdate` and `UserAddress` interfaces to `useUser.ts`
- Added `adminUpdateUser`, `adminGetUserAddresses`, `adminDeleteUserAddress`, `adminUpdateUserAddress` methods to `useUser.ts`
- Created `frontend/components/admin/UserAddressesList.vue` — component for displaying and deleting user addresses
- Updated `frontend/pages/admin/users/index.vue`:
  - Added "Изменить" button (edit-user-btn) in each table row alongside block/unblock button
  - Added edit modal with pre-filled fields: full_name, email, phone, role, is_active
  - Added `openEditModal()`, `handleUpdateUser()` handlers
  - Added `UserAddressesList` component inside edit modal
  - Added all required CSS styles using only var(--color-*) tokens

## Artifacts:
- `frontend/composables/useUser.ts` — added 4 new admin methods and 2 new interfaces
- `frontend/components/admin/UserAddressesList.vue` — new component
- `frontend/pages/admin/users/index.vue` — added edit button, edit modal, CSS

## Contracts Verified:
- API shape matches api_contracts.md:
  - `PATCH /admin/users/{user_id}` — used in `adminUpdateUser`
  - `GET /admin/users/{user_id}/addresses` — used in `adminGetUserAddresses`
  - `DELETE /admin/users/{user_id}/addresses/{addr_id}` — used in `adminDeleteUserAddress`
- data-testid on all interactive elements: OK
  - `edit-user-btn` — редактировать кнопка в строке
  - `edit-user-modal` — модальное окно
  - `edit-name-input`, `edit-email-input`, `edit-phone-input` — поля ввода
  - `edit-role-select` — выпадающий список роли
  - `edit-active-toggle` — чекбокс активности
  - `edit-submit-btn`, `edit-cancel-btn` — кнопки формы
  - `user-addresses-section` — секция адресов
  - `address-item`, `delete-address-btn` — элементы списка адресов
- Only var(--color-*) tokens used: OK
- Mobile-first: OK (actions-group flex, responsive column widths)
- npm run lint: not executable (Bash permission denied)
- npm run type-check: not executable (Bash permission denied)

## Accessibility:
- aria-label on all icon-only buttons
- label[for] linked to toggle-checkbox via id
- Confirm dialog before address deletion

## Next:
- testing-agent: e2e tests for edit user modal, address deletion flow

## Blockers:
- none
