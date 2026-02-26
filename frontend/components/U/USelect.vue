<script setup lang="ts">
interface Option {
  label: string
  value: string | number
}

interface Props {
  modelValue: string | number | undefined
  options: Option[]
  label?: string
  placeholder?: string
  disabled?: boolean
  error?: string
  name?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Выберите...',
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
}>()

const onChange = (e: Event) => {
  emit('update:modelValue', (e.target as HTMLSelectElement).value)
}
</script>

<template>
  <div class="select-wrapper" :class="{ 'select-wrapper--error': error, 'select-wrapper--disabled': disabled }">
    <label v-if="label" :for="name" class="select-label">{{ label }}</label>
    <div class="select-container">
      <select
        :id="name"
        :name="name"
        :value="modelValue"
        :disabled="disabled"
        class="select-field"
        @change="onChange"
      >
        <option value="" disabled selected>{{ placeholder }}</option>
        <option
          v-for="opt in options"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </option>
      </select>
      <div class="select-arrow">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </div>
    </div>
    <span v-if="error" class="select-error-msg">
      {{ error }}
    </span>
  </div>
</template>

<style scoped>
.select-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.select-label {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  font-weight: 500;
}

.select-container {
  position: relative;
  display: flex;
  align-items: center;
}

.select-field {
  width: 100%;
  min-height: 44px;
  padding: 10px 16px;
  padding-right: 40px;
  font-size: 16px;
  font-family: var(--font-sans);
  color: var(--color-text);
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  appearance: none;
  cursor: pointer;
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    background-color var(--transition-theme);
  outline: none;
}

.select-field:focus {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.select-field:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: var(--color-surface-3);
}

.select-arrow {
  position: absolute;
  right: 12px;
  pointer-events: none;
  color: var(--color-muted);
}

.select-wrapper--error .select-field {
  border-color: var(--color-error);
}

.select-error-msg {
  font-size: var(--text-xs);
  color: var(--color-error);
}
</style>
