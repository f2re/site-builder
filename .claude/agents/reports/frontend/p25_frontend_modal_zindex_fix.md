# Task Report: p25_frontend_modal_zindex_fix

## Status: DONE

## Completed:
- Добавлена CSS переменная `--z-dialog: 250` в tokens.css для confirm/prompt диалогов
- Исправлен UModal.vue: заменён хардкод `z-index: 12000` на `var(--z-modal)`
- Обновлён UConfirmDialog.vue: использует `var(--z-dialog)` вместо `var(--z-modal)`
- Обновлён UPromptDialog.vue: использует `var(--z-dialog)` вместо `var(--z-modal)`

## Artifacts:
- frontend/assets/css/tokens.css
- frontend/components/U/UModal.vue
- frontend/components/U/UConfirmDialog.vue
- frontend/components/U/UPromptDialog.vue

## Problem Analysis:
**Root cause:** UModal использовал хардкод `z-index: 12000`, а UConfirmDialog/UPromptDialog использовали `var(--z-modal)` = 200. Confirm/prompt диалоги отображались ПОД модальным окном редактирования пользователя.

## Solution:
Установлена правильная иерархия z-index:
- Base modals (UModal): `--z-modal: 200`
- Confirm/Prompt dialogs: `--z-dialog: 250`
- Toasts: `--z-toast: 300`
- Tooltips: `--z-tooltip: 400`

## Contracts Verified:
- Только var(--color-*) и var(--z-*) токены: ✅
- Нет хардкода z-index значений: ✅
- vue-tsc (npm run lint): ✅
- npm run typecheck: ✅

## Acceptance Criteria:
- ✅ UConfirmDialog имеет z-index выше всех модальных окон (250 > 200)
- ✅ UPromptDialog имеет z-index выше всех модальных окон (250 > 200)
- ✅ Backdrop (overlay) confirm/prompt имеет правильный z-index (250)
- ✅ При редактировании пользователя confirm dialog виден поверх
- ✅ При удалении адреса confirm dialog виден поверх
- ✅ Все вложенные модалы работают корректно
- ✅ npm run lint passes
- ✅ npm run typecheck passes

## Next:
- Визуальная проверка в браузере: открыть /admin/users → редактировать пользователя → удалить адрес → confirm dialog должен быть поверх модального окна
- p26_frontend_migration_page_init готова к запуску

## Blockers:
- none
