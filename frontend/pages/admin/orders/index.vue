<script setup lang="ts">
import UCard from '~/components/U/UCard.vue'
import UBadge from '~/components/U/UBadge.vue'
import USkeleton from '~/components/U/USkeleton.vue'
import USelect from '~/components/U/USelect.vue'

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const { data: orders, pending, refresh } = await useApi<any>('/admin/orders')
const apiFetch = useApiFetch()

const statusMap = {
  pending: { label: 'Новый', variant: 'warning' },
  awaiting_payment: { label: 'Ожидает оплаты', variant: 'info' },
  paid: { label: 'Оплачен', variant: 'success' },
  shipped: { label: 'Отправлен', variant: 'info' },
  delivered: { label: 'Доставлен', variant: 'success' },
}

const statusOptions = Object.keys(statusMap).map(s => ({ 
  value: s, 
  label: statusMap[s as keyof typeof statusMap].label 
}))

async function updateStatus(orderId: string, status: string) {
  try {
    await apiFetch(`/admin/orders/${orderId}`, {
      method: 'PATCH',
      body: { status },
    })
    await refresh()
  } catch (e) {
    console.error(e)
  }
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Заказы</template>

    <div class="admin-orders-page">
      <UCard class="table-card">
      <div v-if="pending" class="p-4 space-y-4">
        <USkeleton v-for="i in 5" :key="i" height="64px" />
      </div>
      <div v-else class="admin-table-wrapper">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Заказ</th>
              <th class="desktop-only">Сумма</th>
              <th class="desktop-only">Статус</th>
              <th class="desktop-only">Создан</th>
              <th class="actions-col">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders?.items" :key="order.id">
              <td>
                <div class="order-info">
                  <span class="order-id font-mono">#{{ order.id.slice(0, 8) }}</span>
                  <div class="order-meta mobile-only">
                    <span class="price">{{ order.total_rub }} ₽</span>
                    <span class="dot">•</span>
                    <UBadge :variant="statusMap[order.status as keyof typeof statusMap]?.variant || 'default'" size="sm">
                      {{ statusMap[order.status as keyof typeof statusMap]?.label || order.status }}
                    </UBadge>
                    <span class="dot">•</span>
                    <span class="date">{{ new Date(order.created_at).toLocaleDateString() }}</span>
                  </div>
                </div>
              </td>
              <td class="desktop-only">
                <span class="price-desktop">{{ order.total_rub }} ₽</span>
              </td>
              <td class="desktop-only">
                <UBadge :variant="statusMap[order.status as keyof typeof statusMap]?.variant || 'default'">
                  {{ statusMap[order.status as keyof typeof statusMap]?.label || order.status }}
                </UBadge>
              </td>
              <td class="desktop-only">
                <span class="date-desktop">{{ new Date(order.created_at).toLocaleDateString() }}</span>
              </td>
              <td class="actions-cell">
                <div class="actions">
                  <USelect
                    :modelValue="order.status"
                    @update:modelValue="updateStatus(order.id, $event)"
                    :options="statusOptions"
                    size="sm"
                    class="status-select"
                  />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!orders?.items?.length" class="empty-state">
          Заказы не найдены
        </div>
      </div>
    </UCard>
  </div>
  </NuxtLayout>
</template>

<style scoped>
.admin-orders-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.table-card {
  padding: 0;
  overflow: hidden;
}

.admin-table-wrapper {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.admin-table th {
  padding: 12px 16px;
  background: var(--color-surface-2);
  font-size: var(--text-xs);
  text-transform: uppercase;
  color: var(--color-text-2);
  border-bottom: 1px solid var(--color-border);
  font-weight: 700;
}

.admin-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order-id {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
}

.order-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  font-size: var(--text-xs);
  color: var(--color-text-2);
}

.dot {
  opacity: 0.5;
}

.price {
  font-weight: 600;
  color: var(--color-text);
}

.price-desktop {
  font-weight: 600;
}

.actions-col, .actions-cell {
  text-align: right;
  width: 180px;
}

.status-select {
  min-width: 140px;
}

.empty-state {
  padding: 48px;
  text-align: center;
  color: var(--color-text-2);
}

.desktop-only {
  display: none;
}

@media (min-width: 768px) {
  .desktop-only {
    display: table-cell;
  }
}

.mobile-only {
  display: flex;
}

@media (min-width: 768px) {
  .mobile-only {
    display: none;
  }
}

.font-mono { font-family: var(--font-mono); }
.p-4 { padding: 16px; }
.space-y-4 > * + * { margin-top: 16px; }
</style>
