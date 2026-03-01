<script setup lang="ts">
interface Props {
  modelValue: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'full'
  closeOnOverlay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  closeOnOverlay: true,
  size: 'md'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}>()

const close = () => {
  emit('update:modelValue', false)
  emit('close')
}

// ESC to close
const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && props.modelValue) {
    close()
  }
}

// Focus trap (simplified)
const modalRef = ref<HTMLElement | null>(null)
const firstFocusable = ref<HTMLElement | null>(null)
const lastFocusable = ref<HTMLElement | null>(null)

const updateFocusableElements = () => {
  if (!modalRef.value) return
  const focusable = modalRef.value.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  if (focusable.length > 0) {
    firstFocusable.value = focusable[0] as HTMLElement
    lastFocusable.value = focusable[focusable.length - 1] as HTMLElement
  }
}

const handleTab = (e: KeyboardEvent) => {
  if (e.key !== 'Tab') return
  if (!firstFocusable.value || !lastFocusable.value) return

  if (e.shiftKey) {
    if (document.activeElement === firstFocusable.value) {
      e.preventDefault()
      lastFocusable.value.focus()
    }
  } else {
    if (document.activeElement === lastFocusable.value) {
      e.preventDefault()
      firstFocusable.value.focus()
    }
  }
}

watch(() => props.modelValue, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
    window.addEventListener('keydown', onKeydown)
    nextTick(() => {
      updateFocusableElements()
      firstFocusable.value?.focus()
    })
  } else {
    document.body.style.overflow = ''
    window.removeEventListener('keydown', onKeydown)
  }
}, { immediate: true })

onUnmounted(() => {
  if (import.meta.client) {
    document.body.style.overflow = ''
    window.removeEventListener('keydown', onKeydown)
  }
})
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div 
        v-if="modelValue" 
        class="u-modal-overlay" 
        @mousedown.self="closeOnOverlay && close()"
        @keydown="handleTab"
      >
        <div 
          ref="modalRef"
          class="u-modal-container" 
          :class="`u-modal--${size}`"
          role="dialog" 
          aria-modal="true"
        >
          <header class="u-modal-header">
            <h3 class="u-modal-title">{{ title }}</h3>
            <button 
              class="u-modal-close" 
              aria-label="Закрыть" 
              @click="close"
            >
              <Icon name="ph:x-bold" size="20" />
            </button>
          </header>
          
          <div class="u-modal-content">
            <slot />
          </div>
          
          <footer v-if="$slots.footer" class="u-modal-footer">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.u-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 12000;
  background: var(--color-overlay);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.u-modal-container {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-modal);
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modal-slide-up 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.u-modal--sm { max-width: 400px; }
.u-modal--md { max-width: 600px; }
.u-modal--lg { max-width: 900px; }
.u-modal--full { max-width: 95vw; height: 95vh; }

.u-modal-header {
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--color-border);
}

.u-modal-title {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
}

.u-modal-close {
  background: transparent;
  border: none;
  color: var(--color-text-2);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.u-modal-close:hover {
  background: var(--color-surface-2);
  color: var(--color-accent);
}

.u-modal-content {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.u-modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-2);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Animations */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

@keyframes modal-slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Mobile-first: slide up sheet on small screens */
@media (max-width: 640px) {
  .u-modal-overlay {
    align-items: flex-end;
    padding: 0;
  }
  .u-modal-container {
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    max-height: 85vh;
    animation: modal-slide-up-mobile 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }
}

@keyframes modal-slide-up-mobile {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
</style>
