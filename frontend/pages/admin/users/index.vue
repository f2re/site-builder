<script setup lang="ts">
import { ref, computed, toRaw } from 'vue'
import { useUser, type UserCreate, type UserProfile } from '~/composables/useUser'
import { useToast } from '~/composables/useToast'
import UButton from '~/components/U/UButton.vue'
import UInput from '~/components/U/UInput.vue'
import UCard from '~/components/U/UCard.vue'
import UModal from '~/components/U/UModal.vue'
import USelect from '~/components/U/USelect.vue'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const toast = useToast()
const { adminGetUsers, adminCreateUser, adminSetUserBlockStatus, adminExportUsers } = useUser()

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

// Fix for TypeError: cyclic object value by mapping to clean objects
const users = computed(() => {
  if (!data.value?.items) return []
  // Create shallow copies of user objects to break potential circular references during serialization
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
    toast.error('Ошибка', 'Email и пароль обязательны')
    return
  }

  isSubmitting.value = true
  try {
    await adminCreateUser(userForm.value)
    toast.success('Успех', 'Пользователь создан')
    isModalOpen.value = false
    refresh()
    userForm.value = { email: '', full_name: '', password: '', role: 'customer' }
  } catch (err: any) {
    toast.error('Ошибка', err.data?.message || 'Не удалось создать пользователя')
  } finally {
    isSubmitting.value = false
  }
}

// Block/Unblock
const handleBlockStatus = async (user: UserProfile) => {
  const newStatus = !user.is_active
  try {
    await adminSetUserBlockStatus(user.id, newStatus)
    toast.success('Успех', `Пользователь ${newStatus ? 'разблокирован' : 'заблокирован'}`)
    refresh()
  } catch (err: any) {
    toast.error('Ошибка', err.data?.message || 'Не удалось изменить статус')
  }
}

const downloadExcel = async () => {
  try {
    const blob = await adminExportUsers()
    
    // Create a link to download the blob
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `users_export_${new Date().toISOString().split('T')[0]}.xlsx`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    
    toast.success('Экспорт завершен', 'Файл успешно скачан.')
  } catch (err) {
    toast.error('Ошибка экспорта', 'Не удалось скачать файл.')
  }
}
</script>

<template>
  <div class="admin-users-page">
    <div class="page-header">
      <h1 class="page-title">Пользователи</h1>
      <div class="flex gap-3">
        <UButton variant="ghost" @click="downloadExcel" icon="ph:file-xls-bold">
          Экспорт
        </UButton>
        <UButton variant="primary" @click="isModalOpen = true" icon="ph:user-plus-bold">
          Создать пользователя
        </UButton>
      </div>
    </div>

    <UCard class="filters-card">
      <div class="filters">
        <div class="search-box">
          <UInput
            v-model="searchQuery"
            placeholder="Поиск по email или имени..."
            icon="ph:magnifying-glass-bold"
            @input="onSearchInput"
          />
        </div>
        <div class="role-filter">
          <select v-model="selectedRole" class="native-select">
            <option value="">Все роли</option>
            <option value="customer">Покупатель</option>
            <option value="manager">Менеджер</option>
            <option value="admin">Админ</option>
          </select>
        </div>
      </div>
    </UCard>

    <UCard class="users-table-card">
      <div v-if="pending" class="loading-state">
        Загрузка...
      </div>
      <div v-else-if="error" class="error-state">
        Ошибка при загрузке данных
      </div>
      <div v-else-if="users.length === 0" class="empty-state">
        Пользователи не найдены
      </div>
      <div v-else class="table-responsive">
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>Имя</th>
              <th>Роль</th>
              <th>Статус</th>
              <th>Регистрация</th>
              <th class="actions-col">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td class="id-cell" :title="user.id">{{ user.id.substring(0, 8) }}...</td>
              <td>{{ user.email }}</td>
              <td>{{ user.full_name || '—' }}</td>
              <td>
                <span class="role-badge" :class="`role-${user.role}`">{{ user.role }}</span>
              </td>
              <td>
                <span v-if="user.is_active" class="status-active">Активен</span>
                <span v-else class="status-blocked">Заблокирован</span>
              </td>
              <td class="date-cell">
                {{ user.created_at ? new Date(user.created_at).toLocaleDateString('ru-RU') : '—' }}
              </td>
              <td class="actions-cell">
                <UButton 
                  v-if="user.is_active"
                  variant="ghost" 
                  size="sm" 
                  color="danger"
                  @click="handleBlockStatus(user)"
                >
                  Заблокировать
                </UButton>
                <UButton 
                  v-else
                  variant="ghost" 
                  size="sm" 
                  color="success"
                  @click="handleBlockStatus(user)"
                >
                  Разблокировать
                </UButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </UCard>
    
    <div class="pagination" v-if="total > 20">
      <UButton 
        variant="ghost" 
        :disabled="currentPage === 1"
        @click="currentPage--"
      >
        Назад
      </UButton>
      <span class="page-info">Страница {{ currentPage }}</span>
      <UButton 
        variant="ghost" 
        :disabled="users.length < 20"
        @click="currentPage++"
      >
        Вперед
      </UButton>
    </div>

    <!-- Modal for new user -->
    <UModal v-model="isModalOpen" title="Создать пользователя">
      <div class="space-y-4 pt-4">
        <UInput 
          v-model="userForm.email" 
          label="Email" 
          placeholder="user@example.com"
          required
        />
        <UInput 
          v-model="userForm.full_name" 
          label="Имя" 
          placeholder="Иван Иванов"
        />
        <UInput 
          v-model="userForm.password" 
          type="password"
          label="Пароль" 
          placeholder="********"
          required
        />
        <USelect 
          v-model="userForm.role" 
          label="Роль" 
          :options="roleOptions"
        />
        
        <div class="flex justify-end gap-3 mt-6">
          <UButton variant="ghost" @click="isModalOpen = false">Отмена</UButton>
          <UButton 
            variant="primary" 
            :loading="isSubmitting"
            @click="handleCreateUser"
          >
            Создать
          </UButton>
        </div>
      </div>
    </UModal>
  </div>
</template>

<style scoped>
.admin-users-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin: 0;
}

.filters-card {
  padding: 16px;
}

.filters {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-box {
  flex: 1;
  max-width: 400px;
}

.native-select {
  height: 44px;
  padding: 0 16px;
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: var(--radius-md);
  font-family: inherit;
  font-size: var(--text-sm);
  outline: none;
  cursor: pointer;
}

.native-select:focus {
  border-color: var(--color-accent);
}

.users-table-card {
  padding: 0;
  overflow: hidden;
}

.table-responsive {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.admin-table th {
  background-color: var(--color-surface-2);
  padding: 12px 16px;
  font-size: var(--text-xs);
  text-transform: uppercase;
  font-weight: 700;
  color: var(--color-text-2);
  border-bottom: 1px solid var(--color-border);
}

.admin-table td {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
  font-size: var(--text-sm);
}

.admin-table tr:last-child td {
  border-bottom: none;
}

.id-cell {
  font-family: var(--font-mono);
  color: var(--color-muted);
}

.date-cell {
  color: var(--color-text-2);
}

.actions-col {
  text-align: right;
}

.actions-cell {
  text-align: right;
}

.role-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
}

.role-customer { background-color: var(--color-surface-3); color: var(--color-text); }
.role-manager { background-color: var(--color-accent-glow); color: var(--color-accent); }
.role-admin { background-color: var(--color-error-bg); color: var(--color-error); }

.status-active { color: var(--color-success); font-weight: 600; }
.status-blocked { color: var(--color-error); font-weight: 600; }

.loading-state, .error-state, .empty-state {
  padding: 48px;
  text-align: center;
  color: var(--color-text-2);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
}

.page-info {
  font-size: var(--text-sm);
  font-weight: 600;
}

.flex { display: flex; }
.items-center { align-items: center; }
.gap-2 { gap: 0.5rem; }
.gap-3 { gap: 0.75rem; }
.justify-end { justify-content: flex-end; }
.space-y-4 > * + * { margin-top: 1rem; }
.pt-4 { padding-top: 1rem; }
.mt-6 { margin-top: 1.5rem; }
</style>
