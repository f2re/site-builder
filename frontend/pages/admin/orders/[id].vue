<script setup lang="ts">
import type { C2CShipmentResponse } from '~/composables/useC2CShipment'

definePageMeta({
  layout: false,
  middleware: 'auth',
})

interface OrderItem {
  product_name: string
  sku: string
  image_url?: string
  quantity: number
  price: number
}

interface TrackingEvent {
  provider: string
  status: string
  message: string
  timestamp: string
}

interface OrderRead {
  id: string
  user_id: string
  user_full_name: string
  user_email: string
  user_phone: string
  items: OrderItem[]
  tracking_events: TrackingEvent[]
  tracking_number?: string
  tracking_url?: string
  delivery_status?: string
  delivery_provider?: string
  payment_id?: string
  paid_at?: string
  status: string
  total_amount: number
  created_at: string
  shipping_address?: string
}

const route = useRoute()
const toast = useToast()
const orderId = route.params.id as string
const apiFetch = useApiFetch()

const { data: order, pending, refresh, error } = await useApi<OrderRead>(`/admin/orders/${orderId}`)

const isC2CProvider = computed(() =>
  order.value?.delivery_provider === 'ozon' || order.value?.delivery_provider === 'wb'
)

const { data: c2cData, pending: c2cPending, error: c2cError } = isC2CProvider.value
  ? await useC2CShipment(orderId)
  : { data: ref(null), pending: ref(false), error: ref(null) }

const statusOptions = [
  { label: 'Новый', value: 'pending' },
  { label: 'Ожидает оплаты', value: 'awaiting_payment' },
  { label: 'Оплачен', value: 'paid' },
  { label: 'Отправлен', value: 'shipped' },
  { label: 'Доставлен', value: 'delivered' },
  { label: 'Отменен', value: 'cancelled' },
]

const updatingStatus = ref(false)

async function updateStatus(newStatus: string) {
  updatingStatus.value = true
  try {
    await apiFetch(`/admin/orders/${orderId}/status`, {
      method: 'PUT',
      body: { new_status: newStatus },
    })
    toast.success('Статус заказа обновлен')
    await refresh()
  } catch (e: any) {
    toast.error(e.data?.message || 'Ошибка при обновлении статуса')
  } finally {
    updatingStatus.value = false
  }
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

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusLabel = (status: string) => {
  return statusOptions.find(opt => opt.value === status)?.label || status
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>
      <div class="flex items-center gap-4">
        <NuxtLink to="/admin/orders" class="text-muted hover:text-accent transition-colors" data-testid="back-to-orders">
          <UIcon name="i-heroicons-arrow-left" class="w-6 h-6" />
        </NuxtLink>
        <span>Заказ #{{ orderId.slice(0, 8) }}</span>
      </div>
    </template>

    <div class="admin-order-view p-4 lg:p-8" data-testid="admin-order-detail">
      <div v-if="pending" class="space-y-6">
        <div class="flex justify-between items-center">
          <USkeleton class="h-10 w-48" />
          <USkeleton class="h-10 w-32" />
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 space-y-6">
            <USkeleton class="h-64 w-full" />
            <USkeleton class="h-48 w-full" />
          </div>
          <div class="space-y-6">
            <USkeleton class="h-40 w-full" />
            <USkeleton class="h-40 w-full" />
            <USkeleton class="h-40 w-full" />
          </div>
        </div>
      </div>

      <div v-else-if="error" class="text-center py-20">
        <p class="text-error text-lg">Ошибка при загрузке заказа</p>
        <UButton class="mt-4" @click="refresh">Попробовать снова</UButton>
      </div>

      <div v-else-if="order" class="space-y-6">
        <!-- Header Actions -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-surface p-4 rounded-lg border border-border">
          <div class="flex flex-col">
            <div class="flex items-center gap-3">
              <h1 class="text-xl font-bold">Заказ #{{ order.id }}</h1>
              <OrdersStatusBadge :status="order.status" data-testid="order-status-badge" />
            </div>
            <p class="text-sm text-muted">Создан: {{ formatDate(order.created_at) }}</p>
          </div>
          
          <div class="flex items-center gap-2">
            <USelectMenu
              v-model="order.status"
              :options="statusOptions"
              value-attribute="value"
              option-attribute="label"
              data-testid="change-status-select"
              class="w-48"
              @update:model-value="updateStatus"
            >
              <template #default="{ open }">
                <UButton
                  color="white"
                  variant="solid"
                  :loading="updatingStatus"
                  data-testid="change-status-btn"
                >
                  {{ getStatusLabel(order.status) }}
                  <UIcon name="i-heroicons-chevron-down" class="ml-auto w-4 h-4 transition-transform" :class="{ 'rotate-180': open }" />
                </UButton>
              </template>
            </USelectMenu>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Main Content -->
          <div class="lg:col-span-2 space-y-6">
            <!-- Items Card -->
            <UCard data-testid="items-card" :ui="{ body: { padding: 'p-0' } }">
              <template #header>
                <div class="flex items-center gap-2">
                  <UIcon name="i-heroicons-shopping-cart" class="text-accent" />
                  <h3 class="font-semibold">Состав заказа</h3>
                </div>
              </template>
              
              <div class="overflow-x-auto">
                <table class="w-full text-sm text-left">
                  <thead class="text-xs uppercase bg-bg-subtle text-muted">
                    <tr>
                      <th class="px-4 py-3">Товар</th>
                      <th class="px-4 py-3">SKU</th>
                      <th class="px-4 py-3">Цена</th>
                      <th class="px-4 py-3 text-center">Кол-во</th>
                      <th class="px-4 py-3 text-right">Итого</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-border">
                    <tr v-for="item in order.items" :key="item.sku" class="hover:bg-bg-subtle/50 transition-colors">
                      <td class="px-4 py-4">
                        <div class="flex items-center gap-3">
                          <img 
                            v-if="item.image_url" 
                            :src="item.image_url" 
                            class="w-12 h-12 rounded object-cover border border-border"
                            alt=""
                          >
                          <div v-else class="w-12 h-12 rounded bg-surface-2 flex items-center justify-center border border-border">
                            <UIcon name="i-heroicons-photo" class="text-muted w-6 h-6" />
                          </div>
                          <span class="font-medium">{{ item.product_name }}</span>
                        </div>
                      </td>
                      <td class="px-4 py-4 text-muted font-mono">{{ item.sku }}</td>
                      <td class="px-4 py-4 whitespace-nowrap">{{ item.price }} ₽</td>
                      <td class="px-4 py-4 text-center">{{ item.quantity }}</td>
                      <td class="px-4 py-4 text-right font-semibold whitespace-nowrap">{{ item.price * item.quantity }} ₽</td>
                    </tr>
                  </tbody>
                  <tfoot class="bg-bg-subtle/30 font-bold text-base">
                    <tr>
                      <td colspan="4" class="px-4 py-4 text-right">Общая стоимость:</td>
                      <td class="px-4 py-4 text-right text-accent whitespace-nowrap" data-testid="order-total">{{ order.total_amount }} ₽</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </UCard>

            <!-- Timeline Section -->
            <UCard data-testid="timeline-card">
              <template #header>
                <div class="flex items-center gap-2">
                  <UIcon name="i-heroicons-clock" class="text-accent" />
                  <h3 class="font-semibold">История перемещений</h3>
                </div>
              </template>

              <div v-if="order.tracking_events && order.tracking_events.length > 0" class="relative pl-8 space-y-8 before:absolute before:inset-0 before:left-[11px] before:w-0.5 before:bg-border">
                <div v-for="(event, idx) in order.tracking_events" :key="idx" class="relative">
                  <div class="absolute -left-[27px] mt-1.5 w-4 h-4 rounded-full bg-surface border-2 border-accent shadow-[0_0_8px_var(--color-accent-glow)]"></div>
                  <div class="flex flex-col">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="text-xs text-muted">{{ formatDate(event.timestamp) }}</span>
                      <UBadge size="xs" variant="subtle" color="gray">{{ event.provider }}</UBadge>
                    </div>
                    <p class="font-semibold text-sm">{{ event.status }}</p>
                    <p class="text-sm text-muted">{{ event.message }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-8 text-muted italic">
                История перемещений пока пуста
              </div>
            </UCard>
          </div>

          <!-- Sidebar content -->
          <div class="space-y-6">
            <!-- Customer Card -->
            <UCard data-testid="customer-card">
              <template #header>
                <div class="flex items-center gap-2">
                  <UIcon name="i-heroicons-user" class="text-accent" />
                  <h3 class="font-semibold">Покупатель</h3>
                </div>
              </template>
              <div class="space-y-3">
                <NuxtLink :to="`/admin/users/${order.user_id}`" class="block font-bold hover:text-accent transition-colors" data-testid="customer-link">
                  {{ order.user_full_name }}
                </NuxtLink>
                <div class="flex items-center gap-2 text-sm">
                  <UIcon name="i-heroicons-envelope" class="text-muted" />
                  <a :href="`mailto:${order.user_email}`" class="hover:underline" data-testid="customer-email">{{ order.user_email }}</a>
                </div>
                <div class="flex items-center gap-2 text-sm">
                  <UIcon name="i-heroicons-phone" class="text-muted" />
                  <a :href="`tel:${order.user_phone}`" class="hover:underline" data-testid="customer-phone">{{ order.user_phone }}</a>
                </div>
              </div>
            </UCard>

            <!-- Shipping Card -->
            <UCard data-testid="shipping-card">
              <template #header>
                <div class="flex items-center gap-2">
                  <UIcon name="i-heroicons-truck" class="text-accent" />
                  <h3 class="font-semibold">Доставка</h3>
                </div>
              </template>
              <div class="space-y-4">
                <div>
                  <label class="text-xs uppercase text-muted font-bold">Адрес</label>
                  <p class="text-sm mt-1" data-testid="shipping-address">{{ order.shipping_address || 'Не указан' }}</p>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="text-xs uppercase text-muted font-bold">Провайдер</label>
                    <p class="text-sm mt-1 uppercase" data-testid="delivery-provider">{{ order.delivery_provider || '—' }}</p>
                  </div>
                  <div>
                    <label class="text-xs uppercase text-muted font-bold">Статус</label>
                    <p class="text-sm mt-1" data-testid="delivery-status">{{ order.delivery_status || '—' }}</p>
                  </div>
                </div>
                <div v-if="order.tracking_number">
                  <label class="text-xs uppercase text-muted font-bold">Трек-номер</label>
                  <div class="flex items-center gap-2 mt-1">
                    <span class="text-sm font-mono" data-testid="tracking-number">{{ order.tracking_number }}</span>
                    <UButton 
                      v-if="order.tracking_url" 
                      :to="order.tracking_url" 
                      target="_blank" 
                      icon="i-heroicons-arrow-top-right-on-square" 
                      size="xs" 
                      variant="ghost" 
                      color="gray"
                      data-testid="tracking-url"
                    />
                  </div>
                </div>
              </div>
            </UCard>

            <!-- C2C Card (Integrated) -->
            <UCard
              v-if="isC2CProvider && !c2cPending && !c2cError && c2cData"
              data-testid="c2c-shipment-card"
              class="border-neon/30 bg-neon/5"
            >
              <template #header>
                <div class="flex items-center gap-2">
                  <UIcon name="i-heroicons-information-circle" class="text-neon" />
                  <h3 class="font-semibold text-neon">Инфо для отправки {{ providerLabel }}</h3>
                </div>
              </template>
              
              <div class="space-y-4 text-sm">
                <div class="space-y-1">
                  <p><span class="text-muted">Получатель:</span> {{ c2cData.recipient_name }}</p>
                  <p><span class="text-muted">Телефон:</span> {{ c2cData.recipient_phone }}</p>
                  <p><span class="text-muted">ПВЗ:</span> {{ c2cData.pvz_code }} — {{ c2cData.pvz_address }}</p>
                  <p><span class="text-muted">Ценность:</span> {{ c2cData.declared_value }} ₽</p>
                  <p><span class="text-muted">Вес:</span> {{ c2cData.weight_kg }} кг</p>
                </div>

                <div class="bg-surface p-3 rounded border border-border">
                  <h4 class="font-bold mb-2 text-xs uppercase">Инструкция</h4>
                  <ol class="list-decimal list-inside space-y-1 text-xs text-muted">
                    <li v-for="(step, idx) in c2cData.instructions" :key="idx">{{ step }}</li>
                  </ol>
                </div>

                <div class="flex flex-col gap-2">
                  <UButton
                    data-testid="c2c-open-app-btn"
                    block
                    color="primary"
                    variant="solid"
                    @click="openDeeplink"
                  >
                    Открыть в приложении
                  </UButton>
                  <UButton
                    data-testid="c2c-copy-btn"
                    block
                    color="white"
                    variant="solid"
                    @click="copyC2CData"
                  >
                    Копировать данные
                  </UButton>
                </div>
              </div>
            </UCard>

            <!-- Payment Card -->
            <UCard data-testid="payment-card">
              <template #header>
                <div class="flex items-center gap-2">
                  <UIcon name="i-heroicons-credit-card" class="text-accent" />
                  <h3 class="font-semibold">Оплата</h3>
                </div>
              </template>
              <div class="space-y-4">
                <div>
                  <label class="text-xs uppercase text-muted font-bold">Статус</label>
                  <div class="mt-1">
                    <UBadge 
                      :color="order.paid_at ? 'success' : 'warning'" 
                      variant="subtle"
                      data-testid="payment-status-badge"
                    >
                      {{ order.paid_at ? 'Оплачено' : 'Ожидает оплаты' }}
                    </UBadge>
                  </div>
                </div>
                <div v-if="order.payment_id">
                  <label class="text-xs uppercase text-muted font-bold">Payment ID</label>
                  <p class="text-sm font-mono mt-1" data-testid="payment-id">{{ order.payment_id }}</p>
                </div>
                <div v-if="order.paid_at">
                  <label class="text-xs uppercase text-muted font-bold">Дата оплаты</label>
                  <p class="text-sm mt-1" data-testid="paid-at">{{ formatDate(order.paid_at) }}</p>
                </div>
              </div>
            </UCard>
          </div>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<style scoped>
.admin-order-view {
  min-height: 100vh;
  background-color: var(--color-bg);
  color: var(--color-text);
}

:deep(.u-card) {
  background-color: var(--color-surface);
  border-color: var(--color-border);
}

:deep(.u-card-header) {
  border-bottom-color: var(--color-border);
}

.text-muted {
  color: var(--color-text-2);
}

.text-accent {
  color: var(--color-accent);
}

.text-neon {
  color: var(--color-neon);
}

.bg-surface {
  background-color: var(--color-surface);
}

.bg-bg-subtle {
  background-color: var(--color-bg-subtle);
}

.border-border {
  border-color: var(--color-border);
}

.border-neon\/30 {
  border-color: color-mix(in srgb, var(--color-neon) 30%, transparent);
}

.bg-neon\/5 {
  background-color: color-mix(in srgb, var(--color-neon) 5%, transparent);
}
</style>
