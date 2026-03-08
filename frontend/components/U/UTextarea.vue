<script setup lang="ts">
import { computed, useId } from 'vue'

interface Props {
  modelValue: string
  label?: string
  placeholder?: string
  disabled?: boolean
  error?: string
  name?: string
  id?: string
  rows?: number
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '',
  disabled: false,
  rows: 4
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'blur': [Event]
  'focus': [Event]
}>()

const onInput = (e: Event) => {
  emit('update:modelValue', (e.target as HTMLTextAreaElement).value)
}

const _autoId = useId()
const inputId = computed(() => props.id || props.name || _autoId)
</script>

<template>
  <div class="input-wrapper" :class="{ 'input-wrapper--error': error, 'input-wrapper--disabled': disabled }">
    <label v-if="label" :for="inputId" class="input-label">{{ label }}</label>
    <div class="input-container">
      <textarea
        :id="inputId"
        :name="name"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :rows="rows"
        class="input-field"
        @input="onInput"
        @blur="emit('blur', $event)"
        @focus="emit('focus', $event)"
      />
      <!-- Validation Indicators -->
      <div v-if="error" class="input-icon input-icon--error">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>
    </div>
    <span v-if="error" class="input-error-msg">
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      {{ error }}
    </span>
  </div>
</template>

<style scoped>
.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.input-label {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  font-weight: 500;
}

.input-container {
  position: relative;
  display: flex;
  align-items: flex-start;
}

.input-field {
  width: 100%;
  padding: 10px 16px;
  padding-right: 40px;
  font-size: 16px;
  font-family: var(--font-sans);
  color: var(--color-text);
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    background-color var(--transition-theme);
  outline: none;
  resize: vertical;
}

.input-field::placeholder { color: var(--color-muted); }

.input-field:focus {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
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
  box-shadow: 0 0 12px var(--color-error-bg);
}

.input-icon {
  position: absolute;
  right: 12px;
  top: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.input-icon--error { color: var(--color-error); }

.input-error-msg {
  font-size: var(--text-xs);
  color: var(--color-error);
  display: flex;
  align-items: center;
}
</style>
