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
type MigrationEntityKey = 'users' | 'categories' | 'products' | 'images' | 'orders' | 'blog'

interface MigrationEntityStatus {
  total: number
  processed: number
  skipped?: number
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
const isResetPending = ref(false)
const refreshInterval = ref<NodeJS.Timeout | null>(null)

// Stale detection
const lastProgressValue = ref<number | null>(null)
const lastProgressAt = ref<number | null>(null)
const isMigrationStale = ref(false)

const { add: addToast } = useToast()
const { confirm } = useConfirm()
const apiFetch = useApiFetch()

// Stale detection watchEffect
watchEffect(() => {
  if (status.value?.overall_status === 'RUNNING') {
    const currentProgress = status.value.overall_progress
    if (lastProgressValue.value !== currentProgress) {
      lastProgressValue.value = currentProgress
      lastProgressAt.value = Date.now()
      isMigrationStale.value = false
    } else if (lastProgressAt.value !== null) {
      const elapsed = Date.now() - lastProgressAt.value
      isMigrationStale.value = elapsed > 30_000
    }
  } else {
    isMigrationStale.value = false
    lastProgressValue.value = null
    lastProgressAt.value = null
  }
})

// API Methods
const fetchStatus = async () => {
  try {
    const { data, error } = await useApi<MigrationStatus>('/admin/migration/status')
    if (error.value) throw error.value
    if (data.value) {
      status.value = data.value
      // Adjust polling based on status
      if (status.value.overall_status === 'RUNNING') {
        startPolling(2000)
      } else {
        startPolling(15000) // Slower polling when idle/paused/completed
      }
    }
  } catch (err: any) {
    console.error('Migration status fetch error:', err)
    // Don't show toast on every polling error to avoid spam
    if (isLoading.value) {
      addToast({
        type: 'error',
        title: 'Ошибка получения статуса',
        message: err.message || 'Не удалось загрузить данные миграции'
      })
    }
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
  // Immediately start fast polling so UI reflects changes quickly
  startPolling(2000)
  try {
    await apiFetch('/admin/migration/resume', { method: 'POST' })
    addToast({ type: 'success', title: 'Миграция возобновлена' })
    await fetchStatus()
  } catch (err: any) {
    addToast({ type: 'error', title: 'Ошибка возобновления', message: err.message })
    startPolling(15000)
  } finally {
    isActionPending.value = false
  }
}

const resetMigration = async () => {
  if (!await confirm({
    title: 'Очистить мигрированные данные?',
    message: 'Это удалит товары, категории, заказы и записи в блоге, созданные в процессе миграции. Действие необратимо.',
    confirmLabel: 'Очистить всё',
    variant: 'danger',
  })) {
    return
  }

  isResetPending.value = true
  try {
    await apiFetch('/admin/migration/reset', { method: 'DELETE' })
    addToast({ type: 'success', title: 'Данные очищены' })
    status.value = null
    startPolling(15000)
    await fetchStatus()
  } catch (err: any) {
    addToast({ type: 'error', title: 'Ошибка очистки', message: err.message })
  } finally {
    isResetPending.value = false
  }
}

// Polling Logic
const startPolling = (ms: number) => {
  stopPolling()
  refreshInterval.value = setInterval(() => {
    fetchStatus()
  }, ms)
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
    case 'blog': return 'ph:article-duotone'
  }
}

const getEntityLabel = (key: string) => {
  const labels: Record<string, string> = {
    users: 'Пользователи',
    categories: 'Категории',
    products: 'Товары',
    images: 'Изображения',
    orders: 'Заказы',
    blog: 'Блог (новости и инструкции)'
  }
  return labels[key] || key
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>
      Миграция данных
    </template>

    <template #header-actions>
      <div class="flex items-center gap-4">
        <UButton
          v-if="status && (status.overall_status === 'COMPLETED' || status.overall_status === 'FAILED' || status.overall_status === 'PAUSED' || status.overall_status === 'IDLE')"
          variant="ghost"
          color="error"
          @click="resetMigration"
          :loading="isResetPending"
          data-testid="migration-reset-btn"
        >
          <template #icon><Icon name="ph:trash-bold" /></template>
          Очистить данные
        </UButton>

        <template v-if="status?.overall_status === 'RUNNING'">
          <UButton
            variant="secondary"
            @click="pauseMigration"
            :loading="isActionPending"
            data-testid="migration-pause-btn"
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
            data-testid="migration-resume-btn"
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
            data-testid="migration-start-btn"
          >
            <template #icon><Icon name="ph:rocket-launch-bold" /></template>
            Запустить миграцию
          </UButton>
        </template>
      </div>
    </template>

    <div class="migration-page">
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

          <div
            v-if="isMigrationStale"
            class="stale-warning"
            data-testid="migration-stale-warning"
          >
            <Icon name="ph:warning-bold" />
            <span>Миграция может быть зависшей. Попробуйте приостановить и возобновить.</span>
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
              <div
                v-if="entity.skipped && entity.skipped > 0"
                class="entity-skipped"
                data-testid="entity-skipped"
              >
                Пропущено: {{ entity.skipped }}
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
  </NuxtLayout>
</template>

<style scoped>
.migration-page {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-bottom: 4rem;
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

.entity-skipped {
  font-size: var(--text-xs);
  color: var(--color-warning);
  margin-top: 0.25rem;
  font-family: var(--font-mono);
}

.stale-warning {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding: 0.75rem 1rem;
  background: color-mix(in srgb, var(--color-warning) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-warning) 40%, transparent);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  color: var(--color-warning);
}

</style>
