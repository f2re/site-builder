<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUser } from '~/composables/useUser'
import UButton from '~/components/U/UButton.vue'
import UCard from '~/components/U/UCard.vue'
import UBadge from '~/components/U/UBadge.vue'
import USkeleton from '~/components/U/USkeleton.vue'

definePageMeta({
  layout: false,
  middleware: 'auth',
})

const route = useRoute()
const userId = route.params.id as string
const { adminGetUserFull } = useUser()

const { data: user, pending, error, refresh } = await adminGetUserFull(userId)

const activeTab = ref('general')
const tabs = [
  { id: 'general', label: 'Общая информация', icon: 'ph:user-bold' },
  { id: 'security', label: 'Безопасность', icon: 'ph:shield-check-bold' },
  { id: 'addresses', label: 'Адреса', icon: 'ph:map-pin-bold' },
  { id: 'orders', label: 'Заказы', icon: 'ph:shopping-cart-bold' },
  { id: 'devices', label: 'Устройства', icon: 'ph:cpu-bold' }
]

const formatDate = (dateString?: string | null) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>
      <div class="flex items-center gap-2">
        <UButton 
          variant="ghost" 
          to="/admin/users" 
          size="sm" 
          aria-label="Назад" 
          data-testid="back-btn" 
          class="p-1 -ml-2"
        >
          <template #icon><Icon name="ph:caret-left-bold" size="20" /></template>
        </UButton>
        <span class="text-muted mr-1">Пользователь:</span>
        <h1 class="font-semibold text-lg truncate max-w-[200px] md:max-w-[400px]">
          {{ user?.full_name || user?.email || 'Загрузка...' }}
        </h1>
        <UBadge 
          v-if="user" 
          :variant="user.is_active ? 'success' : 'error'" 
          size="sm" 
          class="ml-2" 
          data-testid="user-status-badge"
        >
          {{ user.is_active ? 'Активен' : 'Заблокирован' }}
        </UBadge>
      </div>
    </template>

    <template #header-actions>
      <div v-if="user" class="flex gap-2">
        <UButton variant="outline" size="sm" data-testid="edit-btn">
          <template #icon><Icon name="ph:pencil-simple-bold" /></template>
          <span class="hidden sm:inline">Редактировать</span>
        </UButton>
        <UButton variant="error" size="sm" data-testid="delete-btn">
          <template #icon><Icon name="ph:trash-bold" /></template>
          <span class="hidden sm:inline">Удалить</span>
        </UButton>
      </div>
    </template>

    <div v-if="pending" class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-4 space-y-6">
          <USkeleton height="300px" />
          <USkeleton height="200px" />
        </div>
        <div class="lg:col-span-8">
          <USkeleton height="600px" />
        </div>
      </div>
    </div>

    <div v-else-if="error" class="flex flex-col items-center justify-center py-12">
      <UCard class="max-w-md w-full text-center p-8">
        <Icon name="ph:warning-duotone" size="64" class="text-error mb-4 mx-auto" />
        <h2 class="text-xl font-bold mb-2">Ошибка загрузки</h2>
        <p class="text-muted mb-6">Не удалось получить данные пользователя.</p>
        <UButton variant="primary" @click="refresh">Повторить попытку</UButton>
      </UCard>
    </div>

    <div v-else-if="user" class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        <!-- Sidebar Panel -->
        <div class="lg:col-span-4 space-y-6">
          <!-- Profile Card -->
          <UCard>
            <div class="flex flex-col items-center text-center py-4">
              <div class="w-24 h-24 rounded-full bg-surface-2 flex items-center justify-center mb-4 text-muted overflow-hidden border border-border">
                <Icon name="ph:user-circle-fill" size="96" />
              </div>
              <h2 class="text-xl font-bold truncate w-full px-2 text-text">
                {{ user.full_name || 'Без имени' }}
              </h2>
              <p class="text-muted text-sm truncate w-full px-2 mb-4">{{ user.email }}</p>
              
              <div class="flex flex-wrap justify-center gap-2">
                <UBadge variant="accent" data-testid="user-role">{{ user.role }}</UBadge>
                <UBadge :variant="user.is_verified ? 'success' : 'warning'">
                  {{ user.is_verified ? 'Верифицирован' : 'Не верифицирован' }}
                </UBadge>
              </div>
            </div>
            
            <div class="mt-6 pt-6 border-t border-border space-y-4">
              <div class="flex justify-between items-center text-sm">
                <span class="text-muted">ID:</span>
                <span class="font-mono text-xs select-all text-text" data-testid="user-id">{{ user.id }}</span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-muted">Регистрация:</span>
                <span class="text-text">{{ formatDate(user.created_at) }}</span>
              </div>
            </div>
          </UCard>

          <!-- Last Session Info -->
          <UCard>
            <template #header>
              <div class="flex items-center gap-2 font-semibold text-sm">
                <Icon name="ph:activity-bold" class="text-accent" />
                <span class="text-text">Последняя активность</span>
              </div>
            </template>
            <div class="space-y-4">
              <div>
                <span class="block text-xs text-muted uppercase mb-1">Дата и время</span>
                <span class="font-medium text-sm text-text">{{ formatDate(user.last_login_at) }}</span>
              </div>
              <div>
                <span class="block text-xs text-muted uppercase mb-1">IP адрес</span>
                <span class="font-mono text-sm text-text">{{ user.last_login_ip || '—' }}</span>
              </div>
              <div>
                <span class="block text-xs text-muted uppercase mb-1">Устройство</span>
                <p class="text-xs text-muted leading-tight break-all bg-surface-2 p-2 rounded mt-1 border border-border">
                  {{ user.last_login_device || 'Нет данных' }}
                </p>
              </div>
            </div>
          </UCard>
        </div>

        <!-- Main Content Area -->
        <div class="lg:col-span-8">
          <UCard class="p-0 overflow-hidden">
            <!-- Tabs Navigation -->
            <div class="flex overflow-x-auto border-b border-border hide-scrollbar sticky top-0 bg-surface z-10">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="activeTab = tab.id"
                class="flex items-center gap-2 px-6 py-4 text-sm font-medium whitespace-nowrap border-b-2 transition-colors duration-200"
                :class="activeTab === tab.id 
                  ? 'border-accent text-accent' 
                  : 'border-transparent text-muted hover:text-text hover:bg-surface-2'"
                :data-testid="`tab-btn-${tab.id}`"
              >
                <Icon :name="tab.icon" size="18" />
                <span>{{ tab.label }}</span>
              </button>
            </div>

            <!-- Tab Content -->
            <div class="p-6 md:p-8">
              
              <!-- General Section -->
              <div v-if="activeTab === 'general'" class="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div>
                  <h3 class="text-lg font-semibold mb-4 flex items-center gap-2 text-text">
                    <Icon name="ph:user-bold" class="text-accent" />
                    Личные данные
                  </h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-surface-2 p-4 rounded-lg border border-border">
                      <span class="block text-xs text-muted uppercase mb-1">ФИО</span>
                      <span class="font-medium text-text">{{ user.full_name || '—' }}</span>
                    </div>
                    <div class="bg-surface-2 p-4 rounded-lg border border-border">
                      <span class="block text-xs text-muted uppercase mb-1">Email (Логин)</span>
                      <span class="font-medium font-mono text-text">{{ user.email }}</span>
                    </div>
                    <div class="bg-surface-2 p-4 rounded-lg border border-border">
                      <span class="block text-xs text-muted uppercase mb-1">Телефон</span>
                      <span class="font-medium text-text">{{ user.phone || '—' }}</span>
                    </div>
                    <div class="bg-surface-2 p-4 rounded-lg border border-border">
                      <span class="block text-xs text-muted uppercase mb-1">Роль</span>
                      <span class="font-medium uppercase text-text">{{ user.role }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Security Section -->
              <div v-if="activeTab === 'security'" class="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div>
                  <h3 class="text-lg font-semibold mb-4 flex items-center gap-2 text-warning">
                    <Icon name="ph:shield-check-bold" />
                    Параметры безопасности
                  </h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-surface-2 p-4 rounded-lg border border-border">
                      <span class="block text-xs text-muted uppercase mb-1">Последний вход</span>
                      <span class="font-medium text-text">{{ formatDate(user.last_login_at) }}</span>
                    </div>
                    <div class="bg-surface-2 p-4 rounded-lg border border-border">
                      <span class="block text-xs text-muted uppercase mb-1">IP-адрес входа</span>
                      <span class="font-medium font-mono text-text">{{ user.last_login_ip || '—' }}</span>
                    </div>
                    <div class="bg-surface-2 p-4 rounded-lg border border-border md:col-span-2">
                      <span class="block text-xs text-muted uppercase mb-1">Сигнатура устройства (User Agent)</span>
                      <p class="text-xs font-mono text-muted mt-2 bg-bg p-3 rounded border border-border break-all">
                        {{ user.last_login_device || 'Нет данных' }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Addresses Section -->
              <div v-if="activeTab === 'addresses'" class="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div class="flex justify-between items-center">
                  <h3 class="text-lg font-semibold flex items-center gap-2 text-text">
                    <Icon name="ph:map-pin-bold" class="text-info" />
                    Адреса доставки
                  </h3>
                </div>

                <div v-if="!user.addresses || user.addresses.length === 0" class="flex flex-col items-center justify-center py-12 text-muted border-2 border-dashed border-border rounded-xl">
                  <Icon name="ph:map-pin-light" size="48" class="mb-2 opacity-50" />
                  <p>Адреса не добавлены</p>
                </div>

                <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-for="addr in user.addresses" :key="addr.id" class="p-4 rounded-lg border border-border bg-surface-2 hover:border-info transition-colors">
                    <div class="flex justify-between items-start mb-2">
                      <span class="font-bold text-sm uppercase text-text">{{ addr.city }}</span>
                      <UBadge v-if="addr.is_default" variant="success" size="sm">Основной</UBadge>
                    </div>
                    <p class="text-sm text-text-2 mb-4">{{ addr.address }}</p>
                    <div class="text-[10px] text-muted font-mono">Добавлен: {{ formatDate(addr.created_at) }}</div>
                  </div>
                </div>
              </div>

              <!-- Orders Section -->
              <div v-if="activeTab === 'orders'" class="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <h3 class="text-lg font-semibold flex items-center gap-2 text-text">
                  <Icon name="ph:shopping-cart-bold" class="text-primary" />
                  История заказов
                </h3>

                <div v-if="!user.orders || user.orders.length === 0" class="flex flex-col items-center justify-center py-12 text-muted border-2 border-dashed border-border rounded-xl">
                  <Icon name="ph:receipt-light" size="48" class="mb-2 opacity-50" />
                  <p>История заказов пуста</p>
                </div>

                <div v-else class="overflow-x-auto -mx-6 md:-mx-8">
                  <table class="w-full text-left border-collapse">
                    <thead>
                      <tr class="bg-surface-2 border-y border-border">
                        <th class="px-6 py-3 text-xs font-bold uppercase text-muted tracking-wider">Заказ</th>
                        <th class="px-6 py-3 text-xs font-bold uppercase text-muted tracking-wider">Дата</th>
                        <th class="px-6 py-3 text-xs font-bold uppercase text-muted tracking-wider">Статус</th>
                        <th class="px-6 py-3 text-xs font-bold uppercase text-muted tracking-wider text-right">Сумма</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-border">
                      <tr 
                        v-for="order in user.orders" 
                        :key="order.id" 
                        class="hover:bg-surface-2/50 transition-colors" 
                        :data-testid="`order-row-${order.id}`"
                      >
                        <td class="px-6 py-4 font-mono text-sm text-accent">{{ order.id.split('-')[0] }}</td>
                        <td class="px-6 py-4 text-sm text-text-2">{{ formatDate(order.created_at) }}</td>
                        <td class="px-6 py-4">
                          <UBadge variant="outline" size="sm">{{ order.status }}</UBadge>
                        </td>
                        <td class="px-6 py-4 text-sm font-bold text-right text-text">
                          {{ order.total_amount }} {{ order.currency }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Devices Section -->
              <div v-if="activeTab === 'devices'" class="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div class="flex justify-between items-center">
                  <h3 class="text-lg font-semibold flex items-center gap-2 text-text">
                    <Icon name="ph:cpu-bold" class="text-success" />
                    IoT Устройства
                  </h3>
                </div>

                <div v-if="!user.devices || user.devices.length === 0" class="flex flex-col items-center justify-center py-12 text-muted border-2 border-dashed border-border rounded-xl">
                  <Icon name="ph:cpu-light" size="48" class="mb-2 opacity-50" />
                  <p>Устройства не подключены</p>
                </div>

                <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div 
                    v-for="dev in user.devices" 
                    :key="dev.id" 
                    class="relative overflow-hidden p-5 rounded-lg border border-border bg-surface-2" 
                    :data-testid="`device-card-${dev.id}`"
                  >
                    <div class="absolute top-0 left-0 bottom-0 w-1" :class="dev.is_online ? 'bg-success' : 'bg-muted'"></div>
                    
                    <div class="flex items-center gap-4 mb-4">
                      <div class="w-12 h-12 rounded-lg flex items-center justify-center" :class="dev.is_online ? 'bg-success/10 text-success' : 'bg-muted/10 text-muted'">
                        <Icon name="ph:circuitry-bold" size="28" />
                      </div>
                      <div class="flex-1 min-w-0">
                        <h4 class="font-bold text-sm truncate text-text">{{ dev.name || 'Безымянный модуль' }}</h4>
                        <p class="text-xs text-muted font-mono truncate">{{ dev.device_id }}</p>
                      </div>
                      <UBadge :variant="dev.is_online ? 'success' : 'ghost'" size="sm">
                        {{ dev.is_online ? 'Онлайн' : 'Оффлайн' }}
                      </UBadge>
                    </div>
                    
                    <div class="flex justify-between items-center text-[10px] text-muted font-mono bg-bg/50 p-2 rounded border border-border/50">
                      <span>ПОСЛЕДНЯЯ АКТИВНОСТЬ:</span>
                      <span :class="{'text-success': dev.is_online}">{{ formatDate(dev.last_activity) }}</span>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </UCard>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<style scoped>
.hide-scrollbar::-webkit-scrollbar { display: none; }
.hide-scrollbar { scrollbar-width: none; }

.animate-in {
  animation-duration: 0.3s;
  animation-fill-mode: both;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInFromBottom {
  from { transform: translateY(10px); }
  to { transform: translateY(0); }
}

.fade-in { animation-name: fadeIn; }
.slide-in-from-bottom-2 { animation-name: slideInFromBottom; }
</style>
