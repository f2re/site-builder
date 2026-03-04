<script setup lang="ts">
import { useIoT, type IoTDevice, type TelemetryEvent } from '~/composables/useIoT'

definePageMeta({
  middleware: 'auth'
})

const route = useRoute()
const { getDevice, connectDevice } = useIoT()
const toast = useToast()

const device = ref<IoTDevice | null>(null)
const status = ref<'connecting' | 'connected' | 'error' | 'disconnected'>('connecting')
const telemetry = ref<any>({})
const logs = ref<{ts: string, type: string, data: any}[]>([])
const lastUpdate = ref<number | null>(null)

let socket: WebSocket | null = null

onMounted(async () => {
  try {
    device.value = await getDevice(route.params.id as string)
    initWebSocket()
  } catch (err) {
    status.value = 'error'
    toast.error('Ошибка', 'Не удалось загрузить данные устройства')
  }
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
})

function initWebSocket() {
  status.value = 'connecting'
  socket = connectDevice(route.params.id as string, (event: TelemetryEvent) => {
    if (event.event === 'connected') {
      status.value = 'connected'
      toast.success('Подключено', 'Стрим телеметрии активен')
    } else if (event.event === 'telemetry') {
      telemetry.value = { ...telemetry.value, ...event.data }
      lastUpdate.value = Date.now()
      
      // Add to logs
      logs.value.unshift({
        ts: new Date().toLocaleTimeString(),
        type: 'DATA',
        data: event.data
      })
      if (logs.value.length > 50) logs.value.pop()
    } else if (event.event === 'error') {
      status.value = 'error'
      toast.error('Ошибка связи', event.message || 'Произошла ошибка WebSocket')
    }
  })

  socket.onclose = () => {
    if (status.value !== 'error') {
      status.value = 'disconnected'
    }
  }
}

const formatValue = (val: any) => {
  if (typeof val === 'number') return val.toFixed(2)
  return val
}

const isOnline = computed(() => {
  if (status.value !== 'connected') return false
  if (!lastUpdate.value) return false
  return (Date.now() - lastUpdate.value) < 10000 // consider online if data in last 10s
})
</script>

<template>
  <div class="dashboard-page">
    <div class="container">
      <div class="dashboard-nav">
        <NuxtLink to="/profile/devices" class="back-link">
          <Icon name="ph:arrow-left-bold" />
          Вернуться к списку
        </NuxtLink>
        <div class="status-indicator" :class="status">
          <span class="dot"></span>
          {{ status === 'connected' ? 'LIVE' : status.toUpperCase() }}
        </div>
      </div>

      <header class="dashboard-header">
        <div class="device-meta">
          <h1 class="device-name">{{ device?.name || 'Загрузка...' }}</h1>
          <p class="device-uid">{{ device?.device_uid }} • {{ device?.model }}</p>
        </div>
        <div class="header-actions">
          <UButton
            v-if="status === 'error' || status === 'disconnected'"
            variant="primary"
            size="sm"
            icon="ph:arrow-clockwise-bold"
            @click="initWebSocket"
          >
            Переподключиться
          </UButton>
        </div>
      </header>

      <div class="dashboard-grid">
        <!-- Main Telemetry Grid -->
        <div class="telemetry-main">
          <div class="metrics-grid">
            <div v-for="(value, key) in telemetry" :key="key" class="metric-card">
              <span class="metric-label">{{ key.replace(/_/g, ' ').toUpperCase() }}</span>
              <div class="metric-value-wrap">
                <span class="metric-value">{{ formatValue(value) }}</span>
                <span class="metric-unit" v-if="key.includes('temp')">°C</span>
                <span class="metric-unit" v-else-if="key.includes('speed')">km/h</span>
                <span class="metric-unit" v-else-if="key.includes('voltage')">V</span>
                <span class="metric-unit" v-else-if="key.includes('rpm')">RPM</span>
                <span class="metric-unit" v-else-if="key.includes('percent')">%</span>
              </div>
              <div class="metric-chart-mini">
                <!-- Placeholder for mini chart -->
                <div class="mini-bar" :style="{ width: '70%', background: 'var(--color-neon)' }"></div>
              </div>
            </div>
            
            <div v-if="Object.keys(telemetry).length === 0" class="no-data">
              <Icon name="ph:gauge-bold" size="48" />
              <p>Ожидание данных телеметрии...</p>
            </div>
          </div>

          <UCard class="terminal-card">
            <template #header>
              <div class="terminal-header">
                <Icon name="ph:terminal-window-bold" />
                <span>RAW DATA STREAM</span>
              </div>
            </template>
            <div class="terminal-content">
              <div v-for="(log, i) in logs" :key="i" class="log-entry">
                <span class="log-ts">[{{ log.ts }}]</span>
                <span class="log-type" :class="log.type">{{ log.type }}</span>
                <span class="log-data">{{ JSON.stringify(log.data) }}</span>
              </div>
              <div v-if="logs.length === 0" class="log-empty">
                Starting telemetry listener...
              </div>
            </div>
          </UCard>
        </div>

        <!-- Sidebar / Secondary Info -->
        <aside class="dashboard-sidebar">
          <UCard class="status-card">
            <h3 class="sidebar-title">Состояние системы</h3>
            <div class="status-list">
              <div class="status-item">
                <span class="label">Связь</span>
                <span class="value" :class="{ 'text-neon': isOnline }">
                  {{ isOnline ? 'ОТЛИЧНО' : 'НЕТ ДАННЫХ' }}
                </span>
              </div>
              <div class="status-item">
                <span class="label">Задержка</span>
                <span class="value">14ms</span>
              </div>
              <div class="status-item">
                <span class="label">Протокол</span>
                <span class="value">WSS/JSON</span>
              </div>
            </div>
          </UCard>

          <div class="action-panel">
            <UButton variant="ghost" icon="ph:gear-bold" block>Настройки устройства</UButton>
            <UButton variant="ghost" icon="ph:export-bold" block>Экспорт истории</UButton>
            <UButton variant="danger" icon="ph:warning-bold" block>Экстренная остановка</UButton>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page {
  padding: 24px 0 60px;
  background-color: var(--color-bg);
  min-height: 100vh;
  color: var(--color-text);
}

.dashboard-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.back-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-2);
  text-decoration: none;
  font-size: var(--text-sm);
  transition: color var(--transition-fast);
}

.back-link:hover {
  color: var(--color-accent);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
}

.status-indicator .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-muted);
}

.status-indicator.connected { color: var(--color-neon); border-color: var(--color-neon-glow); }
.status-indicator.connected .dot { background: var(--color-neon); box-shadow: var(--shadow-glow-neon); animation: pulse 2s infinite; }
.status-indicator.connecting .dot { background: var(--color-warning); animation: pulse 1s infinite; }
.status-indicator.error { color: var(--color-error); border-color: var(--color-error-bg); }
.status-indicator.error .dot { background: var(--color-error); }

@keyframes pulse {
  0% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
  100% { opacity: 1; transform: scale(1); }
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 20px;
}

.device-name {
  font-size: var(--text-3xl);
  font-weight: 900;
  margin: 0;
  letter-spacing: -0.04em;
  text-transform: uppercase;
  font-style: italic;
}

.device-uid {
  font-family: var(--font-mono);
  color: var(--color-muted);
  font-size: var(--text-sm);
  margin: 4px 0 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 32px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.metric-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 20px;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.metric-card:hover {
  border-color: var(--color-neon);
  box-shadow: var(--shadow-glow-neon);
  transform: translateY(-2px);
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; width: 4px; height: 100%;
  background: var(--color-neon);
  opacity: 0.3;
}

.metric-label {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  color: var(--color-muted);
  margin-bottom: 8px;
}

.metric-value-wrap {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.metric-value {
  font-size: var(--text-2xl);
  font-family: var(--font-mono);
  font-weight: 800;
  color: var(--color-text);
}

.metric-unit {
  font-size: var(--text-sm);
  color: var(--color-muted);
  font-weight: 600;
}

.metric-chart-mini {
  margin-top: 16px;
  height: 4px;
  background: var(--color-surface-3);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.mini-bar {
  height: 100%;
  transition: width 0.3s ease;
}

.no-data {
  grid-column: 1 / -1;
  padding: 60px;
  text-align: center;
  color: var(--color-muted);
  background: var(--color-surface-2);
  border-radius: var(--radius-xl);
  border: 1px dashed var(--color-border);
}

.no-data p {
  margin-top: 16px;
  font-family: var(--font-mono);
}

.terminal-card {
  background: #000 !important;
  border-color: #1a1a1a !important;
}

.terminal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-neon);
}

.terminal-content {
  font-family: var(--font-mono);
  font-size: 11px;
  height: 300px;
  overflow-y: auto;
  color: #00ff41; /* Matrix green */
  padding: 12px;
  line-height: 1.5;
}

.log-entry {
  margin-bottom: 4px;
  display: flex;
  gap: 12px;
  white-space: nowrap;
}

.log-ts { color: #888; }
.log-type { font-weight: 700; padding: 0 4px; border-radius: 2px; }
.log-type.DATA { background: rgba(0, 255, 65, 0.1); color: #00ff41; }
.log-data { color: #eee; overflow: hidden; text-overflow: ellipsis; }

.sidebar-title {
  font-size: var(--text-sm);
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 20px;
  color: var(--color-text-2);
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: var(--font-mono);
  font-size: 12px;
}

.status-item .label { color: var(--color-muted); }
.status-item .value { font-weight: 700; }
.text-neon { color: var(--color-neon); text-shadow: var(--shadow-glow-neon); }

.action-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .device-name {
    font-size: var(--text-2xl);
  }
}
</style>
