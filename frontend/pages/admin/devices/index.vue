<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useUser, type AdminDeviceRead, type AdminDeviceCreate, type AdminDeviceUpdate } from '~/composables/useUser'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import UButton from '~/components/U/UButton.vue'
import UInput from '~/components/U/UInput.vue'
import UCard from '~/components/U/UCard.vue'
import USkeleton from '~/components/U/USkeleton.vue'
import UModal from '~/components/U/UModal.vue'
import USelect from '~/components/U/USelect.vue'
import UBadge from '~/components/U/UBadge.vue'

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const toast = useToast()
const { confirm } = useConfirm()
const { 
  adminGetDevices, 
  adminPatchDevice, 
  adminDeleteDevice, 
  adminCreateDevice, 
  adminGetDeviceModels,
  adminGetUsers,
  formatDeviceModel
} = useUser()

// State
const searchQuery = ref('')
const isActiveFilter = ref<string>('')
const modelFilter = ref<string>('')
const currentPage = ref(1)
const perPage = 50
const groupingMode = ref<'user' | 'flat'>('user')

// Models list
const { data: modelsData } = await adminGetDeviceModels()
const availableModels = computed(() => modelsData.value || ['wifi_obd2', 'wifi_obd2_advanced'])

// Fetch devices
const buildParams = () => {
  const params: Record<string, any> = {
    page: currentPage.value,
    per_page: perPage,
  }
  if (searchQuery.value) params.search = searchQuery.value
  if (isActiveFilter.value !== '') params.is_active = isActiveFilter.value === 'true'
  if (modelFilter.value) params.model = modelFilter.value
  return params
}

const { data, pending, error, refresh } = await adminGetDevices(computed(() => buildParams()))

const devices = computed<AdminDeviceRead[]>(() => data.value?.items || [])
const total = computed(() => data.value?.total || 0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage)))

// Grouping
const groupedDevices = computed(() => {
  if (groupingMode.value === 'flat') {
    return [{ id: 'all', title: 'Все устройства', items: devices.value }]
  }
  
  const groups: Record<string, { id: string, title: string, subtitle: string, items: AdminDeviceRead[] }> = {}
  
  devices.value.forEach(dev => {
    const userId = dev.user_id || 'unassigned'
    if (!groups[userId]) {
      groups[userId] = {
        id: userId,
        title: dev.user_name || 'Без имени',
        subtitle: dev.user_email || '—',
        items: []
      }
    }
    groups[userId].items.push(dev)
  })
  
  return Object.values(groups)
})

// Modals state
const isAddModalOpen = ref(false)
const isEditModalOpen = ref(false)
const currentDevice = ref<AdminDeviceRead | null>(null)

// Form state
const deviceForm = ref<AdminDeviceCreate>({
  device_uid: '',
  user_id: '',
  model: 'wifi_obd2',
  name: '',
  comment: '',
  is_active: true
})

const editForm = ref<AdminDeviceUpdate>({
  user_id: '',
  name: '',
  model: '',
  comment: '',
  is_active: true
})

// User search for creation
const userSearchQuery = ref('')
const usersList = ref<any[]>([])
const isSearchingUsers = ref(false)

const searchUsers = async () => {
  if (userSearchQuery.value.length < 2) return
  isSearchingUsers.value = true
  try {
    const { data: userData } = await adminGetUsers({ q: userSearchQuery.value, per_page: 5 })
    usersList.value = userData.value?.items || []
  } catch (err) {
    console.error(err)
  } finally {
    isSearchingUsers.value = false
  }
}

// Actions
const openAddModal = () => {
  deviceForm.value = {
    device_uid: '',
    user_id: '',
    model: availableModels.value[0] || 'wifi_obd2',
    name: '',
    comment: '',
    is_active: true
  }
  userSearchQuery.value = ''
  usersList.value = []
  isAddModalOpen.value = true
}

const openEditModal = (device: AdminDeviceRead) => {
  currentDevice.value = device
  editForm.value = {
    user_id: device.user_id,
    name: device.name,
    model: device.model,
    comment: device.comment,
    is_active: device.is_active
  }
  userSearchQuery.value = device.user_email || ''
  usersList.value = [{ id: device.user_id, email: device.user_email, full_name: device.user_name }]
  isEditModalOpen.value = true
}

const handleCreate = async () => {
  try {
    await adminCreateDevice(deviceForm.value)
    toast.success('Устройство добавлено')
    isAddModalOpen.value = false
    refresh()
  } catch (err: any) {
    toast.error(err.data?.detail || 'Ошибка при создании устройства')
  }
}

const handleUpdate = async () => {
  if (!currentDevice.value) return
  try {
    await adminPatchDevice(currentDevice.value.id, editForm.value)
    toast.success('Устройство обновлено')
    isEditModalOpen.value = false
    refresh()
  } catch (err: any) {
    toast.error(err.data?.detail || 'Ошибка при обновлении устройства')
  }
}

const handleDelete = async (device: AdminDeviceRead) => {
  const confirmed = await confirm({
    title: 'Удалить устройство?',
    message: `Устройство "${device.name || device.device_uid}" будет безвозвратно удалено.`,
    variant: 'danger',
    confirmLabel: 'Удалить',
    cancelLabel: 'Отмена',
  })
  if (!confirmed) return

  try {
    await adminDeleteDevice(device.id)
    toast.success('Устройство удалено')
    refresh()
  } catch (err: any) {
    toast.error(err.data?.detail || 'Не удалось удалить устройство')
  }
}

const handleToggleActive = async (device: AdminDeviceRead) => {
  try {
    await adminPatchDevice(device.id, { is_active: !device.is_active })
    toast.success(device.is_active ? 'Деактивировано' : 'Активировано')
    refresh()
  } catch (err: any) {
    toast.error('Ошибка при изменении статуса')
  }
}

// Helpers
const formatDate = (date?: string | null) => {
  if (!date) return '—'
  return new Date(date).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const resetFilters = () => {
  searchQuery.value = ''
  isActiveFilter.value = ''
  modelFilter.value = ''
  currentPage.value = 1
  refresh()
}

watch([searchQuery, isActiveFilter, modelFilter], () => {
  currentPage.value = 1
  refresh()
})
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Устройства</template>
    <template #header-actions>
      <UButton variant="primary" icon="ph:plus-bold" @click="openAddModal">
        Добавить устройство
      </UButton>
    </template>

    <div class="admin-devices-page" data-testid="admin-devices-page">
      <!-- Filters -->
      <UCard class="filters-card">
        <div class="filters">
          <div class="search-box">
            <UInput
              v-model="searchQuery"
              placeholder="Поиск по UID или названию..."
              icon="ph:magnifying-glass-bold"
              data-testid="device-search-input"
            />
          </div>
          <div class="filter-group">
            <USelect
              v-model="isActiveFilter"
              :options="[
                { label: 'Все статусы', value: '' },
                { label: 'Активные', value: 'true' },
                { label: 'Неактивные', value: 'false' }
              ]"
              data-testid="device-status-filter"
            />
            <USelect
              v-model="modelFilter"
              :options="[
                { label: 'Все модели', value: '' },
                ...availableModels.map(m => ({ label: formatDeviceModel(m), value: m }))
              ]"
              data-testid="device-model-filter"
            />
            <USelect
              v-model="groupingMode"
              :options="[
                { label: 'Группировка: Пользователь', value: 'user' },
                { label: 'Плоский список', value: 'flat' }
              ]"
            />
          </div>
          <UButton variant="ghost" size="sm" @click="resetFilters">
            Сбросить
          </UButton>
        </div>
      </UCard>

      <!-- Content -->
      <div v-if="pending" class="loading-state">
        <USkeleton v-for="i in 3" :key="i" height="200px" class="mb-4" />
      </div>
      
      <div v-else-if="groupedDevices.length === 0" class="empty-state">
        <Icon name="ph:cpu-bold" size="48" class="mb-2" />
        <p>Устройства не найдены</p>
      </div>

      <div v-else class="groups-container">
        <div v-for="group in groupedDevices" :key="group.id" class="device-group">
          <div v-if="groupingMode === 'user' && group.id !== 'unassigned'" class="group-header">
            <NuxtLink :to="`/admin/users/${group.id}`" class="group-title">
              {{ group.title }}
              <span class="group-subtitle">{{ group.subtitle }}</span>
            </NuxtLink>
            <UBadge variant="secondary">{{ group.items.length }}</UBadge>
          </div>
          <div v-else-if="groupingMode === 'flat'" class="group-header">
            <span class="group-title">{{ group.title }}</span>
            <UBadge variant="secondary">{{ total }}</UBadge>
          </div>

          <div class="devices-grid">
            <div v-for="device in group.items" :key="device.id" class="device-card-wrapper">
              <UCard class="device-card" @click="openEditModal(device)">
                <div class="device-card-header">
                  <code class="device-uid">{{ device.device_uid }}</code>
                  <UBadge :variant="device.is_active ? 'success' : 'secondary'">
                    {{ device.is_active ? 'Активен' : 'Отключен' }}
                  </UBadge>
                </div>
                
                <div class="device-card-body">
                  <div class="main-info">
                    <h4 class="device-name">{{ device.name || 'Без названия' }}</h4>
                    <span class="device-model">{{ formatDeviceModel(device.model) }}</span>
                  </div>
                  
                  <div class="meta-info">
                    <div class="meta-item">
                      <Icon name="ph:calendar-bold" />
                      <span>Рег: {{ formatDate(device.registered_at) }}</span>
                    </div>
                    <div class="meta-item" v-if="device.last_seen_at">
                      <Icon name="ph:broadcast-bold" />
                      <span>Был: {{ formatDate(device.last_seen_at) }}</span>
                    </div>
                  </div>
                </div>

                <div class="device-card-actions" @click.stop>
                  <UButton variant="ghost" size="sm" @click="handleToggleActive(device)">
                    <Icon :name="device.is_active ? 'ph:toggle-right-fill' : 'ph:toggle-left'" size="20" />
                  </UButton>
                  <UButton variant="ghost" size="sm" @click="handleDelete(device)">
                    <Icon name="ph:trash-bold" size="18" />
                  </UButton>
                </div>
              </UCard>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="total > perPage" class="pagination-footer">
        <p class="pagination-info">Показано {{ (currentPage - 1) * perPage + 1 }} - {{ Math.min(currentPage * perPage, total) }} из {{ total }}</p>
        <div class="pagination-controls">
          <UButton variant="ghost" :disabled="currentPage === 1" @click="currentPage--">Назад</UButton>
          <span class="page-num">{{ currentPage }} / {{ totalPages }}</span>
          <UButton variant="ghost" :disabled="currentPage === totalPages" @click="currentPage++">Вперед</UButton>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <UModal v-model="isAddModalOpen" title="Добавить устройство">
      <div class="device-form">
        <div class="form-section">
          <label>Пользователь</label>
          <UInput 
            v-model="userSearchQuery" 
            placeholder="Поиск по email или имени..." 
            @input="searchUsers"
          />
          <div v-if="usersList.length > 0" class="user-search-results">
            <div 
              v-for="user in usersList" 
              :key="user.id" 
              class="user-result-item"
              :class="{ selected: deviceForm.user_id === user.id }"
              @click="deviceForm.user_id = user.id; userSearchQuery = user.email"
            >
              <span class="user-email">{{ user.email }}</span>
              <span class="user-name">{{ user.full_name }}</span>
            </div>
          </div>
        </div>

        <div class="form-grid">
          <div class="form-section">
            <label>UID (S/N)</label>
            <UInput v-model="deviceForm.device_uid" placeholder="MAC или Serial" />
          </div>
          <div class="form-section">
            <label>Модель</label>
            <USelect v-model="deviceForm.model" :options="availableModels.map(m => ({ label: formatDeviceModel(m), value: m }))" />
          </div>
        </div>

        <div class="form-section">
          <label>Название (опционально)</label>
          <UInput v-model="deviceForm.name" placeholder="Напр. Машина жены" />
        </div>

        <div class="form-section">
          <label>Комментарий</label>
          <UInput v-model="deviceForm.comment" placeholder="Служебная заметка..." />
        </div>
      </div>
      <template #footer>
        <UButton variant="ghost" @click="isAddModalOpen = false">Отмена</UButton>
        <UButton variant="primary" :disabled="!deviceForm.user_id || !deviceForm.device_uid" @click="handleCreate">Создать</UButton>
      </template>
    </UModal>

    <!-- Edit Modal -->
    <UModal v-model="isEditModalOpen" title="Редактировать устройство">
      <div class="device-form">
        <div class="form-section">
          <label>Владелец</label>
          <UInput 
            v-model="userSearchQuery" 
            placeholder="Сменить владельца (email)..." 
            @input="searchUsers"
          />
          <div v-if="usersList.length > 0" class="user-search-results">
            <div 
              v-for="user in usersList" 
              :key="user.id" 
              class="user-result-item"
              :class="{ selected: editForm.user_id === user.id }"
              @click="editForm.user_id = user.id; userSearchQuery = user.email"
            >
              <span class="user-email">{{ user.email }}</span>
            </div>
          </div>
        </div>

        <div class="form-grid">
          <div class="form-section">
            <label>Название</label>
            <UInput v-model="editForm.name" />
          </div>
          <div class="form-section">
            <label>Модель</label>
            <USelect v-model="editForm.model" :options="availableModels.map(m => ({ label: formatDeviceModel(m), value: m }))" />
          </div>
        </div>

        <div class="form-section">
          <label>Комментарий</label>
          <UInput v-model="editForm.comment" />
        </div>

        <div class="form-section">
          <label class="checkbox-label">
            <input type="checkbox" v-model="editForm.is_active" />
            Устройство активно
          </label>
        </div>
      </div>
      <template #footer>
        <UButton variant="ghost" @click="isEditModalOpen = false">Отмена</UButton>
        <UButton variant="primary" @click="handleUpdate">Сохранить</UButton>
      </template>
    </UModal>
  </NuxtLayout>
</template>

<style scoped>
.admin-devices-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filters {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
}

.filter-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.groups-container {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.device-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

.group-title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
  display: flex;
  flex-direction: column;
  text-decoration: none;
}

.group-subtitle {
  font-size: var(--text-xs);
  font-weight: 400;
  color: var(--color-text-2);
}

.devices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.device-card {
  height: 100%;
  cursor: pointer;
  transition: transform 0.2s;
  position: relative;
}

.device-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-accent);
}

.device-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.device-uid {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-2);
  background: var(--color-surface-2);
  padding: 2px 6px;
  border-radius: 4px;
}

.device-name {
  font-size: var(--text-base);
  font-weight: 700;
  margin: 0;
}

.device-model {
  font-size: var(--text-xs);
  color: var(--color-accent);
  text-transform: uppercase;
  font-weight: 600;
}

.meta-info {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-xs);
  color: var(--color-text-2);
}

.device-card-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  display: none;
  gap: 4px;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.device-card:hover .device-card-actions {
  display: flex;
}

.pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.pagination-info {
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.device-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-section label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
}

.user-search-results {
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-top: 4px;
  max-height: 150px;
  overflow-y: auto;
}

.user-result-item {
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.user-result-item:hover {
  background: var(--color-surface-3);
}

.user-result-item.selected {
  background: var(--color-accent-glow);
  border-left: 3px solid var(--color-accent);
}

.user-email {
  font-size: var(--text-sm);
  font-weight: 600;
}

.user-name {
  font-size: var(--text-xs);
  color: var(--color-text-2);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-sm);
  cursor: pointer;
}

@media (max-width: 768px) {
  .devices-grid {
    grid-template-columns: 1fr;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
