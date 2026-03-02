<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '~/stores/authStore'
import { useToast } from '~/composables/useToast'
import UButton from '~/components/U/UButton.vue'
import UInput from '~/components/U/UInput.vue'
import UCard from '~/components/U/UCard.vue'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const config = useRuntimeConfig()
const authStore = useAuthStore()
const toast = useToast()

const searchQuery = ref('')
const selectedRole = ref('')
const currentPage = ref(1)

const buildParams = () => {
  const params: Record<string, any> = { skip: (currentPage.value - 1) * 20, limit: 20 }
  if (searchQuery.value) params.q = searchQuery.value
  if (selectedRole.value) params.role = selectedRole.value
  return params
}

const { data, pending, error, refresh } = await useFetch('/admin/users', {
  baseURL: config.public.apiBase,
  headers: {
    Authorization: `Bearer ${authStore.accessToken}`
  },
  query: computed(() => buildParams()),
  watch: [currentPage, selectedRole]
})

// Quick debounced search
let searchTimeout: any
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    refresh()
  }, 500)
}

const users = computed(() => data.value?.items || [])
const total = computed(() => data.value?.total || 0)

const downloadExcel = async () => {
  try {
    const response = await $fetch('/admin/users/export', {
      baseURL: config.public.apiBase,
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`
      },
      responseType: 'blob'
    })
    
    // Create a link to download the blob
    const url = window.URL.createObjectURL(response as Blob)
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
      <UButton variant="primary" @click="downloadExcel" icon="ph:file-xls-bold">
        Экспорт в Excel
      </UButton>
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
              <td class="date-cell">{{ new Date(user.created_at).toLocaleDateString('ru-RU') }}</td>
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
</style>
