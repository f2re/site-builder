<script setup lang="ts">
import type { DeliveryProvider } from '~/stores/deliveryStore'

interface Props {
  provider: DeliveryProvider
  label: string
  cost_rub?: number
  days_min?: number
  days_max?: number
  isSelected: boolean
  isLoading: boolean
  isDisabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isDisabled: false
})

const emit = defineEmits<{
  (e: 'click'): void
}>()

const daysText = computed(() => {
  if (!props.days_min || !props.days_max) return ''
  return props.days_min === props.days_max ? `${props.days_min} дн.` : `${props.days_min}–${props.days_max} дн.`
})
</script>

<template>
  <button
    class="provider-card"
    :class="{
      'provider-card--selected': isSelected,
      'provider-card--disabled': isDisabled
    }"
    :disabled="isDisabled"
    :data-testid="`delivery-provider-card-${provider}`"
    @click="emit('click')"
  >
    <Icon
      v-if="isSelected"
      name="ph:check-circle-fill"
      size="20"
      class="provider-card__check"
    />
    <div class="provider-card__logo">
      <Icon name="ph:package-bold" size="32" />
    </div>
    <div class="provider-card__label">{{ label }}</div>
    <div v-if="isLoading" class="provider-card__info">
      <USkeleton width="80px" height="16px" />
    </div>
    <div v-else-if="cost_rub !== undefined" class="provider-card__info">
      <span class="provider-card__price">от {{ cost_rub }} ₽</span>
      <span v-if="daysText" class="provider-card__days">{{ daysText }}</span>
    </div>
  </button>
</template>

<style scoped>
.provider-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-width: 140px;
  min-height: 120px;
  padding: 16px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface-2);
  color: var(--color-text);
  cursor: pointer;
  transition: border-color var(--transition-fast), transform var(--transition-fast), box-shadow var(--transition-fast);
}

.provider-card:hover:not(:disabled) {
  border-color: var(--color-accent);
  transform: translateY(-2px);
}

.provider-card--selected {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.provider-card--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.provider-card__check {
  position: absolute;
  top: 8px;
  right: 8px;
  color: var(--color-accent);
}

.provider-card__logo {
  color: var(--color-accent);
}

.provider-card__label {
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text);
  text-align: center;
}

.provider-card__info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.provider-card__price {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-accent);
}

.provider-card__days {
  font-size: var(--text-xs);
  color: var(--color-muted);
}
</style>
