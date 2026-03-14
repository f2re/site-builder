<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUser, type AdminDeviceRead } from '~/composables/useUser'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import UButton from '~/components/U/UButton.vue'
import UCard from '~/components/U/UCard.vue'
import UBadge from '~/components/U/UBadge.vue'
import USkeleton from '~/components/U/USkeleton.vue'

definePageMeta({
  layout: false,
  middleware: 'auth',
})

const route = useRoute()
const toast = useToast()
const { confirm } = useConfirm()
const userId = route.params.id as string
const { adminGetUserFull, adminSetUserBlockStatus, adminGetUserDevices } = useUser()

const { data: user, pending, error, refresh } = await adminGetUserFull(userId)

const activeTab = ref('general')
const tabs = [
  { id: 'general', label: 'Общая информация', icon: 'ph:user-bold' },
  { id: 'security', label: 'Безопасность', icon: 'ph:shield-check-bold' },
  { id: 'addresses', label: 'Адреса', icon: 'ph:map-pin-bold' },
  { id: 'orders', label: 'Заказы', icon: 'ph:shopping-cart-bold' },
  { id: 'devices', label: 'Устройства', icon: 'ph:cpu-bold' }
]

// Devices tab — loaded via dedicated endpoint GET /admin/users/{id}/devices
const { data: devicesData, pending: devicesPending, refresh: refreshDevices } = await adminGetUserDevices(userId)
const userDevices = computed<AdminDeviceRead[]>(() => devicesData.value ?? [])

watch(activeTab, (tab) => {
  if (tab === 'devices') refreshDevices()
})

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

const userInitials = computed(() => {
  if (!user.value?.full_name) return user.value?.email?.charAt(0).toUpperCase() || '?'
  return user.value.full_name
    .split(' ')
    .filter(Boolean)
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const handleDeleteUser = async () => {
  const confirmed = await confirm({
    title: 'Удалить пользователя?',
    message: 'Это действие необратимо. Все данные пользователя будут удалены.',
    variant: 'danger',
    confirmLabel: 'Удалить',
    cancelLabel: 'Отмена'
  })
  
  if (confirmed) {
    toast.info('Функция удаления пользователя пока не реализована в API')
  }
}

const handleBlockStatus = async () => {
  if (!user.value) return
  const newStatus = !user.value.is_active
  try {
    await adminSetUserBlockStatus(userId, newStatus)
    toast.success(`Пользователь ${newStatus ? 'разблокирован' : 'заблокирован'}`)
    refresh()
  } catch (err: any) {
    toast.error(err.data?.message || 'Не удалось изменить статус')
  }
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
        <span class="text-muted mr-1 hidden sm:inline">Пользователь:</span>
        <h1 class="font-bold text-lg truncate max-w-[150px] sm:max-w-[300px] md:max-w-[400px]">
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
        <UButton 
          variant="outline" 
          size="sm" 
          :to="`/admin/users/${userId}/edit`" 
          data-testid="edit-btn"
        >
          <template #icon><Icon name="ph:pencil-simple-bold" /></template>
          <span class="hidden sm:inline">Редактировать</span>
        </UButton>
        <UButton 
          variant="error" 
          size="sm" 
          @click="handleDeleteUser" 
          data-testid="delete-btn"
        >
          <template #icon><Icon name="ph:trash-bold" /></template>
          <span class="hidden sm:inline">Удалить</span>
        </UButton>
      </div>
    </template>

    <div v-if="pending" class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-4 space-y-6">
          <USkeleton height="320px" />
          <USkeleton height="220px" />
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
        <aside class="lg:col-span-4 space-y-6">
          <!-- Profile Card -->
          <UCard>
            <div class="flex flex-col items-center text-center py-6">
              <div class="profile-avatar mb-4" data-testid="user-avatar">
                <span v-if="userInitials">{{ userInitials }}</span>
                <Icon v-else name="ph:user-circle-fill" size="96" />
              </div>
              <h2 class="text-xl font-bold truncate w-full px-2 text-text mb-1" data-testid="user-full-name">
                {{ user.full_name || 'Без имени' }}
              </h2>
              <p class="text-muted text-sm truncate w-full px-2 mb-6">{{ user.email }}</p>
              
              <div class="flex flex-wrap justify-center gap-2">
                <UBadge variant="accent" size="sm" data-testid="user-role-badge" class="uppercase font-bold tracking-wider">
                  {{ user.role }}
                </UBadge>
                <UBadge :variant="user.is_verified ? 'success' : 'warning'" size="sm">
                  {{ user.is_verified ? 'Верифицирован' : 'Не верифицирован' }}
                </UBadge>
              </div>
            </div>
            
            <div class="profile-stats border-t border-border pt-6 mt-2 space-y-3">
              <div class="flex justify-between items-center text-sm">
                <span class="text-muted">ID:</span>
                <span class="font-mono text-xs select-all text-text" data-testid="user-id">{{ user.id }}</span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-muted">Регистрация:</span>
                <span class="text-text">{{ formatDate(user.created_at) }}</span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-muted">Статус:</span>
                <button 
                  @click="handleBlockStatus"
                  class="text-xs font-bold transition-colors hover:opacity-80"
                  :class="user.is_active ? 'text-success' : 'text-error'"
                >
                  {{ user.is_active ? 'АКТИВЕН' : 'ЗАБЛОКИРОВАН' }}
                </button>
              </div>
            </div>
          </UCard>

          <!-- Last Activity Card -->
          <UCard>
            <template #header>
              <div class="flex items-center gap-2 font-bold text-sm uppercase tracking-wide">
                <Icon name="ph:activity-bold" class="text-accent" />
                <span class="text-text">Последняя активность</span>
              </div>
            </template>
            <div class="space-y-5">
              <div class="info-item">
                <label>Дата и время</label>
                <p>{{ formatDate(user.last_login_at) }}</p>
              </div>
              <div class="info-item">
                <label>IP адрес</label>
                <p class="font-mono">{{ user.last_login_ip || '—' }}</p>
              </div>
              <div class="info-item">
                <label>Устройство</label>
                <div class="user-agent-box">
                  {{ user.last_login_device || 'Нет данных' }}
                </div>
              </div>
            </div>
          </UCard>
        </aside>

        <!-- Main Content Area -->
        <main class="lg:col-span-8">
          <UCard class="p-0 overflow-hidden main-content-card">
            <!-- Tabs Navigation -->
            <div class="tabs-nav">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="activeTab = tab.id"
                class="tab-btn"
                :class="{ 'active': activeTab === tab.id }"
                :data-testid="`tab-btn-${tab.id}`"
              >
                <Icon :name="tab.icon" size="20" />
                <span>{{ tab.label }}</span>
                <div v-if="activeTab === tab.id" class="tab-indicator"></div>
              </button>
            </div>

            <!-- Tab Content -->
            <div class="tab-content p-6 sm:p-8">
              
              <!-- General Section -->
              <div v-if="activeTab === 'general'" class="section-fade-in">
                <div class="flex items-center justify-between mb-6">
                  <h3 class="text-lg font-bold flex items-center gap-2 text-text">
                    <Icon name="ph:user-bold" class="text-accent" />
                    Личные данные
                  </h3>
                </div>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div class="data-box">
                    <span class="data-label">ФИО</span>
                    <span class="data-value">{{ user.full_name || '—' }}</span>
                  </div>
                  <div class="data-box">
                    <span class="data-label">Email (Логин)</span>
                    <span class="data-value font-mono">{{ user.email }}</span>
                  </div>
                  <div class="data-box">
                    <span class="data-label">Телефон</span>
                    <span class="data-value">{{ user.phone || '—' }}</span>
                  </div>
                  <div class="data-box">
                    <span class="data-label">Роль в системе</span>
                    <span class="data-value uppercase text-accent font-bold">{{ user.role }}</span>
                  </div>
                </div>
              </div>

              <!-- Security Section -->
              <div v-if="activeTab === 'security'" class="section-fade-in">
                <h3 class="text-lg font-bold mb-6 flex items-center gap-2 text-text">
                  <Icon name="ph:shield-check-bold" class="text-warning" />
                  Безопасность
                </h3>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div class="data-box">
                    <span class="data-label">Последний вход</span>
                    <span class="data-value">{{ formatDate(user.last_login_at) }}</span>
                  </div>
                  <div class="data-box">
                    <span class="data-label">IP-адрес входа</span>
                    <span class="data-value font-mono">{{ user.last_login_ip || '—' }}</span>
                  </div>
                  <div class="data-box sm:col-span-2">
                    <span class="data-label">User Agent последнего входа</span>
                    <p class="ua-text mt-2">{{ user.last_login_device || 'Нет данных' }}</p>
                  </div>
                </div>
              </div>

              <!-- Addresses Section -->
              <div v-if="activeTab === 'addresses'" class="section-fade-in">
                <h3 class="text-lg font-bold mb-6 flex items-center gap-2 text-text">
                  <Icon name="ph:map-pin-bold" class="text-info" />
                  Адреса доставки
                </h3>

                <div v-if="!user.addresses || user.addresses.length === 0" class="empty-placeholder">
                  <Icon name="ph:map-pin-light" size="48" class="mb-2 opacity-30" />
                  <p>У пользователя пока нет сохраненных адресов</p>
                </div>

                <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div v-for="addr in user.addresses" :key="addr.id" class="address-card">
                    <div class="address-header">
                      <span class="city">{{ addr.city }}</span>
                      <UBadge v-if="addr.is_default" variant="success" size="sm">Основной</UBadge>
                    </div>
                    <p class="address-full">{{ addr.full_address }}</p>
                    <div class="mt-2 text-sm">
                      <p><span class="text-muted">Получатель:</span> {{ addr.recipient_name }}</p>
                      <p><span class="text-muted">Телефон:</span> {{ addr.recipient_phone }}</p>
                      <p><span class="text-muted">Тип:</span> {{ addr.address_type }} ({{ addr.provider }})</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Orders Section -->
              <div v-if="activeTab === 'orders'" class="section-fade-in">
                <h3 class="text-lg font-bold mb-6 flex items-center gap-2 text-text">
                  <Icon name="ph:shopping-cart-bold" class="text-primary" />
                  История заказов
                </h3>

                <div v-if="!user.orders || user.orders.length === 0" class="empty-placeholder">
                  <Icon name="ph:receipt-light" size="48" class="mb-2 opacity-30" />
                  <p>История заказов пуста</p>
                </div>

                <div v-else class="admin-table-wrapper">
                  <table class="admin-table">
                    <thead>
                      <tr>
                        <th>Заказ</th>
                        <th>Дата</th>
                        <th>Статус</th>
                        <th class="text-right">Сумма</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="order in user.orders" :key="order.id" :data-testid="`order-row-${order.id}`">
                        <td class="font-mono text-accent font-bold">{{ order.id.split('-')[0] }}</td>
                        <td class="text-sm">{{ formatDate(order.created_at) }}</td>
                        <td>
                          <UBadge variant="outline" size="sm">{{ order.status }}</UBadge>
                        </td>
                        <td class="text-right font-bold">
                          {{ order.total_amount }} {{ order.currency }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Devices Section -->
              <div v-if="activeTab === 'devices'" class="section-fade-in">
                <div class="flex items-center justify-between mb-6">
                  <h3 class="text-lg font-bold flex items-center gap-2 text-text">
                    <Icon name="ph:cpu-bold" class="text-success" />
                    IoT Устройства
                  </h3>
                  <UButton 
                    variant="ghost" 
                    size="sm" 
                    :to="`/admin/devices?user_id=${userId}`"
                    icon="ph:arrow-square-out-bold"
                  >
                    Посмотреть все
                  </UButton>
                </div>

                <div v-if="devicesPending" class="empty-placeholder">
                  <Icon name="ph:spinner-bold" size="32" class="mb-2 opacity-50" />
                  <p>Загрузка устройств...</p>
                </div>

                <div v-else-if="userDevices.length === 0" class="empty-placeholder">
                  <Icon name="ph:cpu-light" size="48" class="mb-2 opacity-30" />
                  <p>Нет подключенных устройств</p>
                </div>

                <div v-else class="admin-table-wrapper">
                  <table class="admin-table">
                    <thead>
                      <tr>
                        <th>UID</th>
                        <th>Название</th>
                        <th>Модель</th>
                        <th>Статус</th>
                        <th>Зарегистрировано</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="dev in userDevices"
                        :key="dev.id"
                        :data-testid="`device-row-${dev.id}`"
                      >
                        <td>
                          <span class="font-mono text-xs">{{ dev.device_uid }}</span>
                        </td>
                        <td>{{ dev.name || '—' }}</td>
                        <td>{{ dev.model || '—' }}</td>
                        <td>
                          <span :class="dev.is_active ? 'status-active' : 'status-blocked'">
                            {{ dev.is_active ? 'Активно' : 'Неактивно' }}
                          </span>
                        </td>
                        <td>{{ formatDate(dev.registered_at) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

            </div>
          </UCard>
        </main>
      </div>
    </div>
  </NuxtLayout>
</template>

<style scoped>
/* Profile Header Styles */
.profile-avatar {
  width: 96px;
  height: 96px;
  border-radius: var(--radius-full);
  background: var(--color-surface-2);
  border: 2px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 800;
  color: var(--color-accent);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.info-item label {
  display: block;
  font-size: 10px;
  font-weight: 700;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.info-item p {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
}

.user-agent-box {
  font-size: 11px;
  color: var(--color-text-2);
  line-height: 1.4;
  padding: 10px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  word-break: break-all;
  font-family: var(--font-mono);
}

/* Tabs UI Styles */
.tabs-nav {
  display: flex;
  overflow-x: auto;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  scrollbar-width: none;
  position: sticky;
  top: 0;
  z-index: 20;
}

.tabs-nav::-webkit-scrollbar {
  display: none;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 24px;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
  position: relative;
}

.tab-btn:hover {
  color: var(--color-text);
  background: var(--color-bg-subtle);
}

.tab-btn.active {
  color: var(--color-accent);
  background: var(--color-accent-glow);
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--color-accent);
  box-shadow: 0 -2px 10px var(--color-accent-glow);
}

/* Section Styles */
.section-fade-in {
  animation: section-in 0.4s ease-out;
}

@keyframes section-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.data-box {
  background: var(--color-surface-2);
  padding: 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.data-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-value {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text);
}

.ua-text {
  font-size: 12px;
  font-family: var(--font-mono);
  color: var(--color-text-2);
  background: var(--color-bg);
  padding: 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  word-break: break-all;
}

/* Address & Device Cards */
.address-card {
  padding: 16px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.address-card:hover {
  border-color: var(--color-info);
  background: var(--color-surface-3);
}

.address-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.address-header .city {
  font-weight: 800;
  text-transform: uppercase;
  font-size: 12px;
  color: var(--color-text);
}

.address-full {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin-bottom: 4px;
}

.address-footer {
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--color-muted);
}

.empty-placeholder {
  padding: 48px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  color: var(--color-muted);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
}

.text-right { text-align: right; }

.status-active { color: var(--color-success); font-weight: 600; }
.status-blocked { color: var(--color-error); font-weight: 600; }
</style>
