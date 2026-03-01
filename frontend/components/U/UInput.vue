<script setup lang="ts">
interface Props {
  modelValue: string | number
  label?: string
  type?: string
  placeholder?: string
  disabled?: boolean
  error?: string
  name?: string
  id?: string
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  'blur': [Event]
  'focus': [Event]
}>()

const onInput = (e: Event) => {
  emit('update:modelValue', (e.target as HTMLInputElement).value)
}

const inputId = computed(() => props.id || props.name || `input-${Math.random().toString(36).slice(2, 9)}`)
</script>

<template>
  <div 
    class="input-wrapper" 
    :class="{ 
      'input-wrapper--error': error, 
      'input-wrapper--disabled': disabled,
      'input-wrapper--has-icon': icon 
    }"
  >
    <label v-if="label" :for="inputId" class="input-label">{{ label }}</label>
    <div class="input-container">
      <div v-if="icon" class="input-prefix-icon">
        <Icon :name="icon" size="18" />
      </div>
      
      <input
        :id="inputId"
        :name="name"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        class="input-field"
        @input="onInput"
        @blur="emit('blur', $event)"
        @focus="emit('focus', $event)"
      />
      
      <!-- Validation Indicators -->
      <div class="input-status-icons">
        <Transition name="fade">
          <div v-if="error" class="input-status-icon input-status-icon--error" title="Ошибка">
            <Icon name="ph:warning-circle-bold" size="20" />
          </div>
          <div v-else-if="modelValue && !error" class="input-status-icon input-status-icon--success" title="Верно">
            <Icon name="ph:check-circle-bold" size="20" />
          </div>
        </Transition>
      </div>
    </div>
    
    <Transition name="slide-up">
      <span v-if="error" class="input-error-msg">
        <Icon name="ph:warning-bold" size="14" style="margin-right: 4px;" />
        {{ error }}
      </span>
    </Transition>
  </div>
</template>

<style scoped>
.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.input-label {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  font-weight: 600;
  transition: color var(--transition-fast);
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.input-prefix-icon {
  position: absolute;
  left: 14px;
  color: var(--color-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  transition: color var(--transition-fast);
  z-index: 1;
}

.input-field {
  width: 100%;
  min-height: 48px;
  padding: 12px 16px;
  padding-right: 44px;
  font-size: 16px;
  font-family: var(--font-sans);
  color: var(--color-text);
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    background-color var(--transition-theme),
    color var(--transition-theme);
  outline: none;
}

.input-wrapper--has-icon .input-field {
  padding-left: 44px;
}

.input-field::placeholder { color: var(--color-muted); }

.input-field:focus {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
  background-color: var(--color-surface-3);
}

.input-field:focus ~ .input-prefix-icon {
  color: var(--color-accent);
}

.input-wrapper:focus-within .input-label {
  color: var(--color-accent);
}

.input-wrapper--disabled .input-field {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: var(--color-surface-3);
}

.input-wrapper--error .input-field {
  border-color: var(--color-error);
}

.input-wrapper--error .input-field:focus {
  box-shadow: 0 0 0 4px var(--color-error-bg);
}

.input-status-icons {
  position: absolute;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  pointer-events: none;
}

.input-status-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-status-icon--error { color: var(--color-error); }
.input-status-icon--success { color: var(--color-success); }

.input-error-msg {
  font-size: var(--text-xs);
  color: var(--color-error);
  font-weight: 500;
  display: flex;
  align-items: center;
  margin-top: 2px;
}

/* Animations */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-up-enter-active, .slide-up-leave-active { transition: all 0.2s ease-out; }
.slide-up-enter-from { opacity: 0; transform: translateY(-4px); }
.slide-up-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
