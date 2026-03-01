<script setup lang="ts">
import { useOrders } from '~/composables/useOrders'

const route = useRoute()
const orderId = computed(() => (route.query.order_id || route.query.id) as string)

const { getOrder } = useOrders()
const { data: order, pending } = await getOrder(orderId.value)
</script>

<template>
  <div class="success-page">
    <div class="container container--narrow">
      <div class="success-card">
        <div class="success-header">
          <div class="success-icon">
            <Icon name="ph:check-circle-fill" size="64" />
          </div>
          <h1 class="page-title">Заказ оплачен!</h1>
          
          <div v-if="orderId" class="order-id-badge">
            Номер заказа: #{{ orderId.slice(0, 8) }}
          </div>
        </div>

        <div class="success-body">
          <template v-if="pending">
            <USkeleton width="100%" height="20px" class="mb-2" />
            <USkeleton width="80%" height="20px" class="mx-auto" />
          </template>
          
          <template v-else-if="order">
            <div class="order-brief">
              <p class="thanks-text">
                Спасибо за ваш заказ, {{ order.delivery.address ? 'мы уже начали его обработку' : 'мы свяжемся с вами' }}!
              </p>
              
              <div class="order-summary-box">
                <div class="summary-line">
                  <span>Сумма заказа:</span>
                  <span class="highlight">{{ order.total_rub }} ₽</span>
                </div>
                <div class="summary-line">
                  <span>Статус:</span>
                  <span class="status-tag" :data-status="order.status">{{ order.status }}</span>
                </div>
              </div>

              <div class="items-preview">
                <div v-for="item in order.items.slice(0, 3)" :key="item.product_id" class="item-mini">
                  {{ item.name }} × {{ item.quantity }}
                </div>
                <div v-if="order.items.length > 3" class="more-items">
                  и еще {{ order.items.length - 3 }} товаров
                </div>
              </div>
            </div>
          </template>
          
          <p v-else>
            Спасибо за ваш заказ! Мы уже начали его обработку.
            Вы получите уведомление на электронную почту, когда статус заказа изменится.
          </p>
        </div>

        <div class="success-footer">
          <UButton to="/products" variant="primary" size="lg">
            В каталог
          </UButton>
          <UButton v-if="orderId" :to="`/orders/${orderId}`" variant="ghost" size="lg">
            Детали заказа
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.success-page {
  padding: 80px 0;
  min-height: calc(100vh - 400px);
  display: flex;
  align-items: center;
}

.container--narrow {
  max-width: 600px;
}

.success-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 48px;
  text-align: center;
  box-shadow: var(--shadow-card);
  overflow: hidden;
  position: relative;
}

.success-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--color-success), var(--color-neon));
}

.success-icon {
  color: var(--color-success);
  margin-bottom: 24px;
  filter: drop-shadow(0 0 12px var(--color-success-bg));
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: 800;
  margin-bottom: 12px;
  background: linear-gradient(135deg, var(--color-text) 0%, var(--color-text-2) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.order-id-badge {
  display: inline-block;
  padding: 4px 12px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-2);
  margin-bottom: 32px;
}

.success-body {
  margin-bottom: 40px;
  line-height: 1.6;
  color: var(--color-text-2);
}

.thanks-text {
  margin-bottom: 24px;
}

.order-summary-box {
  background: var(--color-bg-subtle);
  border-radius: var(--radius-lg);
  padding: 20px;
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-line {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-sm);
}

.highlight {
  color: var(--color-text);
  font-weight: 700;
}

.status-tag {
  font-size: 10px;
  text-transform: uppercase;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--color-surface-3);
}

.items-preview {
  font-size: var(--text-xs);
  color: var(--color-muted);
  text-align: left;
  border-left: 2px solid var(--color-border);
  padding-left: 16px;
  max-width: 300px;
  margin: 0 auto 24px;
}

.item-mini {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.success-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (min-width: 480px) {
  .success-footer {
    flex-direction: row;
    justify-content: center;
  }
}

.mx-auto { margin-left: auto; margin-right: auto; }
.mb-2 { margin-bottom: 8px; }
</style>
