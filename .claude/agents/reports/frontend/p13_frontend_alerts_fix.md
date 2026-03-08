## Status: DONE

## Задача
Заменить все нативные `alert()`, `confirm()`, `prompt()` в frontend/ на UI-компоненты дизайн-системы проекта (Race-Style UI).

## Найдено и исправлено
Всего: 19 вхождений в 10 файлах.

### Типы замен
- 7 × `alert()` → `useToast()` (warning/error)
- 8 × `confirm()` → `useConfirm()` с await
- 4 × `prompt()` / `window.prompt()` → `usePrompt()` с await

## Созданные артефакты

### Новые файлы
- `frontend/composables/useConfirm.ts` — Promise-based singleton composable для confirm диалогов. Поддерживает variants: danger/warning/default.
- `frontend/composables/usePrompt.ts` — Promise-based singleton composable для prompt диалогов ввода текста.
- `frontend/components/U/UConfirmDialog.vue` — Глобальный компонент диалога подтверждения. Teleport to body. Иконки по variant. Focus trap. Escape/click-outside закрывает. Анимации confirm-fade + slide-up. Mobile sheet.
- `frontend/components/U/UPromptDialog.vue` — Глобальный компонент диалога ввода текста. Autofocus + select на открытии. Enter подтверждает, Escape отменяет. Progress bar.
- `frontend/components/U/UToast.vue` — Глобальный компонент стека toast-уведомлений. TransitionGroup. Прогресс-бар. Slide справа (desktop) / снизу (mobile). Максимум 3 toast.

### Изменённые файлы
- `frontend/app.vue` — добавлены `<UToast />`, `<UConfirmDialog />`, `<UPromptDialog />` как глобальные синглтоны
- `frontend/components/admin/BlogEditor.vue` — 3 alert → toast, 1 prompt → usePrompt
- `frontend/components/blog/TipTapEditor.vue` — 1 alert → toast, 2 window.prompt → usePrompt (async)
- `frontend/components/U/URichEditor.vue` — 3 alert → toast, 1 prompt → usePrompt
- `frontend/pages/profile/addresses.vue` — confirm → useConfirm
- `frontend/pages/admin/blog/index.vue` — confirm → useConfirm
- `frontend/pages/profile/orders/[id].vue` — confirm → useConfirm
- `frontend/pages/admin/migration.vue` — confirm → useConfirm
- `frontend/pages/admin/pages/index.vue` — confirm → useConfirm
- `frontend/pages/admin/products/categories.vue` — confirm → useConfirm
- `frontend/pages/admin/products/index.vue` — confirm → useConfirm
- `frontend/pages/admin/products/[id].vue` — confirm → useConfirm
- `frontend/pages/admin/firmware/index.vue` — confirm → useConfirm

## Contracts Verified
- Нет ни одного нативного alert(/confirm(/prompt( в исходниках: ✅
- Только var(--color-*) токены — никаких hex/rgb: ✅
- data-testid на всех интерактивных элементах: ✅ (confirm-dialog, confirm-dialog-title, confirm-dialog-message, confirm-dialog-cancel-btn, confirm-dialog-confirm-btn, prompt-dialog, prompt-dialog-title, prompt-dialog-input, prompt-dialog-cancel-btn, prompt-dialog-ok-btn, toast-container, toast-item, toast-close-btn)
- Mobile-first breakpoints (max-width: 640px sheet from bottom): ✅
- Поддержка тёмной и светлой темы (все var(--color-*) автоматически переключаются): ✅
- Accessibility: focus trap, aria-label, role="dialog", aria-modal="true", Escape закрывает: ✅
- Touch targets ≥ 44px: ✅
- Анимации согласно Animation Contract (fade, slide-up, mobile sheet): ✅

## Accessibility
- UConfirmDialog: role="dialog", aria-modal="true", aria-labelledby, focus trap, Escape, click-outside
- UPromptDialog: role="dialog", aria-modal="true", aria-labelledby, focus trap, Escape, Enter
- UToast: role="status", aria-live="polite", role="alert" на каждом toast
- Все кнопки закрытия: aria-label="Закрыть"

## API useConfirm
```ts
const { confirm } = useConfirm()
const ok = await confirm({
  title: 'Удалить товар?',
  message: 'Это действие нельзя отменить.',
  confirmLabel: 'Удалить',
  cancelLabel: 'Отмена',
  variant: 'danger', // 'danger' | 'warning' | 'default'
})
if (!ok) return
```

## API usePrompt
```ts
const { prompt } = usePrompt()
const url = await prompt({
  title: 'Вставить ссылку',
  label: 'URL',
  placeholder: 'https://...',
  defaultValue: previousUrl,
  inputType: 'url',
})
if (url === null) return // отменено
```

## Blockers
- none
