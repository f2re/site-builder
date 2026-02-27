<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useIntervalFn } from '@vueuse/core'
import { useOrders } from '~/composables/useOrders'
import OrderStatus from '~/components/shop/OrderStatus.vue'

const route = useRoute()
const orderId = route.params.id as string
const { getOrder } = useOrders()

const { data: order, refresh, error } = await getOrder(orderId)

// Polling every 30s to check for status updates (e.g. PAID)
const { pause, resume } = useIntervalFn(() => {
  if (order.value && !['delivered', 'cancelled', 'refunded'].includes(order.value.status)) {
    refresh()
  }
}, 30000)

useSeoMeta({
  title: `Заказ #${orderId} — WifiOBD`,
  description: 'Отслеживание статуса заказа',
})

const breadcrumbs = computed(() => [
  { label: 'Главная', to: '/' },
  { label: 'Мои заказы', to: '/profile' },
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

      <div v-else-if="order" class="order-content">
        <div class="order-header">
          <h1 class="page-title">Заказ #{{ orderId }}</h1>
          <div class="order-date">от {{ new Date(order.created_at).toLocaleDateString() }}</div>
        </div>

        <UCard class="status-card">
          <OrderStatus :status="order.status" />
        </UCard>

        <div class="order-grid">
          <!-- Order Items -->
          <div class="order-info-col">
            <UCard class="items-card">
              <h2 class="section-title">Состав заказа</h2>
              <div class="items-list">
                <div v-for="item in order.items" :key="item.product_id" class="order-item">
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
            </UCard>
          </div>

          <!-- Delivery / Payment Info -->
          <div class="order-sidebar-col">
            <UCard class="delivery-card">
              <h2 class="section-title">Доставка</h2>
              <div class="delivery-info">
                <div class="info-label">Способ:</div>
                <div class="info-value">{{ order.delivery.type === 'cdek_pvz' ? 'Пункт выдачи СДЭК' : 'Доставка курьером' }}</div>
                
                <div class="info-label mt-4">Адрес:</div>
                <div class="info-value">{{ order.delivery.address || '—' }}</div>
                
                <div v-if="order.delivery.pvz_code" class="info-label mt-4">Пункт выдачи:</div>
                <div v-if="order.delivery.pvz_code" class="info-value">Код: {{ order.delivery.pvz_code }}</div>
              </div>
            </UCard>

            <UCard v-if="order.status === 'pending' && order.payment_url" class="payment-card mt-6">
              <h2 class="section-title">Оплата</h2>
              <p class="mb-4">Заказ еще не оплачен. Пожалуйста, завершите оплату, чтобы мы начали сборку.</p>
              <UButton :to="order.payment_url" variant="primary" external class="w-full">Оплатить {{ order.total_rub }} ₽</UButton>
            </UCard>
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

.page-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 8px;
}

.order-header {
  margin-bottom: 32px;
}

.order-date {
  color: var(--color-muted);
  font-size: var(--text-sm);
}

.status-card {
  margin-bottom: 32px;
  padding: 32px;
}

.order-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 32px;
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
