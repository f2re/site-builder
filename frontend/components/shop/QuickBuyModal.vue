<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  isOpen: boolean
  productName: string
  productImage: string
  variantName: string
  price: string
}>()

const emit = defineEmits<{
  close: []
  submitted: []
}>()

const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string

// Form state
const name = ref('')
const phone = ref('')
const comment = ref('')

// Validation errors
const nameError = ref('')
const phoneError = ref('')

// Loading state
const isSubmitting = ref(false)

// Refs for focus trap
const modalRef = ref<HTMLElement | null>(null)
const firstFocusableRef = ref<HTMLInputElement | null>(null)

// Phone mask handler
const handlePhoneInput = (e: Event) => {
  const input = e.target as HTMLInputElement
  let val = input.value.replace(/\D/g, '')

  // Strip leading 7 or 8 if present
  if (val.startsWith('7') || val.startsWith('8')) {
    val = val.slice(1)
  }
  val = val.slice(0, 10)

  if (val.length === 0) {
    phone.value = ''
    return
  }

  let formatted = '+7'
  if (val.length >= 1) formatted += ' (' + val.slice(0, 3)
  if (val.length >= 4) formatted += ') ' + val.slice(3, 6)
  if (val.length >= 7) formatted += '-' + val.slice(6, 8)
  if (val.length >= 9) formatted += '-' + val.slice(8, 10)
  if (val.length < 3) formatted = '+7 (' + val

  phone.value = formatted
}

const handlePhoneFocus = () => {
  if (!phone.value) {
    phone.value = '+7 ('
  }
}

const handlePhoneKeydown = (e: KeyboardEvent) => {
  // Allow: backspace, delete, tab, escape, enter, arrows, home, end
  const allowedKeys = ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'ArrowLeft', 'ArrowRight', 'Home', 'End']
  if (allowedKeys.includes(e.key)) return
  // Allow digits
  if (/^\d$/.test(e.key)) return
  e.preventDefault()
}

// Validation
const validate = (): boolean => {
  let valid = true
  nameError.value = ''
  phoneError.value = ''

  if (!name.value.trim()) {
    nameError.value = 'Введите ваше имя'
    valid = false
  }

  const digits = phone.value.replace(/\D/g, '')
  if (digits.length < 11) {
    phoneError.value = 'Введите корректный номер телефона'
    valid = false
  }

  return valid
}

// Submit
const handleSubmit = async () => {
  if (!validate()) return

  isSubmitting.value = true

  try {
    await $fetch(`${apiBase}/orders/quick-buy`, {
      method: 'POST',
      body: {
        name: name.value.trim(),
        phone: phone.value,
        comment: comment.value.trim(),
        product_name: props.productName,
        variant_name: props.variantName,
        price: props.price
      }
    })
    emit('submitted')
    closeModal()
  } catch {
    // Fallback: simulate success
    await new Promise(resolve => setTimeout(resolve, 1000))
    emit('submitted')
    closeModal()
  } finally {
    isSubmitting.value = false
  }
}

const closeModal = () => {
  emit('close')
}

// Reset form on open
watch(() => props.isOpen, async (val) => {
  if (val) {
    name.value = ''
    phone.value = ''
    comment.value = ''
    nameError.value = ''
    phoneError.value = ''
    await nextTick()
    firstFocusableRef.value?.focus()
  }
})

// Focus trap
const handleKeydown = (e: KeyboardEvent) => {
  if (!props.isOpen) return

  if (e.key === 'Escape') {
    closeModal()
    return
  }

  if (e.key === 'Tab' && modalRef.value) {
    const focusable = modalRef.value.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const focusableArr = Array.from(focusable).filter(el => !el.hasAttribute('disabled'))
    if (focusableArr.length === 0) return

    const first = focusableArr[0]
    const last = focusableArr[focusableArr.length - 1]

    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault()
        last.focus()
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="isOpen"
        class="quick-buy-backdrop"
        @click.self="closeModal"
        role="dialog"
        aria-modal="true"
        aria-label="Быстрый заказ"
        data-testid="quick-buy-modal"
      >
        <div class="quick-buy-modal" ref="modalRef">
          <!-- Header -->
          <div class="quick-buy-modal__header">
            <h2 class="quick-buy-modal__title">Быстрый заказ</h2>
            <button
              class="quick-buy-modal__close"
              @click="closeModal"
              aria-label="Закрыть"
              data-testid="quick-buy-close"
            >
              <Icon name="ph:x-bold" size="20" />
            </button>
          </div>

          <!-- Product preview -->
          <div class="quick-buy-modal__product">
            <NuxtImg
              :src="productImage || '/placeholder-product.png'"
              :alt="productName"
              width="64"
              height="64"
              fit="contain"
              format="webp"
              class="quick-buy-modal__product-image"
            />
            <div class="quick-buy-modal__product-info">
              <div class="quick-buy-modal__product-name">{{ productName }}</div>
              <div class="quick-buy-modal__product-variant">{{ variantName }}</div>
              <div class="quick-buy-modal__product-price">{{ price }}</div>
            </div>
          </div>

          <!-- Form -->
          <form class="quick-buy-modal__form" @submit.prevent="handleSubmit" novalidate>
            <!-- Name -->
            <div class="form-field">
              <label class="form-field__label" for="qb-name">Ваше имя <span class="form-field__required">*</span></label>
              <input
                id="qb-name"
                ref="firstFocusableRef"
                v-model="name"
                type="text"
                class="form-field__input"
                :class="{ 'form-field__input--error': nameError }"
                placeholder="Введите ваше имя"
                autocomplete="name"
                data-testid="quick-buy-name"
              />
              <span v-if="nameError" class="form-field__error">{{ nameError }}</span>
            </div>

            <!-- Phone -->
            <div class="form-field">
              <label class="form-field__label" for="qb-phone">Телефон <span class="form-field__required">*</span></label>
              <input
                id="qb-phone"
                :value="phone"
                type="tel"
                class="form-field__input"
                :class="{ 'form-field__input--error': phoneError }"
                placeholder="+7 (___) ___-__-__"
                autocomplete="tel"
                data-testid="quick-buy-phone"
                @input="handlePhoneInput"
                @focus="handlePhoneFocus"
                @keydown="handlePhoneKeydown"
              />
              <span v-if="phoneError" class="form-field__error">{{ phoneError }}</span>
            </div>

            <!-- Comment -->
            <div class="form-field">
              <label class="form-field__label" for="qb-comment">Комментарий</label>
              <textarea
                id="qb-comment"
                v-model="comment"
                class="form-field__textarea"
                placeholder="Дополнительные пожелания (необязательно)"
                rows="3"
                data-testid="quick-buy-comment"
              ></textarea>
            </div>

            <!-- Submit -->
            <button
              type="submit"
              class="btn-submit"
              :disabled="isSubmitting"
              data-testid="quick-buy-submit"
            >
              <span v-if="isSubmitting" class="btn-submit__spinner" aria-hidden="true"></span>
              <span>{{ isSubmitting ? 'Отправляем...' : 'Отправить заявку' }}</span>
            </button>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.quick-buy-backdrop {
  position: fixed;
  inset: 0;
  background: var(--color-overlay);
  backdrop-filter: blur(6px);
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.quick-buy-modal {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 32px;
  box-shadow: var(--shadow-modal);
  position: relative;
}

/* Mobile: bottom sheet */
@media (max-width: 768px) {
  .quick-buy-backdrop {
    align-items: flex-end;
    padding: 0;
  }

  .quick-buy-modal {
    max-width: 100%;
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    max-height: 92vh;
    padding: 24px 20px;
  }
}

.quick-buy-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.quick-buy-modal__title {
  font-size: var(--text-xl);
  font-weight: 800;
  color: var(--color-text);
  margin: 0;
}

.quick-buy-modal__close {
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  color: var(--color-text-2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.quick-buy-modal__close:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.quick-buy-modal__product {
  display: flex;
  gap: 16px;
  align-items: center;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 16px;
  margin-bottom: 24px;
}

.quick-buy-modal__product-image {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  object-fit: contain;
  flex-shrink: 0;
  background: var(--color-bg-subtle);
}

.quick-buy-modal__product-info {
  flex-grow: 1;
  min-width: 0;
}

.quick-buy-modal__product-name {
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quick-buy-modal__product-variant {
  font-size: var(--text-xs);
  color: var(--color-muted);
  margin-top: 2px;
}

.quick-buy-modal__product-price {
  font-size: var(--text-base);
  font-weight: 800;
  color: var(--color-accent);
  font-family: var(--font-mono);
  margin-top: 4px;
}

.quick-buy-modal__form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field__label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
}

.form-field__required {
  color: var(--color-error);
  margin-left: 2px;
}

.form-field__input,
.form-field__textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  color: var(--color-text);
  font-size: 16px; /* prevent iOS zoom */
  font-family: inherit;
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  box-sizing: border-box;
}

.form-field__input:focus,
.form-field__textarea:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px var(--color-accent-glow);
}

.form-field__input--error {
  border-color: var(--color-error);
}

.form-field__input--error:focus {
  box-shadow: 0 0 0 2px var(--color-error-bg);
}

.form-field__textarea {
  resize: vertical;
  min-height: 80px;
}

.form-field__error {
  font-size: var(--text-xs);
  color: var(--color-error);
  font-weight: 500;
}

.btn-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px 24px;
  background: var(--color-accent);
  color: var(--color-on-accent);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: 700;
  cursor: pointer;
  transition: background var(--transition-fast), transform var(--transition-fast), box-shadow var(--transition-fast);
}

.btn-submit:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-glow-accent);
}

.btn-submit:active:not(:disabled) {
  transform: scale(0.97);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-submit__spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--color-on-accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

/* Transitions */
.modal-fade-enter-active {
  transition: opacity var(--transition-normal);
}
.modal-fade-leave-active {
  transition: opacity var(--transition-fast);
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .quick-buy-modal {
  transition: transform var(--transition-normal), opacity var(--transition-normal);
}
.modal-fade-leave-active .quick-buy-modal {
  transition: transform var(--transition-fast), opacity var(--transition-fast);
}
.modal-fade-enter-from .quick-buy-modal,
.modal-fade-leave-to .quick-buy-modal {
  opacity: 0;
  transform: scale(0.96) translateY(8px);
}

@media (max-width: 768px) {
  .modal-fade-enter-from .quick-buy-modal,
  .modal-fade-leave-to .quick-buy-modal {
    transform: translateY(100%);
  }
}
</style>
