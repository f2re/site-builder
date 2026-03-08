<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useOrders } from '~/composables/useOrders'
import { useToast } from '~/composables/useToast'

const route = useRoute()
const { accessToken } = useAuth()
const orderId = route.params.id as string
const toast = useToast()

const { getOrder } = useOrders()
const { data: order, refresh, error } = await getOrder(orderId)

const lastStatus = ref(order.value?.status)
let pollInterval: ReturnType<typeof setInterval> | null = null

const startPolling = () => {
  pollInterval = setInterval(async () => {
    await refresh()
    if (order.value && order.value.status !== lastStatus.value) {
      toast.success('Статус обновлён', `Новый статус заказа`)
      lastStatus.value = order.value.status
    }
  }, 30000)
}

onMounted(() => {
  if (order.value && !['delivered', 'cancelled'].includes(order.value.status)) {
    startPolling()
  }
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})

useSeoMeta({
  title: `Заказ #${orderId} — WifiOBD`,
  description: 'Отслеживание статуса заказа',
})

const breadcrumbs = computed(() => [
  { label: 'Главная', to: '/' },
  { label: 'Мои заказы', to: accessToken.value ? '/profile/orders' : '/auth/login' },
  { label: `Заказ #${orderId}`, to: `/orders/${orderId}` },
])
</script>

<template>
  <div class="order-detail-page">
    <div class="container">
      <AppBreadcrumbs :crumbs="breadcrumbs" />

      <div v-if="error" class="error-state">
        <h1 class="page-title">Заказ не найден</h1>
        <p>К сожалению, мы не смогли найти информацию о заказе #{{ orderId }}</p>
        <UButton to="/products" variant="primary" class="mt-8">Вернуться в магазин</UButton>
      </div>

      <div v-else-if="order" class="order-content" data-testid="order-detail">
        <div class="order-header">
          <h1 class="page-title">Заказ #{{ orderId.split('-')[0].toUpperCase() }}</h1>
          <StatusBadge :status="order.status" />
        </div>
        <div class="order-date">от {{ new Date(order.created_at).toLocaleDateString() }}</div>

        <TrackingButton
          v-if="order.delivery?.tracking_url"
          :tracking-url="order.delivery.tracking_url"
          :provider="order.delivery.provider || 'cdek'"
          class="tracking-btn-spacing"
        />

        <div class="order-grid">
          <!-- Order Items -->
          <div class="order-info-col">
            <div class="items-card">
              <h2 class="section-title">Состав заказа</h2>
              <div class="items-list">
                <div v-for="item in order.items" :key="item.product_id" class="order-item" data-testid="order-item">
                  <div class="item-details">
                    <div class="item-name">{{ item.name }}</div>
                    <div class="item-meta">Количество: {{ item.quantity }}</div>
                  </div>
                  <div class="item-price">{{ item.price_rub * item.quantity }} ₽</div>
                </div>
              </div>
              <div class="order-total">
                <span>Итого к оплате</span>
                <span>{{ order.total_rub }} ₽</span>
              </div>
            </div>
          </div>

          <!-- Delivery / Payment Info -->
          <div class="order-sidebar-col">
            <div class="delivery-card">
              <h2 class="section-title">Доставка</h2>
              <div class="delivery-info">
                <div class="info-label">Способ:</div>
                <div class="info-value">{{ order.delivery.type === 'cdek_pvz' ? 'Пункт выдачи СДЭК' : 'Доставка курьером' }}</div>

                <div class="info-label mt-4">Адрес:</div>
                <div class="info-value">{{ order.delivery.address || '—' }}</div>

                <div v-if="order.delivery.pvz_code" class="info-label mt-4">Пункт выдачи:</div>
                <div v-if="order.delivery.pvz_code" class="info-value">Код: {{ order.delivery.pvz_code }}</div>
              </div>
            </div>

            <div v-if="order.status === 'pending' && order.payment_url" class="payment-card mt-6">
              <h2 class="section-title">Оплата</h2>
              <p class="mb-4">Заказ еще не оплачен. Пожалуйста, завершите оплату, чтобы мы начали сборку.</p>
              <a :href="order.payment_url" class="btn btn--primary w-full" target="_blank" rel="noopener">Оплатить {{ order.total_rub }} ₽</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.order-detail-page {
  padding: 40px 0;
}

.error-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--color-muted);
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 8px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 16px;
}

.order-date {
  color: var(--color-muted);
  font-size: var(--text-sm);
  margin-bottom: 24px;
}

.tracking-btn-spacing {
  margin-bottom: 32px;
}

.order-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 32px;
}

.items-card,
.delivery-card,
.payment-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.section-title {
  font-size: var(--text-lg);
  font-weight: 700;
  margin-bottom: 24px;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.item-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.item-meta {
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.item-price {
  font-weight: 700;
}

.order-total {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-xl);
  font-weight: 800;
  color: var(--color-accent);
}

.info-label {
  font-size: var(--text-xs);
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-weight: 600;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  font-weight: 700;
  font-size: var(--text-sm);
  cursor: pointer;
  border: none;
  text-decoration: none;
  transition: background var(--transition-fast);
  min-height: 44px;
}

.btn--primary {
  background: var(--color-accent);
  color: var(--color-on-accent);
}

.btn--primary:hover {
  background: var(--color-accent-hover);
}

.mt-4 { margin-top: 16px; }
.mt-6 { margin-top: 24px; }
.mt-8 { margin-top: 32px; }
.mb-4 { margin-bottom: 16px; }
.w-full { width: 100%; }

@media (max-width: 900px) {
  .order-grid {
    grid-template-columns: 1fr;
  }
}
</style>
