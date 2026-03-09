<script setup lang="ts">
import { ref, computed } from 'vue'
import UCard from '~/components/U/UCard.vue'
import UBadge from '~/components/U/UBadge.vue'
import USkeleton from '~/components/U/USkeleton.vue'
import USelect from '~/components/U/USelect.vue'
import UButton from '~/components/U/UButton.vue'

const days = ref(10)
const daysOptions = [
  { value: 10, label: 'Последние 10 дней' },
  { value: 30, label: 'Последние 30 дней' },
  { value: 90, label: 'Последние 90 дней' },
]

const dateFrom = computed(() => {
  const d = new Date()
  d.setDate(d.getDate() - days.value)
  return d.toISOString().split('T')[0]
})

const { data: orders, pending } = await useApi<any>('/admin/orders', {
  query: computed(() => ({
    date_from: dateFrom.value,
    per_page: 5,
  })),
  watch: [days]
})

const statusMap: Record<string, { label: string, variant: string }> = {
  pending: { label: 'Новый', variant: 'warning' },
  awaiting_payment: { label: 'Ожидает оплаты', variant: 'info' },
  paid: { label: 'Оплачен', variant: 'success' },
  shipped: { label: 'Отправлен', variant: 'info' },
  delivered: { label: 'Доставлен', variant: 'success' },
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString(undefined, { 
    month: 'short', 
    day: 'numeric' 
  })
}
</script>

<template>
  <div class="recent-orders">
    <div class="widget-header">
      <h2 class="section-title">Последние заказы</h2>
      <USelect 
        v-model="days" 
        :options="daysOptions" 
        size="sm" 
        class="days-selector"
        data-testid="recent-orders-period"
      />
    </div>

    <UCard class="recent-orders-card">
      <div v-if="pending" class="orders-skeleton">
        <USkeleton v-for="i in 5" :key="i" height="48px" />
      </div>

      <div v-else-if="!orders?.items?.length" class="empty-state">
        <Icon name="ph:shopping-bag-open-bold" size="32" />
        <p>Заказов за выбранный период не найдено</p>
      </div>

      <div v-else class="orders-list">
        <div 
          v-for="order in orders.items" 
          :key="order.id" 
          class="order-item"
          data-testid="recent-order-item"
        >
          <div class="order-main">
            <NuxtLink :to="`/admin/orders/${order.id}`" class="order-link">
              #{{ order.id.slice(0, 8) }}
            </NuxtLink>
            <span class="order-date">{{ formatDate(order.created_at) }}</span>
          </div>
          
          <div class="order-details">
            <span class="order-amount">{{ (order.total_amount || order.total_rub).toLocaleString() }} ₽</span>
            <UBadge 
              :variant="statusMap[order.status]?.variant || 'default'" 
              size="sm"
              class="status-badge"
            >
              {{ statusMap[order.status]?.label || order.status }}
            </UBadge>
          </div>
        </div>
        
        <div class="view-all">
          <UButton to="/admin/orders" variant="ghost" size="sm" block>
            Показать все заказы
          </UButton>
        </div>
      </div>
    </UCard>
  </div>
</template>

<style scoped>
.recent-orders {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.widget-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.section-title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.days-selector {
  width: auto;
  min-width: 160px;
}

.recent-orders-card :deep(.card__body) {
  padding: 0;
}

.orders-skeleton {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px 24px;
  color: var(--color-text-3);
  gap: 12px;
}

.orders-list {
  display: flex;
  flex-direction: column;
}

.order-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  transition: background-color var(--transition-fast);
}

.order-item:hover {
  background-color: var(--color-bg-2);
}

.order-main {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.order-link {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
  text-decoration: none;
}

.order-link:hover {
  color: var(--color-accent);
}

.order-date {
  font-size: var(--text-xs);
  color: var(--color-text-3);
}

.order-details {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.order-amount {
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text);
}

.status-badge {
  font-size: 10px;
}

.view-all {
  padding: 12px;
}

@media (max-width: 640px) {
  .widget-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .days-selector {
    width: 100%;
  }
}
</style>
