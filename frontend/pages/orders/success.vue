<script setup lang="ts">
const route = useRoute()
const orderId = computed(() => route.query.order_id as string)
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
          <p class="order-number" v-if="orderId">
            Номер заказа: <span>#{{ orderId.slice(0, 8) }}</span>
          </p>
        </div>

        <div class="success-body">
          <p>
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

.order-number {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  font-family: var(--font-mono);
  margin-bottom: 32px;
}

.order-number span {
  color: var(--color-accent);
  font-weight: 700;
}

.success-body {
  margin-bottom: 40px;
  line-height: 1.6;
  color: var(--color-text-2);
  font-size: var(--text-base);
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
</style>
