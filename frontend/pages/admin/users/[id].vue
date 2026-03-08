<script setup lang="ts">
import { ref, computed } from 'vue'
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
  { id: 'general', label: 'ОБЩАЯ ИНФО', icon: 'ph:user-bold' },
  { id: 'security', label: 'БЕЗОПАСНОСТЬ', icon: 'ph:shield-check-bold' },
  { id: 'addresses', label: 'АДРЕСА', icon: 'ph:map-pin-bold' },
  { id: 'orders', label: 'ЗАКАЗЫ', icon: 'ph:shopping-cart-bold' },
  { id: 'devices', label: 'УСТРОЙСТВА', icon: 'ph:cpu-bold' }
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
      <div class="flex items-center gap-4">
        <UButton variant="ghost" to="/admin/users" size="sm" aria-label="Назад" class="race-back-btn">
          <template #icon><Icon name="ph:caret-left-bold" size="24" /></template>
        </UButton>
        <h1 class="font-race text-2xl uppercase tracking-widest truncate max-w-[200px] md:max-w-[400px]">
          {{ user?.full_name || user?.email || 'ЗАГРУЗКА...' }}
        </h1>
        <UBadge v-if="user" :variant="user.is_active ? 'success' : 'error'" class="race-badge">
          {{ user.is_active ? 'ONLINE' : 'BLOCKED' }}
        </UBadge>
      </div>
    </template>

    <template #header-actions>
      <div v-if="user" class="flex gap-2">
        <UButton variant="outline" size="sm" class="race-btn-outline">
          <template #icon><Icon name="ph:pencil-simple-bold" /></template>
          <span>РЕДАКТИРОВАТЬ</span>
        </UButton>
        <UButton variant="error" size="sm" class="race-btn-danger">
          <template #icon><Icon name="ph:trash-bold" /></template>
        </UButton>
      </div>
    </template>

    <div v-if="pending" class="p-4 md:p-8 w-full max-w-[1600px] mx-auto">
      <USkeleton height="250px" class="mb-6 rounded-none" />
      <USkeleton height="500px" class="rounded-none" />
    </div>

    <div v-else-if="error" class="p-4 md:p-8 w-full max-w-[1600px] mx-auto">
      <UCard class="race-card border-error">
        <div class="text-center py-12 text-error">
          <Icon name="ph:warning-duotone" size="64" class="mb-6 animate-pulse" />
          <h2 class="text-2xl font-race uppercase tracking-widest mb-4">Системная Ошибка</h2>
          <p class="mb-6 text-muted">Не удалось загрузить данные пилота.</p>
          <UButton variant="primary" @click="refresh" class="race-btn">ПОВТОРНЫЙ ЗАПРОС</UButton>
        </div>
      </UCard>
    </div>

    <div v-else-if="user" class="w-full h-full p-4 md:p-8 lg:p-10 max-w-none">
      <div class="grid grid-cols-1 xl:grid-cols-12 gap-8">
        
        <!-- Sidebar Panel -->
        <div class="xl:col-span-3 space-y-8">
          <UCard class="race-panel relative overflow-hidden">
            <div class="absolute top-0 right-0 w-16 h-16 bg-accent opacity-10 transform rotate-45 translate-x-8 -translate-y-8"></div>
            
            <div class="flex flex-col items-center text-center relative z-10 pt-4">
              <div class="race-avatar-container mb-6">
                <Icon name="ph:user-focus-duotone" size="72" class="text-accent" />
                <div class="race-avatar-ring"></div>
              </div>
              
              <h2 class="text-2xl font-race uppercase tracking-widest truncate w-full mb-1">
                {{ user.full_name || 'UNDEFINED' }}
              </h2>
              <p class="text-muted font-mono text-sm truncate w-full mb-6">{{ user.email }}</p>
              
              <div class="flex gap-2 mb-8">
                <UBadge variant="accent" class="race-badge-small">{{ user.role }}</UBadge>
                <UBadge :variant="user.is_verified ? 'success' : 'warning'" class="race-badge-small">
                  {{ user.is_verified ? 'VERIFIED' : 'UNVERIFIED' }}
                </UBadge>
              </div>
            </div>
            
            <div class="space-y-4 pt-6 border-t border-border/50">
              <div class="race-info-row">
                <span class="race-info-label">ID Пилота</span>
                <span class="race-info-value font-mono text-accent">{{ user.id }}</span>
              </div>
              <div class="race-info-row">
                <span class="race-info-label">Регистрация</span>
                <span class="race-info-value font-mono">{{ formatDate(user.created_at) }}</span>
              </div>
            </div>
          </UCard>

          <UCard class="race-panel">
            <template #header>
              <div class="flex items-center gap-2 border-b border-border/50 pb-4 mb-4">
                <Icon name="ph:activity-bold" class="text-accent" />
                <h3 class="font-race text-sm uppercase tracking-widest text-muted">ТЕЛЕМЕТРИЯ ВХОДА</h3>
              </div>
            </template>
            <div class="space-y-5">
              <div class="race-telemetry-block">
                <span class="race-telemetry-label">ПОСЛЕДНИЙ КОНТАКТ</span>
                <span class="race-telemetry-value font-mono">{{ formatDate(user.last_login_at) }}</span>
              </div>
              <div class="race-telemetry-block">
                <span class="race-telemetry-label">IP УЗЕЛ</span>
                <span class="race-telemetry-value font-mono text-accent">{{ user.last_login_ip || 'UNKNOWN' }}</span>
              </div>
              <div class="race-telemetry-block">
                <span class="race-telemetry-label">ТЕРМИНАЛ</span>
                <div class="race-terminal-box line-clamp-2" :title="user.last_login_device || ''">
                  {{ user.last_login_device || 'NO DATA' }}
                </div>
              </div>
            </div>
          </UCard>
        </div>

        <!-- Main Display Screen -->
        <div class="xl:col-span-9 flex flex-col h-full min-h-[600px]">
          <UCard class="race-panel flex-grow flex flex-col p-0 overflow-hidden">
            
            <!-- Tech Tabs -->
            <div class="race-tabs-nav bg-surface-2 border-b border-border">
              <div class="flex overflow-x-auto hide-scrollbar w-full">
                <button
                  v-for="tab in tabs"
                  :key="tab.id"
                  @click="activeTab = tab.id"
                  class="race-tab-btn flex-1 min-w-[140px]"
                  :class="{ 'active': activeTab === tab.id }"
                >
                  <Icon :name="tab.icon" size="20" class="mb-1" />
                  <span>{{ tab.label }}</span>
                  <div class="race-tab-indicator"></div>
                </button>
              </div>
            </div>

            <!-- Tab Screens -->
            <div class="p-6 md:p-8 flex-grow bg-bg/30 relative">
              <!-- Grid background effect -->
              <div class="absolute inset-0 race-grid-bg opacity-10 pointer-events-none"></div>

              <!-- General -->
              <div v-if="activeTab === 'general'" class="race-screen animate-fade-in relative z-10">
                <h3 class="font-race text-xl mb-6 flex items-center gap-3">
                  <span class="w-2 h-2 bg-accent rounded-full animate-pulse"></span>
                  БАЗОВЫЕ ПАРАМЕТРЫ
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div class="race-data-card">
                    <label>ПОЛНОЕ ИМЯ</label>
                    <div class="value">{{ user.full_name || '—' }}</div>
                  </div>
                  <div class="race-data-card">
                    <label>ПОЗЫВНОЙ (EMAIL)</label>
                    <div class="value font-mono">{{ user.email }}</div>
                  </div>
                  <div class="race-data-card">
                    <label>СВЯЗЬ (ТЕЛЕФОН)</label>
                    <div class="value font-mono">{{ user.phone || '—' }}</div>
                  </div>
                  <div class="race-data-card">
                    <label>УРОВЕНЬ ДОСТУПА</label>
                    <div class="value uppercase text-accent font-bold">{{ user.role }}</div>
                  </div>
                  <div class="race-data-card">
                    <label>СТАТУС СИСТЕМЫ</label>
                    <div class="value uppercase font-bold" :class="user.is_active ? 'text-success' : 'text-error'">
                      {{ user.is_active ? 'ACTIVE' : 'LOCKED' }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Security -->
              <div v-if="activeTab === 'security'" class="race-screen animate-fade-in relative z-10">
                 <h3 class="font-race text-xl mb-6 flex items-center gap-3">
                  <span class="w-2 h-2 bg-warning rounded-full animate-pulse"></span>
                  ПРОТОКОЛ БЕЗОПАСНОСТИ
                </h3>
                <div class="race-security-box">
                  <div class="flex items-center gap-4 mb-6 pb-4 border-b border-border/50">
                    <Icon name="ph:fingerprint-duotone" size="32" class="text-warning" />
                    <div>
                      <h4 class="font-race uppercase tracking-widest">Аудит авторизации</h4>
                      <p class="text-xs text-muted font-mono">Последняя фиксация в логах</p>
                    </div>
                  </div>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="race-data-card border-warning/30">
                      <label>IP АДРЕС</label>
                      <div class="value font-mono text-warning">{{ user.last_login_ip || '—' }}</div>
                    </div>
                    <div class="race-data-card border-warning/30">
                      <label>ВРЕМЯ КОНТАКТА</label>
                      <div class="value font-mono">{{ formatDate(user.last_login_at) }}</div>
                    </div>
                    <div class="race-data-card border-warning/30 md:col-span-2">
                      <label>СИГНАТУРА УСТРОЙСТВА (USER AGENT)</label>
                      <div class="race-terminal-box mt-2 text-warning/80">
                        {{ user.last_login_device || 'NO DATA' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Addresses -->
              <div v-if="activeTab === 'addresses'" class="race-screen animate-fade-in relative z-10">
                <h3 class="font-race text-xl mb-6 flex items-center gap-3">
                  <span class="w-2 h-2 bg-info rounded-full animate-pulse"></span>
                  КООРДИНАТЫ БАЗЫ
                </h3>
                
                <div v-if="!user.addresses || user.addresses.length === 0" class="race-empty-state">
                  <div class="glitch-icon"><Icon name="ph:radar-bold" size="48" /></div>
                  <p>Векторы не заданы. Координаты отсутствуют.</p>
                </div>
                
                <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div v-for="addr in user.addresses" :key="addr.id" class="race-address-card">
                    <div class="card-header">
                      <span class="city font-race tracking-wider uppercase">{{ addr.city }}</span>
                      <UBadge v-if="addr.is_default" variant="success" class="race-badge-small">MAIN</UBadge>
                    </div>
                    <p class="address-text">{{ addr.address }}</p>
                    <div class="card-footer font-mono text-xs">
                      <span>ADD: {{ formatDate(addr.created_at) }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Orders -->
              <div v-if="activeTab === 'orders'" class="race-screen animate-fade-in relative z-10">
                <h3 class="font-race text-xl mb-6 flex items-center gap-3">
                  <span class="w-2 h-2 bg-primary rounded-full animate-pulse"></span>
                  ИСТОРИЯ ОПЕРАЦИЙ
                </h3>
                
                <div v-if="!user.orders || user.orders.length === 0" class="race-empty-state">
                  <div class="glitch-icon"><Icon name="ph:receipt-bold" size="48" /></div>
                  <p>Транзакции не обнаружены.</p>
                </div>
                
                <div v-else class="race-table-container">
                  <table class="race-table">
                    <thead>
                      <tr>
                        <th>ТРЕК-КОД</th>
                        <th>ДАТА</th>
                        <th>СТАТУС</th>
                        <th class="text-right">СУММА</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="order in user.orders" :key="order.id">
                        <td class="font-mono text-accent">{{ order.id.split('-')[0] }}</td>
                        <td class="font-mono text-sm">{{ formatDate(order.created_at) }}</td>
                        <td><UBadge variant="outline" class="race-badge-small border-accent text-accent">{{ order.status }}</UBadge></td>
                        <td class="text-right font-race tracking-wider">{{ order.total_amount }} {{ order.currency }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Devices -->
              <div v-if="activeTab === 'devices'" class="race-screen animate-fade-in relative z-10">
                <div class="flex justify-between items-center mb-6">
                  <h3 class="font-race text-xl flex items-center gap-3">
                    <span class="w-2 h-2 bg-success rounded-full animate-pulse"></span>
                    СЕТЬ IoT УСТРОЙСТВ
                  </h3>
                  <UButton size="sm" variant="outline" class="race-btn-outline border-success text-success hover:bg-success/10">
                    <template #icon><Icon name="ph:arrows-clockwise-bold" /></template>
                    <span>СКАН</span>
                  </UButton>
                </div>
                
                <div v-if="!user.devices || user.devices.length === 0" class="race-empty-state">
                  <div class="glitch-icon"><Icon name="ph:cpu-bold" size="48" /></div>
                  <p>Сопряженные модули отсутствуют.</p>
                </div>
                
                <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div v-for="dev in user.devices" :key="dev.id" class="race-device-card" :class="{'online': dev.is_online}">
                    <div class="device-status-bar" :class="dev.is_online ? 'bg-success' : 'bg-muted'"></div>
                    <div class="p-5">
                      <div class="flex items-center gap-4 mb-4">
                        <div class="device-icon" :class="{ 'text-success drop-shadow-[0_0_8px_rgba(var(--color-success-rgb),0.8)]': dev.is_online, 'text-muted': !dev.is_online }">
                          <Icon name="ph:circuitry-bold" size="32" />
                        </div>
                        <div class="flex-1 min-w-0">
                          <h4 class="font-race uppercase tracking-widest truncate">{{ dev.name || 'UNNAMED_MODULE' }}</h4>
                          <p class="text-xs text-muted font-mono truncate">{{ dev.device_id }}</p>
                        </div>
                        <UBadge :variant="dev.is_online ? 'success' : 'ghost'" class="race-badge-small" :class="{'border border-muted text-muted': !dev.is_online}">
                          {{ dev.is_online ? 'ONLINE' : 'OFFLINE' }}
                        </UBadge>
                      </div>
                      
                      <div class="bg-surface-1 p-3 rounded border border-border/50 flex justify-between items-center font-mono text-xs">
                        <span class="text-muted">ПОСЛЕДНИЙ ПИНГ:</span>
                        <span :class="dev.is_online ? 'text-success' : 'text-text-2'">{{ formatDate(dev.last_activity) }}</span>
                      </div>
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
/* Typography */
.font-race {
  font-family: 'Orbitron', 'Michroma', 'Rajdhani', sans-serif; /* Presuming a sci-fi/racing font if available, fallback to sans */
}

/* Base Panel / Card */
.race-panel {
  border-radius: 0;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  position: relative;
}

.race-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, var(--color-accent), transparent);
}

/* Avatar / Profile */
.race-avatar-container {
  position: relative;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-2);
  clip-path: polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%);
  border: 1px solid var(--color-accent);
}

.race-avatar-ring {
  position: absolute;
  inset: -4px;
  border: 1px dashed var(--color-accent);
  border-radius: 50%;
  animation: spin 10s linear infinite;
  opacity: 0.3;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

/* Badges */
.race-badge {
  border-radius: 0;
  transform: skewX(-15deg);
  font-family: monospace;
  font-weight: bold;
  letter-spacing: 1px;
}
.race-badge-small {
  border-radius: 0;
  font-size: 0.65rem;
  padding: 2px 6px;
  font-family: monospace;
  font-weight: bold;
}

/* Buttons */
.race-back-btn {
  border-radius: 0;
  transform: skewX(-10deg);
}

.race-btn, .race-btn-outline, .race-btn-danger {
  border-radius: 0;
  text-transform: uppercase;
  font-family: 'Rajdhani', sans-serif;
  font-weight: 700;
  letter-spacing: 0.05em;
  position: relative;
  overflow: hidden;
  transform: skewX(-10deg);
}

.race-btn::after, .race-btn-outline::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transform: skewX(-20deg);
  transition: left 0.5s ease;
}

.race-btn:hover::after, .race-btn-outline:hover::after {
  left: 150%;
}

/* Layout Info Rows */
.race-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}
.race-info-label {
  font-size: 0.75rem;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.race-info-value {
  font-size: 0.875rem;
  font-weight: 600;
}

/* Telemetry Section */
.race-telemetry-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.race-telemetry-label {
  font-size: 0.65rem;
  color: var(--color-accent);
  text-transform: uppercase;
  letter-spacing: 2px;
}
.race-telemetry-value {
  font-size: 0.875rem;
  padding: 4px 8px;
  background: var(--color-surface-2);
  border-left: 2px solid var(--color-accent);
}

.race-terminal-box {
  background: #000;
  color: #0f0;
  font-family: monospace;
  font-size: 0.7rem;
  padding: 8px;
  border: 1px solid #333;
  word-break: break-all;
}

/* Tabs Nav */
.hide-scrollbar::-webkit-scrollbar { display: none; }
.hide-scrollbar { scrollbar-width: none; }

.race-tab-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 16px 8px;
  color: var(--color-muted);
  font-family: 'Orbitron', sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  position: relative;
  transition: all 0.2s ease;
  background: transparent;
  border: none;
  cursor: pointer;
  outline: none;
}

.race-tab-btn:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.race-tab-btn.active {
  color: var(--color-accent);
  background: rgba(var(--color-accent-rgb), 0.05);
}

.race-tab-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: var(--color-accent);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.race-tab-btn.active .race-tab-indicator {
  transform: scaleX(1);
}

/* Data Cards */
.race-data-card {
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  padding: 16px;
  position: relative;
  transition: all 0.3s ease;
}

.race-data-card:hover {
  border-color: var(--color-accent);
  box-shadow: inset 0 0 10px rgba(var(--color-accent-rgb), 0.1);
}

.race-data-card label {
  display: block;
  font-size: 0.65rem;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.race-data-card .value {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--color-text);
}

/* Security Box */
.race-security-box {
  background: var(--color-surface-1);
  border: 1px solid var(--color-warning);
  padding: 24px;
  position: relative;
}
.race-security-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(var(--color-warning-rgb), 0.03) 10px, rgba(var(--color-warning-rgb), 0.03) 20px);
  pointer-events: none;
}

/* Address Cards */
.race-address-card {
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  padding: 20px;
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%);
  position: relative;
}
.race-address-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 15px;
  height: 15px;
  background: var(--color-border);
}
.race-address-card:hover { border-color: var(--color-info); }
.race-address-card:hover::after { background: var(--color-info); }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 8px;
}
.address-text {
  font-size: 0.875rem;
  color: var(--color-text-2);
  min-height: 40px;
}
.card-footer {
  margin-top: 16px;
  color: var(--color-muted);
}

/* Table */
.race-table-container {
  overflow-x: auto;
  border: 1px solid var(--color-border);
}
.race-table {
  width: 100%;
  border-collapse: collapse;
}
.race-table th {
  background: var(--color-surface-2);
  padding: 12px 16px;
  text-align: left;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.75rem;
  color: var(--color-muted);
  letter-spacing: 1px;
  border-bottom: 1px solid var(--color-border);
}
.race-table td {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
}
.race-table tr:hover { background: var(--color-surface-hover); }

/* Devices */
.race-device-card {
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}
.race-device-card.online {
  border-color: rgba(var(--color-success-rgb), 0.3);
}
.race-device-card.online:hover {
  border-color: var(--color-success);
  box-shadow: 0 0 15px rgba(var(--color-success-rgb), 0.1);
}
.device-status-bar {
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
}

/* Empty State */
.race-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  border: 1px dashed var(--color-border);
  background: rgba(0,0,0,0.1);
}
.glitch-icon {
  color: var(--color-muted);
  margin-bottom: 16px;
  opacity: 0.5;
}
.race-empty-state p {
  font-family: monospace;
  color: var(--color-text-2);
  letter-spacing: 1px;
}

/* Background Grid */
.race-grid-bg {
  background-size: 40px 40px;
  background-image: linear-gradient(to right, var(--color-border) 1px, transparent 1px),
                    linear-gradient(to bottom, var(--color-border) 1px, transparent 1px);
}

.animate-fade-in {
  animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.text-success { color: var(--color-success); }
.text-error { color: var(--color-error); }
.text-accent { color: var(--color-accent); }
.text-warning { color: var(--color-warning); }
.text-info { color: var(--color-info); }
.border-success { border-color: var(--color-success); }
.border-error { border-color: var(--color-error); }
.border-warning { border-color: var(--color-warning); }
</style>
