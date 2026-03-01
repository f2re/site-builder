<script setup lang="ts">
const route = useRoute()
const orderId = computed(() => route.query.order_id as string)
</script>

<template>
  <div class="failure-page">
    <div class="container container--narrow">
      <div class="failure-card">
        <div class="failure-header">
          <div class="failure-icon">
            <Icon name="ph:x-circle-fill" size="64" />
          </div>
          <h1 class="page-title">Оплата не прошла</h1>
          <p class="order-number" v-if="orderId">
            Номер заказа: <span>#{{ orderId.slice(0, 8) }}</span>
          </p>
        </div>

        <div class="failure-body">
          <p>
            К сожалению, при оплате заказа возникла ошибка. Деньги не были списаны.
            Попробуйте совершить оплату еще раз или выберите другой способ оплаты.
          </p>
        </div>

        <div class="failure-footer">
          <UButton v-if="orderId" :to="`/orders/${orderId}`" variant="primary" size="lg">
            Попробовать снова
          </UButton>
          <UButton to="/cart" variant="ghost" size="lg">
            Вернуться в корзину
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.failure-page {
  padding: 80px 0;
  min-height: calc(100vh - 400px);
  display: flex;
  align-items: center;
}

.container--narrow {
  max-width: 600px;
}

.failure-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 48px;
  text-align: center;
  box-shadow: var(--shadow-card);
  overflow: hidden;
  position: relative;
}

.failure-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--color-error), var(--color-accent));
}

.failure-icon {
  color: var(--color-error);
  margin-bottom: 24px;
  filter: drop-shadow(0 0 12px var(--color-error-bg));
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

.failure-body {
  margin-bottom: 40px;
  line-height: 1.6;
  color: var(--color-text-2);
  font-size: var(--text-base);
}

.failure-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (min-width: 480px) {
  .failure-footer {
    flex-direction: row;
    justify-content: center;
  }
}
</style>
