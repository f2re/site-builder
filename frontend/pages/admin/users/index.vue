<script setup lang="ts">
import { ref, computed, toRaw } from 'vue'
import { useUser, type UserCreate, type UserProfile, type UserAdminUpdate } from '~/composables/useUser'
import { useToast } from '~/composables/useToast'
import UButton from '~/components/U/UButton.vue'
import UInput from '~/components/U/UInput.vue'
import UCard from '~/components/U/UCard.vue'
import UModal from '~/components/U/UModal.vue'
import USelect from '~/components/U/USelect.vue'
import UserAddressesList from '~/components/Admin/UserAddressesList.vue'

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const toast = useToast()
const { adminGetUsers, adminCreateUser, adminSetUserBlockStatus, adminExportUsers, adminUpdateUser } = useUser()

const searchQuery = ref('')
const selectedRole = ref('')
const currentPage = ref(1)

const buildParams = () => {
  const params: Record<string, any> = { skip: (currentPage.value - 1) * 20, limit: 20 }
  if (searchQuery.value) params.q = searchQuery.value
  if (selectedRole.value) params.role = selectedRole.value
  return params
}

const { data, pending, error, refresh } = await adminGetUsers(computed(() => buildParams()))

// Debounced search
let searchTimeout: any
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    refresh()
  }, 500)
}

const users = computed(() => {
  if (!data.value?.items) return []
  return data.value.items.map(u => ({ ...toRaw(u) }))
})
const total = computed(() => data.value?.total || 0)

// User Creation
const isModalOpen = ref(false)
const isSubmitting = ref(false)
const userForm = ref<UserCreate>({
  email: '',
  full_name: '',
  password: '',
  role: 'customer'
})

const roleOptions = [
  { label: 'Покупатель', value: 'customer' },
  { label: 'Менеджер', value: 'manager' },
  { label: 'Админ', value: 'admin' }
]

const handleCreateUser = async () => {
  if (!userForm.value.email || !userForm.value.password) {
    toast.error('Email и пароль обязательны')
    return
  }

  isSubmitting.value = true
  try {
    await adminCreateUser(userForm.value)
    toast.success('Пользователь создан')
    isModalOpen.value = false
    refresh()
    userForm.value = { email: '', full_name: '', password: '', role: 'customer' }
  } catch (err: any) {
    toast.error(err.data?.message || 'Не удалось создать пользователя')
  } finally {
    isSubmitting.value = false
  }
}

// Edit user
const isEditModalOpen = ref(false)
const editingUser = ref<UserProfile | null>(null)
const isEditSubmitting = ref(false)

const editForm = ref<UserAdminUpdate>({
  full_name: '',
  email: '',
  phone: '',
  role: 'customer',
  is_active: true,
})

const openEditModal = (user: UserProfile) => {
  editingUser.value = user
  editForm.value = {
    full_name: user.full_name || '',
    email: user.email || '',
    phone: user.phone || '',
    role: user.role,
    is_active: user.is_active,
  }
  isEditModalOpen.value = true
}

const handleUpdateUser = async () => {
  if (!editingUser.value) return
  isEditSubmitting.value = true
  try {
    await adminUpdateUser(editingUser.value.id, editForm.value)
    toast.success('Пользователь обновлён')
    isEditModalOpen.value = false
    refresh()
  } catch (err: unknown) {
    const apiErr = err as { data?: { message?: string; detail?: string } }
    toast.error(apiErr.data?.message || apiErr.data?.detail || 'Не удалось обновить пользователя')
  } finally {
    isSubmitting.value = false
  }
}

// Block/Unblock
const handleBlockStatus = async (user: UserProfile) => {
  const newStatus = !user.is_active
  try {
    await adminSetUserBlockStatus(user.id, newStatus)
    toast.success(`Пользователь ${newStatus ? 'разблокирован' : 'заблокирован'}`)
    refresh()
  } catch (err: any) {
    toast.error(err.data?.message || 'Не удалось изменить статус')
  }
}

const downloadExcel = async () => {
  try {
    const blob = await adminExportUsers()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `users_export_${new Date().toISOString().split('T')[0]}.xlsx`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    toast.success('Экспорт завершен')
  } catch (err) {
    toast.error('Не удалось скачать файл')
  }
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Пользователи</template>
    <template #header-actions>
      <div class="flex gap-2">
        <UButton variant="ghost" @click="downloadExcel" class="desktop-only">
          <template #icon><Icon name="ph:file-xls-bold" /></template>
          Экспорт
        </UButton>
        <UButton variant="primary" @click="isModalOpen = true" data-testid="admin-add-user-btn">
          <template #icon><Icon name="ph:user-plus-bold" /></template>
          <span class="desktop-only">Создать</span>
        </UButton>
      </div>
    </template>

    <div class="admin-users-page">
      <UCard class="filters-card">
        <div class="filters">
          <div class="search-box">
            <UInput
              v-model="searchQuery"
              placeholder="Поиск..."
              icon="ph:magnifying-glass-bold"
              @input="onSearchInput"
              data-testid="search-input"
            />
          </div>
          <div class="role-filter">
            <select v-model="selectedRole" class="native-select" @change="refresh" data-testid="role-filter">
              <option value="">Все роли</option>
              <option value="customer">Покупатель</option>
              <option value="manager">Менеджер</option>
              <option value="admin">Админ</option>
            </select>
          </div>
          <UButton variant="ghost" @click="downloadExcel" class="mobile-only" aria-label="Экспорт">
            <template #icon><Icon name="ph:file-xls-bold" /></template>
          </UButton>
        </div>
      </UCard>

      <UCard class="table-card">
        <div v-if="pending" class="loading-state">
          <USkeleton v-for="i in 5" :key="i" height="52px" class="mb-2" />
        </div>
        <div v-else-if="error" class="error-state">
          Ошибка при загрузке данных
        </div>
        <div v-else class="admin-table-wrapper">
          <table class="admin-table">
            <thead>
              <tr>
                <th>Пользователь</th>
                <th class="desktop-only">Роль</th>
                <th class="desktop-only">Статус</th>
                <th class="desktop-only">Регистрация</th>
                <th class="actions-col">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" data-testid="user-row">
                <td>
                  <div class="user-info">
                    <span class="user-name truncate" data-testid="user-name">{{ user.full_name || 'Без имени' }}</span>
                    <span class="user-email truncate">{{ user.email }}</span>
                    <div class="user-meta mobile-only">
                      <span class="role-badge" :class="`role-${user.role}`">{{ user.role }}</span>
                      <span v-if="user.is_active" class="status-active">● Активен</span>
                      <span v-else class="status-blocked">● Заблокирован</span>
                    </div>
                  </div>
                </td>
                <td class="desktop-only">
                  <span class="role-badge" :class="`role-${user.role}`">{{ user.role }}</span>
                </td>
                <td class="desktop-only">
                  <span v-if="user.is_active" class="status-active">Активен</span>
                  <span v-else class="status-blocked">Заблокирован</span>
                </td>
                <td class="desktop-only">
                  {{ user.created_at ? new Date(user.created_at).toLocaleDateString('ru-RU') : '—' }}
                </td>
                <td class="actions-cell">
                  <div class="actions-group">
                    <UButton
                      :to="`/admin/users/${user.id}`"
                      variant="ghost"
                      size="sm"
                      aria-label="Подробнее"
                      data-testid="view-user-btn"
                    >
                      <template #icon>
                        <Icon name="ph:eye-bold" size="20" />
                      </template>
                    </UButton>
                    <UButton
                      variant="ghost"
                      size="sm"
                      aria-label="Редактировать"
                      data-testid="edit-user-btn"
                      @click="openEditModal(user)"
                    >
                      <template #icon>
                        <Icon name="ph:pencil-simple-bold" size="20" />
                      </template>
                    </UButton>
                    <UButton
                      :variant="user.is_active ? 'ghost' : 'primary'"
                      size="sm"
                      @click="handleBlockStatus(user)"
                      :aria-label="user.is_active ? 'Заблокировать' : 'Разблокировать'"
                      data-testid="block-unblock-btn"
                    >
                      <template #icon>
                        <Icon :name="user.is_active ? 'ph:user-minus-bold' : 'ph:user-plus-bold'" size="20" />
                      </template>
                    </UButton>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="users.length === 0" class="empty-state" data-testid="empty-state">
            Пользователи не найдены
          </div>
        </div>
      </UCard>
      
      <div class="pagination" v-if="total > 20">
        <UButton variant="ghost" :disabled="currentPage === 1" @click="currentPage--" data-testid="prev-page">
          <template #icon><Icon name="ph:caret-left-bold" /></template>
        </UButton>
        <span class="page-info" data-testid="current-page">{{ currentPage }}</span>
        <UButton variant="ghost" :disabled="users.length < 20" @click="currentPage++" data-testid="next-page">
          <template #icon><Icon name="ph:caret-right-bold" /></template>
        </UButton>
      </div>

      <!-- Modal for new user -->
      <UModal v-model="isModalOpen" title="Новый пользователь">
        <div class="space-y-4 pt-4">
          <UInput v-model="userForm.email" label="Email" placeholder="user@example.com" required data-testid="email-input" />
          <UInput v-model="userForm.full_name" label="Имя" placeholder="Иван Иванов" data-testid="name-input" />
          <UInput v-model="userForm.password" type="password" label="Пароль" placeholder="********" required data-testid="password-input" />
          <USelect v-model="userForm.role" label="Роль" :options="roleOptions" data-testid="role-select" />

          <div class="flex flex-col gap-3 mt-6 sm:flex-row sm:justify-end">
            <UButton variant="ghost" @click="isModalOpen = false" class="sm:order-1" data-testid="modal-cancel-btn">Отмена</UButton>
            <UButton variant="primary" :loading="isSubmitting" @click="handleCreateUser" class="sm:order-2" data-testid="modal-submit-btn">Создать</UButton>
          </div>
        </div>
      </UModal>

      <!-- Modal for editing user -->
      <UModal v-model="isEditModalOpen" title="Редактировать пользователя" data-testid="edit-user-modal">
        <div v-if="editingUser" class="space-y-4 pt-4">
          <div class="user-edit-id">
            <span class="text-muted">ID: {{ editingUser.id }}</span>
          </div>
          <UInput v-model="editForm.full_name" label="Имя" placeholder="Иван Иванов" data-testid="edit-name-input" />
          <UInput v-model="editForm.email" label="Email" placeholder="user@example.com" data-testid="edit-email-input" />
          <UInput v-model="editForm.phone" label="Телефон" placeholder="+7 999 000 00 00" data-testid="edit-phone-input" />
          <USelect v-model="editForm.role" label="Роль" :options="roleOptions" data-testid="edit-role-select" />
          <div class="toggle-row">
            <label class="toggle-label" for="edit-active-toggle">Активен</label>
            <input
              id="edit-active-toggle"
              v-model="editForm.is_active"
              type="checkbox"
              class="toggle-checkbox"
              data-testid="edit-active-toggle"
            />
          </div>

          <div class="addresses-section">
            <h4>Адреса доставки</h4>
            <UserAddressesList :user-id="editingUser.id" />
          </div>

          <div class="flex flex-col gap-3 mt-6 sm:flex-row sm:justify-end">
            <UButton variant="ghost" data-testid="edit-cancel-btn" @click="isEditModalOpen = false">Отмена</UButton>
            <UButton variant="primary" :loading="isEditSubmitting" data-testid="edit-submit-btn" @click="handleUpdateUser">Сохранить</UButton>
          </div>
        </div>
      </UModal>
    </div>
  </NuxtLayout>
</template>

<style scoped>
.admin-users-page {
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
}

.search-box {
  flex: 1;
}

.role-filter {
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
  min-width: 120px;
}

.table-card :deep(.card__body) {
  padding: 0;
}

.table-card {
  overflow: hidden;
}

/* Override admin-table for specific needs */
.admin-table {
  table-layout: fixed;
}

/* Column widths */
.admin-table th:nth-child(1),
.admin-table td:nth-child(1) {
  width: auto;
}

@media (min-width: 768px) {
  .admin-table th:nth-child(1),
  .admin-table td:nth-child(1) {
    width: 30%;
  }
  .admin-table th.desktop-only,
  .admin-table td.desktop-only {
    width: 15%;
  }
}

.actions-col, .actions-cell {
  text-align: right;
  width: 56px;
}

@media (min-width: 768px) {
  .actions-col, .actions-cell {
    width: 150px;
  }
}

.actions-group {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0; /* Critical for truncate */
}

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-name {
  font-weight: 600;
  color: var(--color-text);
  font-size: var(--text-sm);
}

.user-email {
  color: var(--color-text-2);
  font-size: var(--text-xs);
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  font-size: 10px;
}

.role-badge {
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-weight: 700;
  text-transform: uppercase;
  font-size: 10px;
  display: inline-block;
}

.role-customer { background: var(--color-surface-3); color: var(--color-text-2); }
.role-manager { background: var(--color-info-bg); color: var(--color-info); }
.role-admin { background: var(--color-accent-glow); color: var(--color-accent); }

.status-active { color: var(--color-success); font-weight: 600; }
.status-blocked { color: var(--color-error); font-weight: 600; }

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
}

.loading-state, .error-state, .empty-state {
  padding: 48px;
  text-align: center;
  color: var(--color-text-2);
}

/* Utilities not in main.css */
.ml-2 { margin-left: 8px; }
.pt-4 { padding-top: 16px; }
.mt-6 { margin-top: 24px; }
.gap-3 { gap: 12px; }
@media (min-width: 640px) {
  .sm\:order-1 { order: 1; }
  .sm\:order-2 { order: 2; }
  .sm\:flex-row { flex-direction: row; }
  .sm\:justify-end { justify-content: flex-end; }
}

/* Edit modal styles */
.space-y-4 > * + * { margin-top: 16px; }

.flex { display: flex; }
.flex-col { flex-direction: column; }

.user-edit-id {
  margin-bottom: 4px;
}

.text-muted {
  color: var(--color-muted);
  font-size: var(--text-xs);
  font-family: var(--font-mono);
}

.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
}

.toggle-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
}

.toggle-checkbox {
  width: 20px;
  height: 20px;
  accent-color: var(--color-accent);
  cursor: pointer;
}

.addresses-section {
  border-top: 1px solid var(--color-border);
  padding-top: 16px;
  margin-top: 16px;
}

.addresses-section h4 {
  font-size: var(--text-sm);
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--color-text);
}
</style>
