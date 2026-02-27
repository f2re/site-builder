<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
}>()

const steps = [
  { key: 'pending', label: 'Ожидает оплаты', icon: 'ph:clock-bold' },
  { key: 'paid', label: 'Оплачен', icon: 'ph:check-circle-bold' },
  { key: 'processing', label: 'В обработке', icon: 'ph:gear-six-bold' },
  { key: 'shipped', label: 'Отправлен', icon: 'ph:truck-bold' },
  { key: 'delivered', label: 'Доставлен', icon: 'ph:house-line-bold' },
]

const currentIndex = computed(() => {
  return steps.findIndex(step => step.key === props.status.toLowerCase())
})

const isCancelled = computed(() => props.status.toLowerCase() === 'cancelled')

const getStepStatus = (index: number) => {
  if (isCancelled.value) return 'inactive'
  if (index < currentIndex.value) return 'completed'
  if (index === currentIndex.value) return 'active'
  return 'upcoming'
}
</script>

<template>
  <div class="order-status" :class="{ 'is-cancelled': isCancelled }">
    <div v-if="isCancelled" class="cancelled-badge">
      <Icon name="ph:x-circle-bold" size="20" />
      <span>Заказ отменен</span>
    </div>

    <div v-else class="status-steps">
      <div 
        v-for="(step, index) in steps" 
        :key="step.key"
        class="step"
        :class="getStepStatus(index)"
      >
        <div class="step-line" v-if="index > 0"></div>
        <div class="step-content">
          <div class="step-icon-wrap">
            <Icon :name="step.icon" size="20" />
          </div>
          <span class="step-label">{{ step.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.order-status {
  width: 100%;
  padding: 24px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.cancelled-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--color-error);
  font-weight: 700;
  font-size: var(--text-lg);
  padding: 12px;
  background: var(--color-error-bg);
  border-radius: var(--radius-md);
}

.status-steps {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  position: relative;
}

.step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 1;
}

.step-line {
  position: absolute;
  top: 20px;
  right: 50%;
  width: 100%;
  height: 2px;
  background: var(--color-border);
  z-index: -1;
  transition: background var(--transition-normal);
}

.step.completed .step-line,
.step.active .step-line {
  background: var(--color-neon);
  box-shadow: var(--shadow-glow-neon);
}

.step-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-3);
  border: 2px solid var(--color-border);
  color: var(--color-muted);
  transition: all var(--transition-normal);
}

.step-label {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-muted);
  text-align: center;
  transition: color var(--transition-normal);
}

/* Status variants */
.step.completed .step-icon-wrap {
  background: var(--color-neon-glow);
  border-color: var(--color-neon);
  color: var(--color-neon);
}

.step.completed .step-label {
  color: var(--color-text);
}

.step.active .step-icon-wrap {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: var(--color-on-accent);
  box-shadow: var(--shadow-glow-accent);
  transform: scale(1.1);
}

.step.active .step-label {
  color: var(--color-accent);
  font-weight: 700;
}

@media (max-width: 640px) {
  .status-steps {
    flex-direction: column;
    gap: 24px;
    align-items: flex-start;
  }
  
  .step {
    flex-direction: row;
    width: 100%;
    align-items: center;
  }
  
  .step-line {
    top: -24px;
    right: auto;
    left: 20px;
    width: 2px;
    height: 24px;
  }
  
  .step-content {
    flex-direction: row;
    gap: 16px;
  }
  
  .step-label {
    text-align: left;
    font-size: var(--text-sm);
  }
}
</style>
