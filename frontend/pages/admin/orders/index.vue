<script setup lang="ts">
import UCard from '~/components/U/UCard.vue'
import UBadge from '~/components/U/UBadge.vue'
import USkeleton from '~/components/U/USkeleton.vue'
import USelect from '~/components/U/USelect.vue'
import UButton from '~/components/U/UButton.vue'
import UInput from '~/components/U/UInput.vue'

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const route = useRoute()
const router = useRouter()
const toast = useToast()

// Reactive filters from URL
const page = ref(Number(route.query.page) || 1)
const perPage = ref(20)
const statusFilter = ref<string | undefined>(route.query.status as string)
const dateFilter = ref<string>(route.query.date as string || 'all')
const searchQuery = ref(route.query.search as string || '')
const includeArchived = ref(route.query.archived === 'true')

// Debounced search
const debouncedSearch = ref(searchQuery.value)
let searchTimeout: any = null

watch(searchQuery, (val) => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    debouncedSearch.value = val
    page.value = 1 // Reset to first page on search
  }, 400)
})

// Computed query params
const queryParams = computed(() => ({
  page: page.value,
  per_page: perPage.value,
  ...(statusFilter.value && { status: statusFilter.value }),
  ...(dateFilter.value !== 'all' && { date: dateFilter.value }),
  ...(debouncedSearch.value && { search: debouncedSearch.value }),
  include_archived: includeArchived.value,
}))

const { data: orders, pending, refresh } = await useApi<any>('/admin/orders', {
  query: queryParams,
})

const apiFetch = useApiFetch()

// Update URL when filters change
watch([page, statusFilter, dateFilter, debouncedSearch, includeArchived], () => {
  router.push({
    query: {
      ...(page.value > 1 && { page: page.value }),
      ...(statusFilter.value && { status: statusFilter.value }),
      ...(dateFilter.value !== 'all' && { date: dateFilter.value }),
      ...(debouncedSearch.value && { search: debouncedSearch.value }),
      ...(includeArchived.value && { archived: 'true' }),
    },
  })
})

const statusMap = {
  pending: { label: 'Новый', variant: 'warning' },
  awaiting_payment: { label: 'Ожидает оплаты', variant: 'info' },
  paid: { label: 'Оплачен', variant: 'success' },
  shipped: { label: 'Отправлен', variant: 'info' },
  delivered: { label: 'Доставлен', variant: 'success' },
  cancelled: { label: 'Отменен', variant: 'error' },
}

const statusOptions = [
  { value: '', label: 'Все статусы' },
  ...Object.keys(statusMap).map(s => ({
    value: s,
    label: statusMap[s as keyof typeof statusMap].label
  }))
]

const dateFilterOptions = [
  { value: 'all', label: 'Все время' },
  { value: 'today', label: 'Сегодня' },
  { value: 'week', label: 'Эта неделя' },
  { value: 'month', label: 'Этот месяц' },
]

async function updateStatus(orderId: string, status: string) {
  try {
    await apiFetch(`/admin/orders/${orderId}/status`, {
      method: 'PUT',
      body: { new_status: status },
    })
    toast.success('Статус обновлен')
    await refresh()
  } catch (e: any) {
    toast.error(e.data?.message || 'Ошибка обновления статуса')
  }
}

async function archiveOrder(orderId: string) {
  if (!confirm('Архивировать заказ? Он перестанет отображаться в общем списке.')) return
  try {
    await apiFetch(`/admin/orders/${orderId}/archive`, {
      method: 'POST',
    })
    toast.success('Заказ архивирован')
    await refresh()
  } catch (e: any) {
    toast.error(e.data?.message || 'Ошибка архивации')
  }
}

function nextPage() {
  if (orders.value?.items?.length === perPage.value) {
    page.value++
  }
}

function prevPage() {
  if (page.value > 1) {
    page.value--
  }
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Заказы</template>
    <template #header-actions>
      <div class="flex items-center gap-2 text-sm text-muted">
        <input type="checkbox" id="inc-archived" v-model="includeArchived" class="rounded border-border text-accent focus:ring-accent" />
        <label for="inc-archived">Показать архивные</label>
      </div>
    </template>

    <div class="admin-orders-page">
      <UCard class="filters-card">
        <div class="filters">
          <UInput
            v-model="searchQuery"
            placeholder="Поиск (ID, Email, Тел, Трек)"
            icon="ph:magnifying-glass-bold"
            data-testid="order-search"
          />
          <USelect
            v-model="statusFilter"
            :options="statusOptions"
            placeholder="Статус"
            data-testid="order-status-filter"
          />
          <USelect
            v-model="dateFilter"
            :options="dateFilterOptions"
            data-testid="order-date-filter"
          />
        </div>
      </UCard>

      <div class="results-info text-sm text-muted px-1" v-if="orders?.total !== undefined">
        Найдено заказов: <strong>{{ orders.total }}</strong>
      </div>

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
            <tr v-for="order in orders?.items" :key="order.id" data-testid="order-card" :class="{ 'opacity-60 grayscale-[0.5]': order.is_archived }">
              <td>
                <div class="order-info">
                  <div class="flex items-center gap-2">
                    <NuxtLink :to="`/admin/orders/${order.id}`" data-testid="order-detail-link" class="order-id font-mono truncate">
                      #{{ order.id.slice(0, 8) }}
                    </NuxtLink>
                    <UIcon v-if="order.is_archived" name="ph:archive-bold" class="text-muted w-4 h-4" title="Архивирован" />
                  </div>
                  <div class="order-meta">
                    <span class="price mobile-only">{{ order.total_amount || order.total_rub }} ₽</span>
                    <span class="email truncate" v-if="order.user_email">{{ order.user_email }}</span>
                  </div>
                </div>
              </td>
              <td class="desktop-only">
                <span class="price-desktop">{{ order.total_amount || order.total_rub }} ₽</span>
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
                    :options="statusOptions.slice(1)"
                    size="sm"
                    class="status-select"
                  />
                  <UButton
                    v-if="!order.is_archived"
                    icon="ph:archive-bold"
                    variant="ghost"
                    color="gray"
                    size="sm"
                    @click="archiveOrder(order.id)"
                    title="В архив"
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

    <div v-if="orders?.items?.length" class="pagination">
      <UButton
        variant="secondary"
        :disabled="page === 1"
        @click="prevPage"
        data-testid="orders-prev-page"
      >
        Назад
      </UButton>
      <span class="page-info">Страница {{ page }}</span>
      <UButton
        variant="secondary"
        :disabled="orders?.items?.length < perPage"
        @click="nextPage"
        data-testid="orders-next-page"
      >
        Вперёд
      </UButton>
    </div>
  </div>
  </NuxtLayout>
</template>

<style scoped>
.admin-orders-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filters-card {
  padding: 16px;
}

.filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filters > * {
  flex: 1;
  min-width: 200px;
}

.table-card {
  overflow: hidden;
}

.table-card :deep(.card__body) {
  padding: 0;
}

.admin-table {
  table-layout: fixed;
}

.admin-table th:nth-child(1),
.admin-table td:nth-child(1) {
  width: auto;
}

@media (min-width: 768px) {
  .admin-table th:nth-child(1),
  .admin-table td:nth-child(1) {
    width: 30%;
  }
  .admin-table th.desktop-only,
  .admin-table td.desktop-only {
    width: 20%;
  }
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-id {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.order-id:hover {
  color: var(--color-accent);
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

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.page-info {
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.font-mono { font-family: var(--font-mono); }
.p-4 { padding: 16px; }
.space-y-4 > * + * { margin-top: 16px; }
</style>
