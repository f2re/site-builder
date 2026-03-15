<script setup lang="ts">
import { computed } from 'vue'
import type { ProductOptionGroup } from '~/composables/useProducts'
import { formatPrice } from '~/composables/useFormatters'

const props = defineProps<{
  optionGroups: ProductOptionGroup[]
  modelValue: Record<string, string | string[]>
  showValidation?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, string | string[]>]
}>()

const formatModifier = (modifier: number): string => {
  if (modifier === 0) return 'Без доплаты'
  const sign = modifier > 0 ? '+' : ''
  return `${sign}${formatPrice(modifier)}`
}

const isGroupInvalid = (group: ProductOptionGroup): boolean => {
  if (!props.showValidation) return false
  if (!group.is_required) return false
  const val = props.modelValue[group.id]
  if (group.type === 'checkbox') {
    return !val || (Array.isArray(val) && val.length === 0)
  }
  return !val
}

const selectValue = (groupId: string, valueId: string): void => {
  emit('update:modelValue', {
    ...props.modelValue,
    [groupId]: valueId,
  })
}

const toggleCheckboxValue = (groupId: string, valueId: string): void => {
  const current = props.modelValue[groupId]
  const arr = Array.isArray(current) ? [...current] : []
  const idx = arr.indexOf(valueId)
  if (idx >= 0) {
    arr.splice(idx, 1)
  } else {
    arr.push(valueId)
  }
  emit('update:modelValue', {
    ...props.modelValue,
    [groupId]: arr,
  })
}

const isSelected = (groupId: string, valueId: string): boolean => {
  const val = props.modelValue[groupId]
  if (Array.isArray(val)) {
    return val.includes(valueId)
  }
  return val === valueId
}

const hasOptions = computed(() => props.optionGroups.length > 0)
</script>

<template>
  <div v-if="hasOptions" class="option-selector" data-testid="product-options-selector">
    <div
      v-for="group in optionGroups"
      :key="group.id"
      class="option-selector__group"
      :class="{ 'is-invalid': isGroupInvalid(group) }"
      :data-testid="`option-group-${group.id}`"
    >
      <div class="option-selector__group-label">
        <span class="option-selector__group-name">{{ group.name }}</span>
        <span v-if="group.is_required" class="option-selector__required" aria-label="Обязательное поле">*</span>
      </div>

      <div
        class="option-selector__values"
        role="group"
        :aria-label="group.name"
      >
        <!-- Single-select (radio-style) for non-checkbox groups -->
        <template v-if="group.type !== 'checkbox'">
          <button
            v-for="val in group.values"
            :key="val.id"
            type="button"
            class="option-chip"
            :class="{ 'is-active': isSelected(group.id, val.id) }"
            :aria-pressed="isSelected(group.id, val.id)"
            :aria-label="`${val.name}${val.price_modifier !== 0 ? ', ' + formatModifier(val.price_modifier) : ''}`"
            :data-testid="`option-value-${val.id}`"
            @click="selectValue(group.id, val.id)"
          >
            <span class="option-chip__name">{{ val.name }}</span>
            <span
              v-if="val.price_modifier !== 0"
              class="option-chip__modifier"
              :class="{
                'is-positive': val.price_modifier > 0,
                'is-negative': val.price_modifier < 0,
              }"
            >
              {{ formatModifier(val.price_modifier) }}
            </span>
            <span v-else class="option-chip__modifier is-neutral">
              Без доплаты
            </span>
          </button>
        </template>

        <!-- Multi-select (checkbox-style) groups -->
        <template v-else>
          <button
            v-for="val in group.values"
            :key="val.id"
            type="button"
            class="option-chip option-chip--checkbox"
            :class="{ 'is-active': isSelected(group.id, val.id) }"
            :aria-pressed="isSelected(group.id, val.id)"
            :aria-label="`${val.name}${val.price_modifier !== 0 ? ', ' + formatModifier(val.price_modifier) : ''}`"
            :data-testid="`option-value-${val.id}`"
            @click="toggleCheckboxValue(group.id, val.id)"
          >
            <span class="option-chip__check" aria-hidden="true">
              <svg v-if="isSelected(group.id, val.id)" width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
            <span class="option-chip__name">{{ val.name }}</span>
            <span
              v-if="val.price_modifier !== 0"
              class="option-chip__modifier"
              :class="{
                'is-positive': val.price_modifier > 0,
                'is-negative': val.price_modifier < 0,
              }"
            >
              {{ formatModifier(val.price_modifier) }}
            </span>
            <span v-else class="option-chip__modifier is-neutral">
              Без доплаты
            </span>
          </button>
        </template>
      </div>

      <!-- Validation error -->
      <div
        v-if="isGroupInvalid(group)"
        class="option-selector__error"
        role="alert"
        :data-testid="`option-group-error-${group.id}`"
      >
        Выберите вариант
      </div>
    </div>
  </div>
</template>

<style scoped>
.option-selector {
  display: flex;
  flex-direction: column;
  gap: 16px;
  border-top: 1px solid var(--color-border);
  padding-top: 16px;
}

.option-selector__group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: border-color var(--transition-fast);
}

.option-selector__group.is-invalid {
  border-color: var(--color-error);
  background: var(--color-error-bg, rgba(230, 57, 70, 0.06));
}

.option-selector__group-label {
  display: flex;
  align-items: center;
  gap: 4px;
}

.option-selector__group-name {
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-muted);
}

.option-selector__required {
  color: var(--color-error);
  font-size: var(--text-sm);
  font-weight: 700;
  line-height: 1;
}

.option-selector__values {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Option chip (pill/radio-card style) */
.option-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition:
    border-color var(--transition-fast),
    background var(--transition-fast),
    box-shadow var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
  min-height: 44px;
  white-space: nowrap;
}

.option-chip:hover {
  border-color: var(--color-accent);
  background: var(--color-bg-subtle);
  transform: translateY(-1px);
}

.option-chip:active {
  transform: scale(0.97);
}

.option-chip.is-active {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
  color: var(--color-accent);
  box-shadow: 0 0 0 1px var(--color-accent), var(--shadow-glow-accent);
}

.option-chip__name {
  font-size: var(--text-sm);
}

.option-chip__modifier {
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  color: var(--color-muted);
  transition: color var(--transition-fast);
}

.option-chip__modifier.is-positive {
  color: var(--color-success);
}

.option-chip__modifier.is-negative {
  color: var(--color-error);
}

.option-chip__modifier.is-neutral {
  color: var(--color-muted);
}

.option-chip.is-active .option-chip__modifier {
  color: var(--color-accent);
}

/* Checkbox chip variant */
.option-chip--checkbox {
  gap: 8px;
}

.option-chip__check {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  flex-shrink: 0;
  transition: border-color var(--transition-fast), background var(--transition-fast);
  color: var(--color-on-accent);
}

.option-chip.is-active .option-chip__check {
  background: var(--color-accent);
  border-color: var(--color-accent);
}

.option-selector__error {
  font-size: var(--text-xs);
  color: var(--color-error);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.option-selector__error::before {
  content: '!';
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--color-error);
  color: #fff;
  font-size: 9px;
  font-weight: 800;
  flex-shrink: 0;
}

/* Mobile responsive */
@media (max-width: 480px) {
  .option-selector__values {
    gap: 6px;
  }

  .option-chip {
    padding: 7px 12px;
    font-size: var(--text-xs);
  }
}
</style>
