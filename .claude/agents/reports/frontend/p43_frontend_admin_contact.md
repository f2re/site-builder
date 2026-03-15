## Status: DONE

## Completed:
- Added "Обратная связь" and "Настройки связи" nav items to admin layout
- Created composable `useAdminContact.ts` with all API functions
- Created page `/admin/contact` — list with status filter, cursor pagination, skeleton loader
- Created page `/admin/contact/[id]` — detail view with reply/delete actions
- Created page `/admin/settings/contact` — email field + URichEditor for page text

## Artifacts:
- frontend/layouts/admin.vue (added 2 nav items)
- frontend/composables/useAdminContact.ts
- frontend/pages/admin/contact/index.vue
- frontend/pages/admin/contact/[id].vue
- frontend/pages/admin/settings/contact.vue

## Contracts Verified:
- API shape matches api_contracts.md: OK
  - GET /admin/contact → ContactListResponse { items, total, next_cursor }
  - GET /admin/contact/{id} → ContactMessage (auto-marks READ)
  - PUT /admin/contact/{id}/reply → body { status: 'REPLIED' }
  - DELETE /admin/contact/{id} → 204
  - GET /admin/settings/contact → ContactSettings
  - PUT /admin/settings/contact → ContactSettings
- data-testid on all interactive elements: OK
  - admin-contact-table, admin-contact-row, admin-contact-status-filter
  - admin-contact-load-more-btn, contact-open-btn
  - admin-contact-detail, contact-sender-info, contact-message-body
  - contact-status-badge, contact-back-btn
  - admin-contact-reply-btn, admin-contact-delete-btn
  - settings-contact-form, admin-settings-contact-email
  - settings-contact-page-text-editor, admin-settings-contact-save-btn
- Only var(--color-*) tokens used: OK
- Mobile-first breakpoints: OK
- npm run lint: OK (0 errors)
- npm run typecheck: OK (0 errors)

## Accessibility:
- aria-label on icon-only buttons
- role table with aria-label
- Keyboard-accessible filter select

## Next:
- testing-agent: e2e tests for /admin/contact, /admin/contact/[id], /admin/settings/contact

## Blockers:
- none
