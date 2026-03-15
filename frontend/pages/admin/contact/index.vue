<script setup lang="ts">
import type { ContactMessage } from '~/composables/useAdminContact'

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const { getMessages } = useAdminContact()
const toast = useToast()
const router = useRouter()

const statusFilter = ref<string>('')
const cursor = ref<string | undefined>(undefined)
const limit = 20

const allItems = ref<ContactMessage[]>([])
const total = ref(0)
const nextCursor = ref<string | null>(null)
const pending = ref(false)

const queryParams = computed(() => ({
  ...(statusFilter.value && { status: statusFilter.value }),
  ...(cursor.value && { cursor: cursor.value }),
  limit,
}))

const { data, pending: fetchPending, refresh } = await getMessages(queryParams.value)

// Initialize data
watch(data, (val) => {
  if (val) {
    allItems.value = val.items
    total.value = val.total
    nextCursor.value = val.next_cursor
  }
}, { immediate: true })

// Reset on filter change
watch(statusFilter, async () => {
  cursor.value = undefined
  allItems.value = []
  await reload()
})

async function reload() {
  pending.value = true
  try {
    const { data: res } = await getMessages({
      ...(statusFilter.value && { status: statusFilter.value }),
      limit,
    })
    if (res.value) {
      allItems.value = res.value.items
      total.value = res.value.total
      nextCursor.value = res.value.next_cursor
    }
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.error('Ошибка загрузки', err.data?.detail || 'Не удалось загрузить заявки')
  } finally {
    pending.value = false
  }
}

async function loadMore() {
  if (!nextCursor.value) return
  pending.value = true
  try {
    const { data: res } = await getMessages({
      ...(statusFilter.value && { status: statusFilter.value }),
      cursor: nextCursor.value,
      limit,
    })
    if (res.value) {
      allItems.value = [...allItems.value, ...res.value.items]
      total.value = res.value.total
      nextCursor.value = res.value.next_cursor
    }
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.error('Ошибка', err.data?.detail || 'Не удалось загрузить данные')
  } finally {
    pending.value = false
  }
}

function openMessage(id: string) {
  router.push(`/admin/contact/${id}`)
}

const statusOptions = [
  { value: '', label: 'Все' },
  { value: 'NEW', label: 'Новые' },
  { value: 'READ', label: 'Прочитанные' },
  { value: 'REPLIED', label: 'Отвеченные' },
]

function getStatusVariant(status: string): 'accent' | 'warning' | 'success' | 'info' {
  if (status === 'NEW') return 'accent'
  if (status === 'REPLIED') return 'success'
  return 'info'
}

function getStatusLabel(status: string): string {
  if (status === 'NEW') return 'Новая'
  if (status === 'READ') return 'Прочитана'
  if (status === 'REPLIED') return 'Отвечено'
  return status
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function truncate(str: string, maxLen: number): string {
  if (!str) return ''
  return str.length > maxLen ? str.slice(0, maxLen) + '…' : str
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>
      <div class="page-header-title">
        <Icon name="ph:chat-circle-dots-bold" size="20" />
        <span>Обратная связь</span>
        <span v-if="total > 0" class="total-badge">{{ total }}</span>
      </div>
    </template>

    <div class="contact-page" data-testid="admin-contact-table">
      <!-- Filters -->
      <div class="filters-row">
        <select
          v-model="statusFilter"
          class="status-filter"
          data-testid="admin-contact-status-filter"
          aria-label="Фильтр по статусу"
        >
          <option
            v-for="opt in statusOptions"
            :key="opt.value"
            :value="opt.value"
          >
            {{ opt.label }}
          </option>
        </select>
      </div>

      <!-- Skeleton -->
      <div v-if="fetchPending && allItems.length === 0" class="skeleton-list">
        <USkeleton v-for="i in 5" :key="i" height="56px" />
      </div>

      <!-- Table -->
      <div v-else-if="allItems.length > 0" class="table-wrapper">
        <table class="contact-table" aria-label="Список заявок обратной связи">
          <thead>
            <tr>
              <th>Имя</th>
              <th class="desktop-col">Email</th>
              <th class="desktop-col">Тема</th>
              <th>Статус</th>
              <th class="desktop-col">Дата</th>
              <th class="actions-col">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in allItems"
              :key="item.id"
              class="contact-row"
              data-testid="admin-contact-row"
              @click="openMessage(item.id)"
            >
              <td>
                <div class="contact-name" data-testid="contact-name">{{ item.name }}</div>
                <div class="contact-meta mobile-only">{{ item.email }}</div>
              </td>
              <td class="desktop-col">
                <span class="text-muted">{{ item.email }}</span>
              </td>
              <td class="desktop-col">
                <span>{{ truncate(item.subject, 50) }}</span>
              </td>
              <td>
                <UBadge
                  :variant="getStatusVariant(item.status)"
                  size="sm"
                  data-testid="contact-status"
                >
                  {{ getStatusLabel(item.status) }}
                </UBadge>
              </td>
              <td class="desktop-col">
                <span class="text-muted text-sm">{{ formatDate(item.created_at) }}</span>
              </td>
              <td class="actions-cell" @click.stop>
                <UButton
                  variant="ghost"
                  size="sm"
                  :to="`/admin/contact/${item.id}`"
                  data-testid="contact-open-btn"
                  aria-label="Открыть заявку"
                >
                  Открыть
                </UButton>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Load more -->
        <div v-if="nextCursor" class="load-more-row">
          <UButton
            variant="secondary"
            :loading="pending"
            data-testid="admin-contact-load-more-btn"
            @click="loadMore"
          >
            Загрузить ещё
          </UButton>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else class="empty-state">
        <Icon name="ph:chat-circle-dots-bold" size="48" />
        <p>Заявок не найдено</p>
        <span v-if="statusFilter" class="text-muted text-sm">
          Попробуйте изменить фильтр
        </span>
      </div>
    </div>
  </NuxtLayout>
</template>

<style scoped>
.page-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text);
}

.total-badge {
  background: var(--color-accent-glow);
  color: var(--color-accent);
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-full);
  padding: 2px 8px;
  font-size: var(--text-xs);
  font-weight: 700;
}

.contact-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filters-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.status-filter {
  padding: 10px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  color: var(--color-text);
  font-size: var(--text-sm);
  font-family: var(--font-sans);
  cursor: pointer;
  min-height: 44px;
  transition: border-color var(--transition-fast), background-color var(--transition-theme);
  outline: none;
}

.status-filter:focus {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.table-wrapper {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.contact-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.contact-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-2);
  background: var(--color-surface-2);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.contact-table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
  vertical-align: middle;
}

.contact-row {
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.contact-row:hover {
  background: var(--color-surface-2);
}

.contact-row:last-child td {
  border-bottom: none;
}

.contact-name {
  font-weight: 600;
  color: var(--color-text);
}

.contact-meta {
  font-size: var(--text-xs);
  color: var(--color-text-2);
  margin-top: 2px;
}

.text-muted {
  color: var(--color-text-2);
}

.text-sm {
  font-size: var(--text-sm);
}

.actions-col {
  text-align: right;
  width: 100px;
}

.actions-cell {
  text-align: right;
}

.load-more-row {
  display: flex;
  justify-content: center;
  padding: 16px;
  border-top: 1px solid var(--color-border);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  color: var(--color-text-2);
  text-align: center;
  gap: 12px;
}

.mobile-only {
  display: none;
}

@media (max-width: 768px) {
  .desktop-col {
    display: none;
  }

  .mobile-only {
    display: block;
  }

  .actions-col {
    width: 80px;
  }
}
</style>
