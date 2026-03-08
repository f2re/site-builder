<script setup lang="ts">
import { ref, computed } from 'vue'
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
  { id: 'general', label: 'Общая', icon: 'ph:user-bold' },
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
      <div class="flex items-center gap-3">
        <UButton variant="ghost" to="/admin/users" size="sm" aria-label="Назад">
          <template #icon><Icon name="ph:arrow-left-bold" size="20" /></template>
        </UButton>
        <span v-if="user" class="header-name truncate">{{ user.full_name || user.email }}</span>
        <UBadge v-if="user" :variant="user.is_active ? 'success' : 'error'" size="sm">
          {{ user.is_active ? 'Активен' : 'Заблокирован' }}
        </UBadge>
      </div>
    </template>

    <div v-if="pending" class="p-6">
      <USkeleton height="200px" class="mb-6" />
      <USkeleton height="400px" />
    </div>

    <div v-else-if="error" class="p-6">
      <UCard>
        <div class="text-center py-8 text-error">
          <Icon name="ph:warning-circle-bold" size="48" class="mb-4" />
          <p>Ошибка при загрузке данных пользователя</p>
          <UButton variant="ghost" @click="refresh" class="mt-4">Попробовать снова</UButton>
        </div>
      </UCard>
    </div>

    <div v-else-if="user" class="user-detail-page p-4 lg:p-6">
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Sidebar / Summary -->
        <div class="lg:col-span-1 space-y-6">
          <UCard>
            <div class="user-summary text-center">
              <div class="avatar-placeholder mx-auto mb-4">
                <Icon name="ph:user-circle-bold" size="80" class="text-muted" />
              </div>
              <h2 class="text-xl font-bold truncate">{{ user.full_name || 'Без имени' }}</h2>
              <p class="text-muted text-sm truncate mb-4">{{ user.email }}</p>
              <UBadge variant="accent">{{ user.role }}</UBadge>
            </div>
            
            <div class="mt-8 space-y-4 pt-6 border-t border-border">
              <div class="info-row">
                <span class="info-label">ID:</span>
                <span class="info-value font-mono text-xs">{{ user.id }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Создан:</span>
                <span class="info-value">{{ formatDate(user.created_at) }}</span>
              </div>
            </div>
          </UCard>

          <UCard>
            <template #header>
              <h3 class="text-sm font-bold uppercase tracking-wider text-muted">Последний вход</h3>
            </template>
            <div class="space-y-4">
              <div class="info-row-stack">
                <span class="info-label">Дата:</span>
                <span class="info-value">{{ formatDate(user.last_login_at) }}</span>
              </div>
              <div class="info-row-stack">
                <span class="info-label">IP адрес:</span>
                <span class="info-value font-mono">{{ user.last_login_ip || '—' }}</span>
              </div>
              <div class="info-row-stack">
                <span class="info-label">Устройство:</span>
                <span class="info-value text-xs line-clamp-2" :title="user.last_login_device || ''">
                  {{ user.last_login_device || '—' }}
                </span>
              </div>
            </div>
          </UCard>
        </div>

        <!-- Main Content -->
        <div class="lg:col-span-3 space-y-6">
          <UCard>
            <div class="tabs-container">
              <div class="tabs-scroll">
                <button
                  v-for="tab in tabs"
                  :key="tab.id"
                  @click="activeTab = tab.id"
                  class="tab-btn"
                  :class="{ 'tab-btn--active': activeTab === tab.id }"
                >
                  <Icon :name="tab.icon" size="18" />
                  <span>{{ tab.label }}</span>
                </button>
              </div>
            </div>

            <div class="tab-content mt-6">
              <!-- General Tab -->
              <div v-if="activeTab === 'general'" class="space-y-6 animate-fade-in">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="data-group">
                    <label>Полное имя</label>
                    <div class="data-value">{{ user.full_name || '—' }}</div>
                  </div>
                  <div class="data-group">
                    <label>Email</label>
                    <div class="data-value">{{ user.email }}</div>
                  </div>
                  <div class="data-group">
                    <label>Телефон</label>
                    <div class="data-value">{{ user.phone || '—' }}</div>
                  </div>
                  <div class="data-group">
                    <label>Роль</label>
                    <div class="data-value capitalize">{{ user.role }}</div>
                  </div>
                  <div class="data-group">
                    <label>Статус</label>
                    <div class="data-value">
                      <span :class="user.is_active ? 'text-success' : 'text-error'">
                        {{ user.is_active ? 'Активен' : 'Заблокирован' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Security Tab -->
              <div v-if="activeTab === 'security'" class="space-y-6 animate-fade-in">
                <div class="bg-surface-2 p-4 rounded-lg border border-border">
                  <h4 class="font-bold mb-4 flex items-center gap-2 text-accent">
                    <Icon name="ph:fingerprint-bold" />
                    Диагностика входа
                  </h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="data-group">
                      <label>Последний IP</label>
                      <div class="data-value font-mono">{{ user.last_login_ip || '—' }}</div>
                    </div>
                    <div class="data-group">
                      <label>Последний вход</label>
                      <div class="data-value">{{ formatDate(user.last_login_at) }}</div>
                    </div>
                    <div class="data-group md:col-span-2">
                      <label>User Agent (Устройство)</label>
                      <div class="data-value text-xs bg-bg p-3 rounded border border-border font-mono break-all">
                        {{ user.last_login_device || 'Сведения отсутствуют' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Addresses Tab -->
              <div v-if="activeTab === 'addresses'" class="space-y-4 animate-fade-in">
                <div v-if="user.addresses.length === 0" class="empty-state-mini">
                  <Icon name="ph:map-pin-slash-bold" size="32" />
                  <p>У пользователя нет сохраненных адресов</p>
                </div>
                <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-for="addr in user.addresses" :key="addr.id" class="address-card">
                    <div class="address-header">
                      <span class="address-city">{{ addr.city }}</span>
                      <UBadge v-if="addr.is_default" variant="success" size="sm">Основной</UBadge>
                    </div>
                    <p class="address-text">{{ addr.address }}</p>
                    <div class="address-footer">
                      <span class="text-xs text-muted">Добавлен: {{ formatDate(addr.created_at) }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Orders Tab -->
              <div v-if="activeTab === 'orders'" class="space-y-4 animate-fade-in">
                <div v-if="user.orders.length === 0" class="empty-state-mini">
                  <Icon name="ph:shopping-bag-open-bold" size="32" />
                  <p>Заказы не найдены</p>
                </div>
                <div v-else class="overflow-x-auto">
                  <table class="detail-table">
                    <thead>
                      <tr>
                        <th>№ Заказа</th>
                        <th>Дата</th>
                        <th>Статус</th>
                        <th class="text-right">Сумма</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="order in user.orders" :key="order.id">
                        <td class="font-mono text-xs">{{ order.id.split('-')[0] }}...</td>
                        <td>{{ formatDate(order.created_at) }}</td>
                        <td><UBadge variant="accent" size="sm">{{ order.status }}</UBadge></td>
                        <td class="text-right font-bold">{{ order.total_amount }} {{ order.currency }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Devices Tab -->
              <div v-if="activeTab === 'devices'" class="space-y-4 animate-fade-in">
                <div v-if="user.devices.length === 0" class="empty-state-mini">
                  <Icon name="ph:cpu-bold" size="32" />
                  <p>Привязанные устройства отсутствуют</p>
                </div>
                <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-for="dev in user.devices" :key="dev.id" class="device-card">
                    <div class="flex items-center gap-4">
                      <div class="device-icon" :class="{ 'device-icon--online': dev.is_online }">
                        <Icon name="ph:broadcast-bold" size="24" />
                      </div>
                      <div class="flex-1 min-width-0">
                        <h4 class="font-bold truncate">{{ dev.name || 'IoT Device' }}</h4>
                        <p class="text-xs text-muted font-mono">{{ dev.device_id }}</p>
                      </div>
                      <UBadge :variant="dev.is_online ? 'success' : 'accent'" size="sm">
                        {{ dev.is_online ? 'Online' : 'Offline' }}
                      </UBadge>
                    </div>
                    <div class="mt-4 pt-3 border-t border-border flex justify-between items-center text-xs">
                      <span class="text-muted">Активность:</span>
                      <span>{{ formatDate(dev.last_activity) }}</span>
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
.header-name {
  font-size: var(--text-lg);
  font-weight: 700;
  max-width: 200px;
}

@media (min-width: 768px) {
  .header-name { max-width: 400px; }
}

.avatar-placeholder {
  width: 100px;
  height: 100px;
  background-color: var(--color-surface-2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--color-border);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.info-row-stack {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  color: var(--color-text);
  font-weight: 500;
}

/* Tabs Styling */
.tabs-container {
  border-bottom: 1px solid var(--color-border);
  margin: -24px -24px 0;
}

.tabs-scroll {
  display: flex;
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
  padding: 0 12px;
}

.tabs-scroll::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  color: var(--color-text-2);
  font-weight: 600;
  white-space: nowrap;
  border-bottom: 2px solid transparent;
  transition: all var(--transition-fast);
  font-size: var(--text-sm);
}

.tab-btn:hover {
  color: var(--color-text);
  background-color: var(--color-surface-2);
}

.tab-btn--active {
  color: var(--color-accent);
  border-bottom-color: var(--color-accent);
}

/* Data Display */
.data-group label {
  display: block;
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-muted);
  margin-bottom: 4px;
  text-transform: uppercase;
}

.data-value {
  padding: 10px 14px;
  background-color: var(--color-surface-2);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  font-weight: 500;
}

/* Address Card */
.address-card {
  padding: 16px;
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: border-color var(--transition-fast);
}

.address-card:hover {
  border-color: var(--color-accent);
}

.address-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.address-city {
  font-weight: 700;
  color: var(--color-text);
}

.address-text {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin-bottom: 12px;
}

/* Table */
.detail-table {
  width: 100%;
  border-collapse: collapse;
}

.detail-table th {
  text-align: left;
  padding: 12px;
  font-size: var(--text-xs);
  color: var(--color-muted);
  text-transform: uppercase;
  border-bottom: 1px solid var(--color-border);
}

.detail-table td {
  padding: 14px 12px;
  border-bottom: 1px solid var(--color-border);
  font-size: var(--text-sm);
}

/* Device Card */
.device-card {
  padding: 16px;
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.device-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  background-color: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-muted);
}

.device-icon--online {
  color: var(--color-success);
  box-shadow: 0 0 10px var(--color-success-bg);
}

.empty-state-mini {
  padding: 40px 20px;
  text-align: center;
  color: var(--color-muted);
}

.empty-state-mini p {
  margin-top: 12px;
  font-size: var(--text-sm);
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.text-success { color: var(--color-success); }
.text-error { color: var(--color-error); }
.text-accent { color: var(--color-accent); }
</style>
