<script setup lang="ts">
import { useOrders } from '~/composables/useOrders'
import { useAuth } from '~/composables/useAuth'

const { getOrders } = useOrders()
const { accessToken } = useAuth()
const router = useRouter()

useHead({
  meta: [
    { name: 'robots', content: 'noindex' }
  ]
})

// Redirect to login if not authenticated
onMounted(() => {
  if (!accessToken.value) {
    router.push('/auth/login')
  }
})

const { data: ordersData, pending, error, refresh } = getOrders({ per_page: 20 })

const formatStatus = (status: string) => {
  const mapping: Record<string, { label: string; variant: any }> = {
    'pending':          { label: 'Ожидает',        variant: 'info' },
    'awaiting_payment': { label: 'Ожидает оплаты', variant: 'warning' },
    'paid':             { label: 'Оплачен',        variant: 'success' },
    'shipped':          { label: 'Отправлен',      variant: 'accent' },
    'delivered':        { label: 'Доставлен',      variant: 'success' },
    'cancelled':        { label: 'Отменен',        variant: 'error' },
  }
  return mapping[status] || { label: status, variant: 'info' }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div class="profile-orders-page">
    <div class="container">
      <div class="profile-header">
        <h1 class="page-title">Мои заказы</h1>
        <NuxtLink to="/products" class="btn btn-ghost btn-sm">Вернуться в магазин</NuxtLink>
      </div>

      <div v-if="pending" class="orders-loading">
        <USkeleton v-for="i in 3" :key="i" height="120px" style="margin-bottom: 16px; border-radius: var(--radius-lg)" />
      </div>

      <div v-else-if="error" class="orders-error">
        <div class="error-msg">Не удалось загрузить историю заказов.</div>
        <UButton variant="secondary" @click="() => refresh()">Повторить</UButton>
      </div>

      <div v-else-if="!ordersData?.items?.length" class="orders-empty">
        <div class="empty-icon">🛒</div>
        <h2 class="empty-title">У вас пока нет заказов</h2>
        <p class="empty-text">История ваших покупок появится здесь после оформления заказа.</p>
        <UButton to="/products" variant="primary">В каталог</UButton>
      </div>

      <div v-else class="orders-list">
        <UCard v-for="order in ordersData.items" :key="order.id" class="order-card">
          <div class="order-header">
            <div class="order-info">
              <span class="order-id">Заказ #{{ order.id.split('-')[0].toUpperCase() }}</span>
              <span class="order-date">{{ formatDate(order.created_at) }}</span>
            </div>
            <UBadge :variant="formatStatus(order.status).variant">
              {{ formatStatus(order.status).label }}
            </UBadge>
          </div>

          <div class="order-items">
            <div v-for="item in order.items" :key="item.product_id" class="order-item">
              {{ item.name }} × {{ item.quantity }}
            </div>
          </div>

          <div class="order-footer">
            <div class="order-delivery">
              <span class="delivery-label">Доставка:</span>
              <span class="delivery-value">{{ order.delivery?.type === 'cdek_pvz' ? 'В пункт выдачи' : 'Курьером' }}</span>
            </div>
            <div class="order-total">
              <span class="total-label">Сумма:</span>
              <span class="total-value">{{ order.total_rub }} ₽</span>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-orders-page {
  padding: 40px 0;
  min-height: calc(100vh - 200px);
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin: 0;
  letter-spacing: -1px;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-card {
  padding: 24px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order-id {
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--color-text);
}

.order-date {
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.order-items {
  border-top: 1px solid var(--color-border);
  padding: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.order-footer {
  border-top: 1px solid var(--color-border);
  padding-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-delivery {
  font-size: var(--text-xs);
  display: flex;
  gap: 6px;
}

.delivery-label { color: var(--color-muted); }
.delivery-value { font-weight: 500; color: var(--color-text-2); }

.order-total {
  display: flex;
  align-items: center;
  gap: 8px;
}

.total-label {
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.total-value {
  font-size: var(--text-lg);
  font-weight: 800;
  color: var(--color-accent);
}

.orders-empty {
  text-align: center;
  padding: 80px 0;
}

.empty-icon { font-size: 4rem; margin-bottom: 24px; }
.empty-title { font-size: var(--text-xl); font-weight: 700; margin-bottom: 12px; }
.empty-text { color: var(--color-text-2); margin-bottom: 32px; max-width: 400px; margin-inline: auto; }

@media (max-width: 600px) {
  .order-header { flex-direction: column; gap: 12px; }
  .order-footer { flex-direction: column; align-items: flex-start; gap: 12px; }
}
</style>
