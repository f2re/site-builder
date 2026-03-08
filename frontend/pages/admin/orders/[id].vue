<script setup lang="ts">
import type { C2CShipmentResponse } from '~/composables/useC2CShipment'

definePageMeta({
  layout: false,
  middleware: 'auth',
})

const route = useRoute()
const toast = useToast()
const orderId = route.params.id as string

const { data: order, pending } = await useApi<any>(`/admin/orders/${orderId}`)

const isC2CProvider = computed(() =>
  order.value?.delivery_provider === 'ozon' || order.value?.delivery_provider === 'wb'
)

const { data: c2cData, pending: c2cPending, error: c2cError } = isC2CProvider.value
  ? await useC2CShipment(orderId)
  : { data: ref(null), pending: ref(false), error: ref(null) }

const statusMap: Record<string, { label: string; variant: string }> = {
  pending: { label: 'Новый', variant: 'warning' },
  awaiting_payment: { label: 'Ожидает оплаты', variant: 'info' },
  paid: { label: 'Оплачен', variant: 'success' },
  shipped: { label: 'Отправлен', variant: 'info' },
  delivered: { label: 'Доставлен', variant: 'success' },
}

const providerLabel = computed(() => {
  if (!c2cData.value) return ''
  return c2cData.value.provider === 'ozon' ? 'Ozon' : 'WB Track'
})

async function copyC2CData() {
  if (!c2cData.value) return

  const text = `Заказ: ${c2cData.value.order_id}
Получатель: ${c2cData.value.recipient_name}
Телефон: ${c2cData.value.recipient_phone}
ПВЗ: ${c2cData.value.pvz_code} — ${c2cData.value.pvz_address}
Ценность: ${c2cData.value.declared_value} руб
Вес: ${c2cData.value.weight_kg} кг`

  try {
    await navigator.clipboard.writeText(text)
    toast.success('Данные скопированы')
  } catch (e) {
    toast.error('Ошибка копирования')
  }
}

function openDeeplink() {
  if (c2cData.value?.deeplink) {
    window.open(c2cData.value.deeplink, '_blank')
  }
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Заказ #{{ orderId.slice(0, 8) }}</template>

    <div data-testid="order-detail-page" class="order-detail-page">
      <NuxtLink to="/admin/orders" data-testid="order-back-link" class="back-link">
        ← Назад к списку
      </NuxtLink>

      <UCard v-if="pending" class="order-card">
        <div class="p-4 space-y-4">
          <USkeleton height="32px" />
          <USkeleton height="24px" />
          <USkeleton height="24px" />
        </div>
      </UCard>

      <UCard v-else-if="order" class="order-card">
        <div class="order-header">
          <h2 class="order-title">Заказ #{{ order.id.slice(0, 8) }}</h2>
          <UBadge
            data-testid="order-detail-status"
            :variant="statusMap[order.status]?.variant || 'default'"
          >
            {{ statusMap[order.status]?.label || order.status }}
          </UBadge>
        </div>

        <dl class="order-details">
          <div class="detail-row">
            <dt>Сумма</dt>
            <dd data-testid="order-detail-total" class="detail-value">{{ order.total_rub }} ₽</dd>
          </div>
          <div class="detail-row">
            <dt>Дата создания</dt>
            <dd class="detail-value">{{ new Date(order.created_at).toLocaleString() }}</dd>
          </div>
          <div class="detail-row">
            <dt>Адрес доставки</dt>
            <dd class="detail-value">{{ order.shipping_address || 'Не указан' }}</dd>
          </div>
          <div class="detail-row">
            <dt>Провайдер доставки</dt>
            <dd class="detail-value">{{ order.delivery_provider || 'Не указан' }}</dd>
          </div>
        </dl>
      </UCard>

      <UCard
        v-if="isC2CProvider && !c2cPending && !c2cError && c2cData"
        data-testid="c2c-shipment-card"
        class="c2c-card"
      >
        <h3 class="c2c-title">Карточка отправки {{ providerLabel }}</h3>

        <div v-if="c2cPending" class="p-4 space-y-3">
          <USkeleton height="24px" />
          <USkeleton height="24px" />
          <USkeleton height="24px" />
        </div>

        <div v-else-if="c2cError" class="c2c-error">
          Ошибка загрузки данных C2C
        </div>

        <div v-else class="c2c-content">
          <dl class="c2c-details">
            <div class="detail-row">
              <dt>Получатель</dt>
              <dd data-testid="c2c-recipient" class="detail-value">{{ c2cData.recipient_name }}</dd>
            </div>
            <div class="detail-row">
              <dt>Телефон</dt>
              <dd data-testid="c2c-phone" class="detail-value">{{ c2cData.recipient_phone }}</dd>
            </div>
            <div class="detail-row">
              <dt>ПВЗ</dt>
              <dd data-testid="c2c-pvz" class="detail-value">
                {{ c2cData.pvz_code }} — {{ c2cData.pvz_address }}
              </dd>
            </div>
            <div class="detail-row">
              <dt>Объявленная ценность</dt>
              <dd data-testid="c2c-value" class="detail-value">{{ c2cData.declared_value }} ₽</dd>
            </div>
            <div class="detail-row">
              <dt>Вес</dt>
              <dd class="detail-value">{{ c2cData.weight_kg }} кг</dd>
            </div>
            <div v-if="c2cData.comment" class="detail-row">
              <dt>Комментарий</dt>
              <dd class="detail-value">{{ c2cData.comment }}</dd>
            </div>
          </dl>

          <div class="c2c-instructions" data-testid="c2c-instructions">
            <h4 class="instructions-title">Инструкция для администратора</h4>
            <ol class="instructions-list">
              <li v-for="(step, idx) in c2cData.instructions" :key="idx">{{ step }}</li>
            </ol>
          </div>

          <div class="c2c-actions">
            <UButton
              data-testid="c2c-open-app-btn"
              variant="primary"
              @click="openDeeplink"
            >
              Открыть {{ providerLabel }}
            </UButton>
            <UButton
              data-testid="c2c-copy-btn"
              variant="secondary"
              @click="copyC2CData"
            >
              Скопировать данные
            </UButton>
          </div>
        </div>
      </UCard>
    </div>
  </NuxtLayout>
</template>

<style scoped>
.order-detail-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.back-link {
  color: var(--color-accent);
  text-decoration: none;
  font-size: var(--text-sm);
  transition: color var(--transition-fast);
}

.back-link:hover {
  color: var(--color-accent-hover);
}

.order-card,
.c2c-card {
  background: var(--color-surface);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
  flex-wrap: wrap;
}

.order-title {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.order-details,
.c2c-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-row {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 16px;
  align-items: start;
}

@media (max-width: 480px) {
  .detail-row {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}

.detail-row dt {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  font-weight: 500;
}

.detail-row dd {
  margin: 0;
}

.detail-value {
  font-size: var(--text-sm);
  color: var(--color-text);
}

.c2c-card {
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
}

.c2c-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-accent);
  margin: 0 0 24px 0;
}

.c2c-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.c2c-error {
  padding: 16px;
  color: var(--color-error);
  text-align: center;
}

.c2c-instructions {
  padding: 16px;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.instructions-title {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 12px 0;
}

.instructions-list {
  margin: 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.instructions-list li {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  line-height: 1.6;
}

.instructions-list li::marker {
  color: var(--color-accent);
  font-weight: 600;
}

.c2c-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .c2c-actions {
    flex-direction: column;
  }

  .c2c-actions button {
    width: 100%;
  }
}

.p-4 {
  padding: 16px;
}

.space-y-3 > * + * {
  margin-top: 12px;
}

.space-y-4 > * + * {
  margin-top: 16px;
}
</style>
