<script setup lang="ts">
/**
 * UPromptDialog — глобальный компонент диалога ввода текста.
 *
 * Подключается ОДИН РАЗ в app.vue. Управляется через usePrompt().
 *
 * @example в app.vue:
 * <UPromptDialog />
 *
 * @example в компонентах:
 * const { prompt } = usePrompt()
 * const url = await prompt({ title: 'Введите URL', placeholder: 'https://...' })
 * if (url === null) return
 */

import { usePrompt } from '~/composables/usePrompt'

const { state, _resolve } = usePrompt()

/** Локальное значение поля ввода */
const inputValue = ref('')
const inputRef = ref<HTMLInputElement | null>(null)
const dialogRef = ref<HTMLElement | null>(null)

/** Синхронизация с defaultValue при открытии */
watch(
  () => state.value.open,
  (open) => {
    if (!import.meta.client) return
    if (open) {
      inputValue.value = state.value.defaultValue
      document.body.style.overflow = 'hidden'
      window.addEventListener('keydown', onKeydown)
      nextTick(() => {
        inputRef.value?.focus()
        inputRef.value?.select()
      })
    } else {
      document.body.style.overflow = ''
      window.removeEventListener('keydown', onKeydown)
    }
  }
)

const handleConfirm = () => {
  _resolve(inputValue.value)
}

const handleCancel = () => {
  _resolve(null)
}

/** Escape отменяет, Enter подтверждает */
const onKeydown = (e: KeyboardEvent) => {
  if (!state.value.open) return
  if (e.key === 'Escape') handleCancel()
  if (e.key === 'Enter') handleConfirm()
}

/** Focus trap */
const handleTab = (e: KeyboardEvent) => {
  if (e.key !== 'Tab' || !dialogRef.value) return
  const focusable = dialogRef.value.querySelectorAll<HTMLElement>(
    'button, input, [tabindex]:not([tabindex="-1"])'
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

onUnmounted(() => {
  if (import.meta.client) {
    document.body.style.overflow = ''
    window.removeEventListener('keydown', onKeydown)
  }
})
</script>

<template>
  <Teleport to="body">
    <Transition name="prompt-fade">
      <div
        v-if="state.open"
        class="prompt-overlay"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="'prompt-title'"
        data-testid="prompt-dialog"
        @mousedown.self="handleCancel"
        @keydown="handleTab"
      >
        <div ref="dialogRef" class="prompt-container">
          <!-- Header -->
          <div class="prompt-header">
            <h3
              id="prompt-title"
              class="prompt-title"
              data-testid="prompt-dialog-title"
            >
              {{ state.title }}
            </h3>
            <button
              class="prompt-close"
              aria-label="Закрыть"
              @click="handleCancel"
            >
              <Icon name="ph:x-bold" size="18" />
            </button>
          </div>

          <!-- Input -->
          <div class="prompt-body">
            <label v-if="state.label" class="prompt-label" :for="'prompt-input'">
              {{ state.label }}
            </label>
            <input
              id="prompt-input"
              ref="inputRef"
              v-model="inputValue"
              class="prompt-input"
              :type="state.inputType"
              :placeholder="state.placeholder"
              autocomplete="off"
              data-testid="prompt-dialog-input"
            />
          </div>

          <!-- Actions -->
          <div class="prompt-actions">
            <button
              class="prompt-btn prompt-btn--cancel"
              data-testid="prompt-dialog-cancel-btn"
              @click="handleCancel"
            >
              {{ state.cancelLabel }}
            </button>
            <button
              class="prompt-btn prompt-btn--primary"
              data-testid="prompt-dialog-ok-btn"
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
.prompt-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-dialog);
  background: var(--color-overlay);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.prompt-container {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-modal);
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  animation: prompt-slide-up var(--transition-normal) cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

.prompt-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.prompt-title {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
}

.prompt-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--color-text-2);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.prompt-close:hover {
  background: var(--color-surface-2);
  color: var(--color-accent);
}

.prompt-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.prompt-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-2);
}

.prompt-input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  color: var(--color-text);
  font-size: 1rem; /* min 16px — prevents iOS zoom */
  font-family: var(--font-sans);
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast);
  outline: none;
  box-sizing: border-box;
}

.prompt-input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-glow);
}

.prompt-input::placeholder {
  color: var(--color-muted);
}

.prompt-actions {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-2);
  justify-content: flex-end;
}

.prompt-btn {
  padding: 0.625rem 1.25rem;
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

.prompt-btn:hover {
  transform: translateY(-1px);
}

.prompt-btn:active {
  transform: scale(0.97);
}

.prompt-btn--cancel {
  background: var(--color-surface-3);
  color: var(--color-text-2);
  border-color: var(--color-border);
}

.prompt-btn--cancel:hover {
  background: var(--color-surface-3);
  color: var(--color-text);
  border-color: var(--color-border-strong);
}

.prompt-btn--primary {
  background: var(--color-accent);
  color: var(--color-on-accent);
  border-color: var(--color-accent);
}

.prompt-btn--primary:hover {
  background: var(--color-accent-hover);
}

/* Animations */
.prompt-fade-enter-active,
.prompt-fade-leave-active {
  transition: opacity var(--transition-fast);
}

.prompt-fade-enter-from,
.prompt-fade-leave-to {
  opacity: 0;
}

@keyframes prompt-slide-up {
  from {
    transform: translateY(16px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Mobile: sheet from bottom */
@media (max-width: 640px) {
  .prompt-overlay {
    align-items: flex-end;
    padding: 0;
  }

  .prompt-container {
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    max-width: 100%;
    animation: prompt-slide-up-mobile var(--transition-slow) cubic-bezier(0.16, 1, 0.3, 1);
  }
}

@keyframes prompt-slide-up-mobile {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}
</style>
