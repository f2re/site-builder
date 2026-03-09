<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useUser, type AdminDeviceRead } from '~/composables/useUser'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import UButton from '~/components/U/UButton.vue'
import UInput from '~/components/U/UInput.vue'
import UCard from '~/components/U/UCard.vue'
import USkeleton from '~/components/U/USkeleton.vue'

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const toast = useToast()
const { confirm } = useConfirm()
const { adminGetDevices, adminPatchDevice, adminDeleteDevice } = useUser()

const searchQuery = ref('')
const isActiveFilter = ref<string>('')
const currentPage = ref(1)
const perPage = 50

const buildParams = () => {
  const params: Record<string, string | number> = {
    page: currentPage.value,
    per_page: perPage,
  }
  if (searchQuery.value) params.search = searchQuery.value
  if (isActiveFilter.value !== '') params.is_active = isActiveFilter.value
  return params
}

const queryKey = computed(() =>
  `admin-devices-p${currentPage.value}-s${searchQuery.value}-a${isActiveFilter.value}`
)

const { data, pending, error, refresh } = await adminGetDevices(computed(() => buildParams()))

const devices = computed<AdminDeviceRead[]>(() => {
  if (!data.value) return []
  if (Array.isArray(data.value)) return data.value
  if ('items' in data.value) return (data.value as { items: AdminDeviceRead[]; total: number }).items
  return []
})

const total = computed<number>(() => {
  if (!data.value) return 0
  if (Array.isArray(data.value)) return (data.value as AdminDeviceRead[]).length
  if ('total' in data.value) return (data.value as { items: AdminDeviceRead[]; total: number }).total
  return 0
})

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage)))

// Debounced search
let searchTimeout: ReturnType<typeof setTimeout> | null = null
const onSearchInput = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    refresh()
  }, 400)
}

watch(isActiveFilter, () => {
  currentPage.value = 1
  refresh()
})

const resetFilters = () => {
  searchQuery.value = ''
  isActiveFilter.value = ''
  currentPage.value = 1
  refresh()
}

// Loading states per device
const loadingIds = ref<Set<string>>(new Set())

const setLoading = (id: string, val: boolean) => {
  const next = new Set(loadingIds.value)
  if (val) next.add(id)
  else next.delete(id)
  loadingIds.value = next
}

// Toggle is_active
const handleToggleActive = async (device: AdminDeviceRead) => {
  setLoading(device.id, true)
  try {
    await adminPatchDevice(device.id, { is_active: !device.is_active })
    toast.success(
      device.is_active ? 'Устройство деактивировано' : 'Устройство активировано'
    )
    refresh()
  } catch (err: unknown) {
    const apiErr = err as { data?: { detail?: string } }
    toast.error(apiErr.data?.detail || 'Не удалось изменить статус устройства')
  } finally {
    setLoading(device.id, false)
  }
}

// Delete device
const handleDelete = async (device: AdminDeviceRead) => {
  const confirmed = await confirm({
    title: 'Удалить устройство?',
    message: `Устройство "${device.name || device.device_uid}" будет безвозвратно удалено.`,
    variant: 'danger',
    confirmLabel: 'Удалить',
    cancelLabel: 'Отмена',
  })
  if (!confirmed) return

  setLoading(device.id, true)
  try {
    await adminDeleteDevice(device.id)
    toast.success('Устройство удалено')
    refresh()
  } catch (err: unknown) {
    const apiErr = err as { data?: { detail?: string } }
    toast.error(apiErr.data?.detail || 'Не удалось удалить устройство')
  } finally {
    setLoading(device.id, false)
  }
}

const formatDate = (dateString?: string | null) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

const shortUuid = (id?: string | null) => {
  if (!id) return '—'
  return id.slice(0, 8)
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Устройства</template>

    <div class="admin-devices-page" data-testid="admin-devices-page">
      <!-- Filters -->
      <UCard class="filters-card">
        <div class="filters">
          <div class="search-box">
            <UInput
              v-model="searchQuery"
              placeholder="Поиск по UID или названию..."
              icon="ph:magnifying-glass-bold"
              @input="onSearchInput"
              data-testid="device-search-input"
            />
          </div>
          <div class="status-filter">
            <select
              v-model="isActiveFilter"
              class="native-select"
              data-testid="device-status-filter"
            >
              <option value="">Все</option>
              <option value="true">Активные</option>
              <option value="false">Неактивные</option>
            </select>
          </div>
          <UButton variant="ghost" size="sm" @click="resetFilters" data-testid="device-reset-filters">
            <template #icon><Icon name="ph:x-circle-bold" size="18" /></template>
            <span class="desktop-only">Сбросить</span>
          </UButton>
        </div>
      </UCard>

      <!-- Table -->
      <UCard class="table-card">
        <div v-if="pending" class="loading-state" data-testid="devices-loading">
          <USkeleton v-for="i in 6" :key="i" height="52px" class="mb-2" />
        </div>
        <div v-else-if="error" class="error-state" data-testid="devices-error">
          Ошибка при загрузке устройств
        </div>
        <div v-else class="admin-table-wrapper">
          <table class="admin-table">
            <thead>
              <tr>
                <th>UID</th>
                <th class="desktop-only">Название</th>
                <th class="desktop-only">Модель</th>
                <th class="desktop-only">Пользователь</th>
                <th>Статус</th>
                <th class="desktop-only">Зарегистрировано</th>
                <th class="desktop-only">Активность</th>
                <th class="desktop-only">Комментарий</th>
                <th class="actions-col">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="device in devices"
                :key="device.id"
                data-testid="device-row"
              >
                <td>
                  <div class="device-uid-cell">
                    <span class="uid-text" :title="device.device_uid">{{ device.device_uid }}</span>
                    <div class="device-meta-mobile mobile-only">
                      <span class="meta-name">{{ device.name || '—' }}</span>
                      <span class="meta-model">{{ device.model || '—' }}</span>
                    </div>
                  </div>
                </td>
                <td class="desktop-only">
                  <span class="device-name">{{ device.name || '—' }}</span>
                </td>
                <td class="desktop-only">
                  <span class="device-model">{{ device.model || '—' }}</span>
                </td>
                <td class="desktop-only">
                  <NuxtLink
                    v-if="device.user_id"
                    :to="`/admin/users/${device.user_id}`"
                    class="user-link"
                    :title="device.user_id"
                    data-testid="device-user-link"
                  >
                    {{ shortUuid(device.user_id) }}
                  </NuxtLink>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <span
                    :class="device.is_active ? 'badge-active' : 'badge-inactive'"
                    data-testid="device-status-badge"
                  >
                    {{ device.is_active ? 'Активно' : 'Неактивно' }}
                  </span>
                </td>
                <td class="desktop-only text-sm">
                  {{ formatDate(device.registered_at) }}
                </td>
                <td class="desktop-only text-sm">
                  {{ formatDate(device.last_seen_at) }}
                </td>
                <td class="desktop-only comment-cell">
                  <span :title="device.comment || undefined">{{ device.comment || '—' }}</span>
                </td>
                <td class="actions-cell">
                  <div class="actions-group">
                    <UButton
                      :variant="device.is_active ? 'ghost' : 'primary'"
                      size="sm"
                      :loading="loadingIds.has(device.id)"
                      :aria-label="device.is_active ? 'Деактивировать' : 'Активировать'"
                      data-testid="device-toggle-btn"
                      @click="handleToggleActive(device)"
                    >
                      <template #icon>
                        <Icon
                          :name="device.is_active ? 'ph:toggle-right-bold' : 'ph:toggle-left-bold'"
                          size="20"
                        />
                      </template>
                    </UButton>
                    <UButton
                      variant="ghost"
                      size="sm"
                      :loading="loadingIds.has(device.id)"
                      aria-label="Удалить устройство"
                      data-testid="device-delete-btn"
                      @click="handleDelete(device)"
                    >
                      <template #icon>
                        <Icon name="ph:trash-bold" size="20" />
                      </template>
                    </UButton>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="devices.length === 0" class="empty-state" data-testid="devices-empty">
            Устройства не найдены
          </div>
        </div>
      </UCard>

      <!-- Pagination -->
      <div v-if="total > perPage" class="pagination" data-testid="devices-pagination">
        <UButton
          variant="ghost"
          :disabled="currentPage === 1"
          data-testid="devices-prev-page"
          @click="currentPage--; refresh()"
        >
          <template #icon><Icon name="ph:caret-left-bold" /></template>
          <span class="desktop-only">Предыдущая</span>
        </UButton>
        <span class="page-info" data-testid="devices-page-info">
          Страница {{ currentPage }} из {{ totalPages }}
        </span>
        <UButton
          variant="ghost"
          :disabled="currentPage >= totalPages"
          data-testid="devices-next-page"
          @click="currentPage++; refresh()"
        >
          <span class="desktop-only">Следующая</span>
          <template #icon><Icon name="ph:caret-right-bold" /></template>
        </UButton>
      </div>
    </div>
  </NuxtLayout>
</template>

<style scoped>
.admin-devices-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filters-card :deep(.card__body) {
  padding: 12px;
}

.filters {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 200px;
}

.status-filter {
  width: auto;
}

.native-select {
  height: 44px;
  padding: 0 12px;
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: var(--radius-md);
  font-family: inherit;
  font-size: var(--text-sm);
  outline: none;
  cursor: pointer;
  min-width: 130px;
}

.native-select:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px var(--color-accent-glow);
}

.table-card :deep(.card__body) {
  padding: 0;
}

.table-card {
  overflow: hidden;
}

.actions-col,
.actions-cell {
  text-align: right;
  width: 56px;
}

@media (min-width: 768px) {
  .actions-col,
  .actions-cell {
    width: 100px;
  }
}

.actions-group {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
}

.device-uid-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.uid-text {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.device-meta-mobile {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.meta-name {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-text-2);
}

.meta-model {
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.device-name {
  font-weight: 500;
  color: var(--color-text);
  font-size: var(--text-sm);
}

.device-model {
  color: var(--color-text-2);
  font-size: var(--text-sm);
}

.user-link {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 600;
  transition: opacity var(--transition-fast);
}

.user-link:hover {
  opacity: 0.75;
  text-decoration: underline;
}

.text-muted {
  color: var(--color-muted);
  font-size: var(--text-sm);
}

.badge-active {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 700;
  background: var(--color-success-bg);
  color: var(--color-success);
  white-space: nowrap;
}

.badge-inactive {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 700;
  background: var(--color-surface-3);
  color: var(--color-text-2);
  white-space: nowrap;
}

.comment-cell {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-text-2);
  font-size: var(--text-xs);
}

.text-sm {
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.loading-state,
.error-state,
.empty-state {
  padding: 48px;
  text-align: center;
  color: var(--color-text-2);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 8px;
}

.page-info {
  font-weight: 600;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

/* mobile-only helper — duplicated for scoped context */
.mobile-only {
  display: none;
}

@media (max-width: 768px) {
  .mobile-only {
    display: flex;
  }
  .desktop-only {
    display: none;
  }
}

.mb-2 {
  margin-bottom: 8px;
}
</style>
