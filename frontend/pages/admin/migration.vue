<script setup lang="ts">
/**
 * admin/migration.vue
 * Admin Migration Interface with Race-Style UI
 * Handles OpenCart data migration orchestration and status monitoring.
 */

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth'
})

// Types
type MigrationEntityKey = 'users' | 'categories' | 'products' | 'images' | 'orders'

interface MigrationEntityStatus {
  total: number
  processed: number
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'PAUSED' | 'FAILED'
  error?: string | null
}

interface MigrationStatus {
  overall_status: 'IDLE' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'FAILED'
  overall_progress: number
  entities: Record<MigrationEntityKey, MigrationEntityStatus>
}

// State
const status = ref<MigrationStatus | null>(null)
const isLoading = ref(true)
const isActionPending = ref(false)
const refreshInterval = ref<NodeJS.Timeout | null>(null)

const { add: addToast } = useToast()
const apiFetch = useApiFetch()

// API Methods
const fetchStatus = async () => {
  try {
    const { data, error } = await useApi<MigrationStatus>('/admin/migration/status')
    if (error.value) throw error.value
    if (data.value) {
      status.value = data.value
      // Auto-refresh if running
      if (status.value.overall_status === 'RUNNING') {
        startPolling()
      } else {
        stopPolling()
      }
    }
  } catch (err: any) {
    addToast({
      type: 'error',
      title: 'Ошибка получения статуса',
      message: err.message || 'Не удалось загрузить данные миграции'
    })
  } finally {
    isLoading.value = false
  }
}

const startMigration = async () => {
  isActionPending.value = true
  try {
    await apiFetch('/admin/migration/start', { method: 'POST' })
    addToast({ type: 'success', title: 'Миграция запущена' })
    await fetchStatus()
  } catch (err: any) {
    addToast({ type: 'error', title: 'Ошибка запуска', message: err.message })
  } finally {
    isActionPending.value = false
  }
}

const pauseMigration = async () => {
  isActionPending.value = true
  try {
    await apiFetch('/admin/migration/pause', { method: 'POST' })
    addToast({ type: 'info', title: 'Миграция приостановлена' })
    await fetchStatus()
  } catch (err: any) {
    addToast({ type: 'error', title: 'Ошибка паузы', message: err.message })
  } finally {
    isActionPending.value = false
  }
}

const resumeMigration = async () => {
  isActionPending.value = true
  try {
    await apiFetch('/admin/migration/resume', { method: 'POST' })
    addToast({ type: 'success', title: 'Миграция возобновлена' })
    await fetchStatus()
  } catch (err: any) {
    addToast({ type: 'error', title: 'Ошибка возобновления', message: err.message })
  } finally {
    isActionPending.value = false
  }
}

// Polling Logic
const startPolling = () => {
  if (refreshInterval.value) return
  refreshInterval.value = setInterval(() => {
    fetchStatus()
  }, 3000)
}

const stopPolling = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// Lifecycle
onMounted(() => {
  fetchStatus()
})

onUnmounted(() => {
  stopPolling()
})

// Helpers
const getStatusVariant = (s: string): 'info' | 'success' | 'warning' | 'error' | 'accent' => {
  switch (s) {
    case 'RUNNING': return 'info'
    case 'COMPLETED': return 'success'
    case 'PAUSED': return 'warning'
    case 'FAILED': return 'error'
    default: return 'accent'
  }
}

const getEntityIcon = (key: MigrationEntityKey) => {
  switch (key) {
    case 'users': return 'ph:users-duotone'
    case 'categories': return 'ph:folders-duotone'
    case 'products': return 'ph:package-duotone'
    case 'images': return 'ph:image-duotone'
    case 'orders': return 'ph:shopping-cart-duotone'
  }
}

const getEntityLabel = (key: string) => {
  const labels: Record<string, string> = {
    users: 'Пользователи',
    categories: 'Категории',
    products: 'Товары',
    images: 'Изображения',
    orders: 'Заказы'
  }
  return labels[key] || key
}
</script>

<template>
  <div class="migration-page">
    <header class="migration-header">
      <div class="header-content">
        <h1 class="text-2xl font-bold">Миграция данных</h1>
        <p class="text-muted">Импорт каталога и пользователей из OpenCart</p>
      </div>

      <div class="header-actions">
        <template v-if="status?.overall_status === 'RUNNING'">
          <UButton 
            variant="secondary" 
            @click="pauseMigration" 
            :loading="isActionPending"
          >
            <template #icon><Icon name="ph:pause-bold" /></template>
            Приостановить
          </UButton>
        </template>
        <template v-else-if="status?.overall_status === 'PAUSED'">
          <UButton 
            variant="primary" 
            @click="resumeMigration" 
            :loading="isActionPending"
          >
            <template #icon><Icon name="ph:play-bold" /></template>
            Возобновить
          </UButton>
        </template>
        <template v-else>
          <UButton 
            variant="primary" 
            @click="startMigration" 
            :loading="isActionPending"
            :disabled="status?.overall_status === 'COMPLETED'"
          >
            <template #icon><Icon name="ph:rocket-launch-bold" /></template>
            Запустить миграцию
          </UButton>
        </template>
      </div>
    </header>

    <div v-if="isLoading" class="migration-grid">
      <USkeleton v-for="i in 6" :key="i" height="160px" />
    </div>

    <div v-else-if="status" class="migration-content">
      <!-- Global Progress -->
      <UCard class="overall-card" :class="{ 'card--failed': status.overall_status === 'FAILED' }">
        <div class="overall-header">
          <div class="status-info">
            <span class="label">Общий прогресс</span>
            <UBadge :variant="getStatusVariant(status.overall_status)">
              {{ status.overall_status }}
            </UBadge>
          </div>
          <span class="percentage">{{ Math.round(status.overall_progress) }}%</span>
        </div>
        
        <div class="progress-bar-container">
          <div 
            class="progress-bar-fill" 
            :style="{ width: `${status.overall_progress}%` }"
            :class="{ 'is-running': status.overall_status === 'RUNNING' }"
          ></div>
        </div>

        <div class="overall-footer">
          <div v-if="status.overall_status === 'RUNNING'" class="running-indicator">
            <USpinner size="sm" />
            <span>Обработка данных...</span>
          </div>
          <div v-else-if="status.overall_status === 'COMPLETED'" class="completed-indicator">
            <Icon name="ph:check-circle-fill" class="text-success" />
            <span>Миграция успешно завершена</span>
          </div>
        </div>
      </UCard>

      <!-- Entity Cards -->
      <div class="migration-grid">
        <UCard 
          v-for="(entity, key) in status.entities" 
          :key="key"
          class="entity-card"
          clickable
        >
          <div class="entity-card-header">
            <div class="entity-icon-bg">
              <Icon :name="getEntityIcon(key as MigrationEntityKey)" size="24" />
            </div>
            <UBadge :variant="getStatusVariant(entity.status)" size="sm">
              {{ entity.status }}
            </UBadge>
          </div>

          <div class="entity-card-body">
            <h3 class="entity-title">{{ getEntityLabel(key as string) }}</h3>
            <div class="entity-stats">
              <span class="processed">{{ entity.processed }}</span>
              <span class="divider">/</span>
              <span class="total">{{ entity.total }}</span>
            </div>
          </div>

          <div class="entity-card-footer">
            <div class="mini-progress">
              <div 
                class="mini-progress-fill" 
                :style="{ width: `${(entity.processed / (entity.total || 1)) * 100}%` }"
                :class="`fill--${getStatusVariant(entity.status)}`"
              ></div>
            </div>
            <p v-if="entity.error" class="entity-error">
              <Icon name="ph:warning-circle-bold" />
              {{ entity.error }}
            </p>
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
.migration-page {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-bottom: 4rem;
}

.migration-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.text-muted {
  color: var(--color-muted);
  margin-top: 0.25rem;
}

.migration-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* Overall Progress Card */
.overall-card {
  margin-bottom: 2rem;
}

.card--failed {
  border-color: var(--color-error) !important;
  box-shadow: var(--color-error-bg) 0 0 15px !important;
}

.overall-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-info .label {
  font-weight: 600;
  color: var(--color-text);
}

.percentage {
  font-size: var(--text-2xl);
  font-weight: 800;
  font-family: var(--font-mono);
  color: var(--color-accent);
}

.progress-bar-container {
  height: 12px;
  background: var(--color-surface-2);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: 1rem;
  border: 1px solid var(--color-border);
}

.progress-bar-fill {
  height: 100%;
  background: var(--color-accent);
  transition: width var(--transition-slow);
  box-shadow: var(--shadow-glow-accent);
}

.progress-bar-fill.is-running {
  background: linear-gradient(
    90deg,
    var(--color-accent) 0%,
    var(--color-accent-hover) 50%,
    var(--color-accent) 100%
  );
  background-size: 200% 100%;
  animation: progress-shine 2s linear infinite;
}

@keyframes progress-shine {
  from { background-position: 200% 0; }
  to { background-position: -200% 0; }
}

.overall-footer {
  display: flex;
  align-items: center;
  height: 24px;
}

.running-indicator, .completed-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.text-success { color: var(--color-success); }

/* Entity Cards */
.entity-card {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.entity-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.entity-icon-bg {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-accent);
  border: 1px solid var(--color-border);
}

.entity-card-body {
  flex: 1;
  margin-bottom: 1rem;
}

.entity-title {
  font-size: var(--text-lg);
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.entity-stats {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  font-family: var(--font-mono);
}

.processed {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text);
}

.total, .divider {
  color: var(--color-muted);
  font-size: var(--text-sm);
}

.entity-card-footer {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mini-progress {
  height: 4px;
  background: var(--color-surface-3);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.mini-progress-fill {
  height: 100%;
  transition: width var(--transition-normal);
}

.fill--success { background-color: var(--color-success); }
.fill--info { background-color: var(--color-info); }
.fill--warning { background-color: var(--color-warning); }
.fill--error { background-color: var(--color-error); }
.fill--accent { background-color: var(--color-muted); }

.entity-error {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: var(--text-xs);
  color: var(--color-error);
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .migration-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
}
</style>
