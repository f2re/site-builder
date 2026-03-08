<script setup lang="ts">
/**
 * UConfirmDialog — глобальный компонент диалога подтверждения.
 *
 * Подключается ОДИН РАЗ в app.vue. Управляется через useConfirm().
 *
 * @example в app.vue:
 * <UConfirmDialog />
 *
 * @example в компонентах:
 * const { confirm } = useConfirm()
 * if (!await confirm({ title: 'Удалить?', variant: 'danger' })) return
 */

import { useConfirm } from '~/composables/useConfirm'

const { state, _resolve } = useConfirm()

/** Иконка по типу диалога */
const iconName = computed(() => {
  if (state.value.variant === 'danger') return 'ph:warning-circle-bold'
  if (state.value.variant === 'warning') return 'ph:warning-bold'
  return 'ph:question-bold'
})

/** Цвет иконки по типу диалога */
const iconColor = computed(() => {
  if (state.value.variant === 'danger') return 'var(--color-error)'
  if (state.value.variant === 'warning') return 'var(--color-warning)'
  return 'var(--color-info)'
})

const handleConfirm = () => _resolve(true)
const handleCancel = () => _resolve(false)

/** Закрытие по Escape */
const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && state.value.open) {
    handleCancel()
  }
}

/** Focus trap: кнопки диалога */
const dialogRef = ref<HTMLElement | null>(null)

const handleTab = (e: KeyboardEvent) => {
  if (e.key !== 'Tab' || !dialogRef.value) return
  const focusable = dialogRef.value.querySelectorAll<HTMLElement>(
    'button, [href], input, [tabindex]:not([tabindex="-1"])'
  )
  if (focusable.length < 2) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (e.shiftKey && document.activeElement === first) {
    e.preventDefault()
    last.focus()
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault()
    first.focus()
  }
}

watch(
  () => state.value.open,
  (open) => {
    if (!import.meta.client) return
    if (open) {
      document.body.style.overflow = 'hidden'
      window.addEventListener('keydown', onKeydown)
      nextTick(() => {
        const cancelBtn = dialogRef.value?.querySelector<HTMLElement>('[data-testid="confirm-dialog-cancel-btn"]')
        cancelBtn?.focus()
      })
    } else {
      document.body.style.overflow = ''
      window.removeEventListener('keydown', onKeydown)
    }
  }
)

onUnmounted(() => {
  if (import.meta.client) {
    document.body.style.overflow = ''
    window.removeEventListener('keydown', onKeydown)
  }
})
</script>

<template>
  <Teleport to="body">
    <Transition name="confirm-fade">
      <div
        v-if="state.open"
        class="confirm-overlay"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="'confirm-title'"
        :aria-describedby="state.message ? 'confirm-message' : undefined"
        data-testid="confirm-dialog"
        @mousedown.self="handleCancel"
        @keydown="handleTab"
      >
        <div ref="dialogRef" class="confirm-container">
          <!-- Icon -->
          <div class="confirm-icon" :style="{ color: iconColor }">
            <Icon :name="iconName" size="32" />
          </div>

          <!-- Content -->
          <div class="confirm-content">
            <h3
              id="confirm-title"
              class="confirm-title"
              data-testid="confirm-dialog-title"
            >
              {{ state.title }}
            </h3>
            <p
              v-if="state.message"
              id="confirm-message"
              class="confirm-message"
              data-testid="confirm-dialog-message"
            >
              {{ state.message }}
            </p>
          </div>

          <!-- Actions -->
          <div class="confirm-actions">
            <button
              class="confirm-btn confirm-btn--cancel"
              data-testid="confirm-dialog-cancel-btn"
              @click="handleCancel"
            >
              {{ state.cancelLabel }}
            </button>
            <button
              class="confirm-btn"
              :class="{
                'confirm-btn--danger': state.variant === 'danger',
                'confirm-btn--warning': state.variant === 'warning',
                'confirm-btn--primary': state.variant === 'default',
              }"
              data-testid="confirm-dialog-confirm-btn"
              @click="handleConfirm"
            >
              {{ state.confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  background: var(--color-overlay);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.confirm-container {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-modal);
  width: 100%;
  max-width: 420px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
  animation: confirm-slide-up var(--transition-normal) cubic-bezier(0.16, 1, 0.3, 1);
}

.confirm-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: var(--radius-full);
  background: var(--color-surface-2);
  flex-shrink: 0;
}

.confirm-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.confirm-title {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.3;
}

.confirm-message {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--color-text-2);
  line-height: 1.5;
}

.confirm-actions {
  display: flex;
  gap: 0.75rem;
  width: 100%;
  margin-top: 0.5rem;
}

.confirm-btn {
  flex: 1;
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition:
    background var(--transition-fast),
    color var(--transition-fast),
    border-color var(--transition-fast),
    transform var(--transition-fast);
  min-height: 44px;
}

.confirm-btn:hover {
  transform: translateY(-1px);
}

.confirm-btn:active {
  transform: scale(0.97);
}

.confirm-btn--cancel {
  background: var(--color-surface-2);
  color: var(--color-text-2);
  border-color: var(--color-border);
}

.confirm-btn--cancel:hover {
  background: var(--color-surface-3);
  color: var(--color-text);
  border-color: var(--color-border-strong);
}

.confirm-btn--danger {
  background: var(--color-error);
  color: #ffffff;
  border-color: var(--color-error);
}

.confirm-btn--danger:hover {
  opacity: 0.9;
}

.confirm-btn--warning {
  background: var(--color-warning);
  color: #ffffff;
  border-color: var(--color-warning);
}

.confirm-btn--warning:hover {
  opacity: 0.9;
}

.confirm-btn--primary {
  background: var(--color-accent);
  color: var(--color-on-accent);
  border-color: var(--color-accent);
}

.confirm-btn--primary:hover {
  background: var(--color-accent-hover);
}

/* Animations */
.confirm-fade-enter-active,
.confirm-fade-leave-active {
  transition: opacity var(--transition-fast);
}

.confirm-fade-enter-from,
.confirm-fade-leave-to {
  opacity: 0;
}

@keyframes confirm-slide-up {
  from {
    transform: translateY(16px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Mobile: slide up from bottom */
@media (max-width: 640px) {
  .confirm-overlay {
    align-items: flex-end;
    padding: 0;
  }

  .confirm-container {
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    max-width: 100%;
    padding: 1.5rem 1.5rem 2rem;
    animation: confirm-slide-up-mobile var(--transition-slow) cubic-bezier(0.16, 1, 0.3, 1);
  }
}

@keyframes confirm-slide-up-mobile {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}
</style>
