<script setup lang="ts">
import { computed } from 'vue'

interface AttentionStats {
  new_orders: number
  unpaid_orders: number
  to_ship_orders: number
  problem_orders: number
}

const props = defineProps<{
  stats?: AttentionStats
  pending?: boolean
}>()

const items = computed(() => {
  return [
    { 
      id: 'new', 
      label: 'Новые', 
      count: 0,
      icon: 'ph:plus-circle-bold', 
      color: 'var(--color-info)',
      query: { status: 'pending' },
      dataTestId: 'attention-new-orders'
    },
    { 
      id: 'unpaid', 
      label: 'Неоплаченные', 
      count: 0,
      icon: 'ph:credit-card-bold', 
      color: 'var(--color-warning)',
      query: { status: 'awaiting_payment' },
      dataTestId: 'attention-unpaid-orders'
    },
    { 
      id: 'to_ship', 
      label: 'К отправке', 
      count: 0,
      icon: 'ph:package-bold', 
      color: 'var(--color-accent)',
      query: { status: 'paid' },
      dataTestId: 'attention-to-ship-orders'
    },
    { 
      id: 'problem', 
      label: 'Проблемные', 
      count: 0,
      icon: 'ph:warning-circle-bold', 
      color: 'var(--color-danger)',
      query: { status: 'problem' },
      dataTestId: 'attention-problem-orders'
    }
  ].map(item => ({
    ...item,
    // @ts-ignore
    count: props.stats?.[`${item.id}_orders`] || 0
  }))
})
</script>

<template>
  <div class="attention-stats">
    <div v-if="pending" class="attention-grid">
      <div v-for="i in 4" :key="i" class="attention-skeleton" />
    </div>
    
    <div v-else class="attention-grid">
      <NuxtLink 
        v-for="item in items" 
        :key="item.id" 
        :to="{ path: '/admin/orders', query: item.query }"
        class="attention-card"
        :class="{ 'has-count': item.count > 0 }"
        :data-testid="item.dataTestId"
      >
        <div class="attention-icon" :style="{ color: item.color, background: `${item.color}15` }">
          <Icon :name="item.icon" size="20" />
        </div>
        <div class="attention-info">
          <span class="attention-label">{{ item.label }}</span>
          <span class="attention-count">{{ item.count }}</span>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<style scoped>
.attention-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

@media (min-width: 768px) {
  .attention-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
  }
}

.attention-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-bg-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.attention-card:hover {
  border-color: var(--color-accent);
  transform: translateY(-2px);
  background: var(--color-bg-3);
}

.attention-card.has-count {
  border-color: var(--color-accent-30);
  background: var(--color-bg-2);
}

.attention-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.attention-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.attention-label {
  font-size: var(--text-xs);
  color: var(--color-text-2);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.attention-count {
  font-size: var(--text-md);
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.2;
}

.attention-skeleton {
  height: 66px;
  background: var(--color-bg-2);
  border-radius: var(--radius-md);
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .5; }
}
</style>
