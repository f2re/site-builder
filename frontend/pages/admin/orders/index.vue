<script setup lang="ts">
definePageMeta({
  layout: 'admin',
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
  <div>
    <div class="mb-6">
      <h1 class="text-xl font-bold">Заказы</h1>
    </div>

    <UCard class="overflow-hidden">
      <div v-if="pending" class="p-4 space-y-4">
        <USkeleton v-for="i in 5" :key="i" height="40px" />
      </div>
      <table v-else class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Сумма</th>
            <th>Статус</th>
            <th>Создан</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders?.items" :key="order.id">
            <td>
              <span class="font-mono text-xs">#{{ order.id.slice(0, 8) }}</span>
            </td>
            <td>{{ order.total_rub }} ₽</td>
            <td>
              <UBadge :variant="statusMap[order.status]?.variant || 'default'">
                {{ statusMap[order.status]?.label || order.status }}
              </UBadge>
            </td>
            <td>{{ new Date(order.created_at).toLocaleDateString() }}</td>
            <td>
              <div class="actions">
                <USelect
                  :modelValue="order.status"
                  @update:modelValue="updateStatus(order.id, $event)"
                  :options="Object.keys(statusMap).map(s => ({ value: s, label: statusMap[s].label }))"
                  size="sm"
                />
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </UCard>
  </div>
</template>

<style scoped>
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
}

.admin-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
}

.actions { display: flex; gap: 4px; }
.overflow-hidden { overflow: hidden; }
.space-y-4 > * + * { margin-top: 16px; }
.p-4 { padding: 16px; }
.font-mono { font-family: var(--font-mono); }
.text-xs { font-size: var(--text-xs); }
</style>
