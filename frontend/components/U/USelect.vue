<script setup lang="ts">
interface Option {
  label?: string
  value?: string | number
  id?: string | number
  name?: string
}

interface Props {
  modelValue: string | number | null | undefined
  options: Option[]
  label?: string
  placeholder?: string
  disabled?: boolean
  error?: string
  name?: string
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Выберите...',
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number | null]
}>()

const onChange = (e: Event) => {
  const val = (e.target as HTMLSelectElement).value
  emit('update:modelValue', val === '' ? null : val)
}
</script>

<template>
  <div 
    class="select-wrapper" 
    :class="{ 
      'select-wrapper--error': error, 
      'select-wrapper--disabled': disabled,
      'select-wrapper--has-icon': icon
    }"
  >
    <label v-if="label" :for="name" class="select-label">{{ label }}</label>
    <div class="select-container">
      <div v-if="icon" class="select-prefix-icon">
        <Icon :name="icon" size="18" />
      </div>

      <select
        :id="name"
        :name="name"
        :value="modelValue || ''"
        :disabled="disabled"
        class="select-field"
        @change="onChange"
      >
        <option value="" disabled>{{ placeholder }}</option>
        <option
          v-for="opt in options"
          :key="opt.id || opt.value"
          :value="opt.id !== undefined ? opt.id : opt.value"
        >
          {{ opt.name || opt.label }}
        </option>
      </select>
      
      <div class="select-arrow">
        <Icon name="ph:caret-down-bold" size="16" />
      </div>
    </div>
    <Transition name="slide-up">
      <span v-if="error" class="select-error-msg">
        <Icon name="ph:warning-bold" size="14" style="margin-right: 4px;" />
        {{ error }}
      </span>
    </Transition>
  </div>
</template>

<style scoped>
.select-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.select-label {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  font-weight: 600;
  transition: color var(--transition-fast);
}

.select-container {
  position: relative;
  display: flex;
  align-items: center;
}

.select-prefix-icon {
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

.select-field {
  width: 100%;
  min-height: 48px;
  padding: 12px 16px;
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
    background-color var(--transition-theme),
    color var(--transition-theme);
  outline: none;
}

.select-wrapper--has-icon .select-field {
  padding-left: 44px;
}

.select-field:focus {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
  background-color: var(--color-surface-3);
}

.select-field:focus ~ .select-prefix-icon {
  color: var(--color-accent);
}

.select-wrapper:focus-within .select-label {
  color: var(--color-accent);
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
  display: flex;
  align-items: center;
}

.select-wrapper--error .select-field {
  border-color: var(--color-error);
}

.select-error-msg {
  font-size: var(--text-xs);
  color: var(--color-error);
  font-weight: 500;
  display: flex;
  align-items: center;
  margin-top: 2px;
}

/* Animations */
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.2s ease-out; }
.slide-up-enter-from { opacity: 0; transform: translateY(-4px); }
.slide-up-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
