<script setup lang="ts">
import UButton from '~/components/U/UButton.vue'
import UCard from '~/components/U/UCard.vue'
import UBadge from '~/components/U/UBadge.vue'
import USkeleton from '~/components/U/USkeleton.vue'
import { useConfirm } from '~/composables/useConfirm'
import type { BlogListResponse } from '~/composables/useBlog'

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const router = useRouter()
const { confirm } = useConfirm()
const apiFetch = useApiFetch()

// Cursor-based pagination state
const currentCursor = ref<string | null>(null)
const cursorHistory = ref<(string | null)[]>([null]) // history[0] = null (first page)
const currentPage = ref(0)

const { data: postsData, pending, refresh } = await useApi<BlogListResponse>('/blog/posts', {
  params: computed(() => ({
    per_page: 20,
    status: 'all',
    ...(currentCursor.value ? { after: currentCursor.value } : {}),
  })),
  watch: [currentCursor],
})

const { deletePost: apiDeletePost } = useBlog()

const posts = computed(() => postsData.value?.items ?? [])
const nextCursor = computed(() => postsData.value?.next_cursor ?? null)
const total = computed(() => postsData.value?.total ?? 0)
const hasNext = computed(() => nextCursor.value !== null)
const hasPrev = computed(() => currentPage.value > 0)

function goNext() {
  if (!hasNext.value) return
  const next = nextCursor.value!
  cursorHistory.value = [...cursorHistory.value.slice(0, currentPage.value + 1), next]
  currentPage.value += 1
  currentCursor.value = next
}

function goPrev() {
  if (!hasPrev.value) return
  currentPage.value -= 1
  currentCursor.value = cursorHistory.value[currentPage.value]
}

function formatDate(dateStr?: string | null, fallback?: string | null): string {
  const raw = dateStr || fallback
  if (!raw) return '—'
  const d = new Date(raw)
  if (isNaN(d.getTime()) || d.getFullYear() < 2000) return '—'
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function deletePost(id: string) {
  if (!await confirm({ title: 'Удалить статью?', message: 'Это действие нельзя отменить.', confirmLabel: 'Удалить', variant: 'danger' })) return
  try {
    await apiDeletePost(id)
    await refresh()
  } catch (e) {
    console.error(e)
  }
}

</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Блог</template>
    <template #header-actions>
      <UButton to="/admin/blog/create" data-testid="admin-blog-create-btn">
        <template #icon><Icon name="ph:plus-bold" /></template>
        <span class="desktop-only">Новый пост</span>
      </UButton>
    </template>

    <div class="admin-blog-index">
      <UCard class="table-card">
      <div v-if="pending" class="p-4 space-y-4">
        <USkeleton v-for="i in 5" :key="i" height="48px" />
      </div>
      <div v-else class="admin-table-wrapper">
        <table class="admin-table" data-testid="admin-blog-table">
          <thead>
            <tr>
              <th>Заголовок</th>
              <th class="desktop-only">Статус</th>
              <th class="desktop-only">Опубликован</th>
              <th class="actions-col">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="post in posts"
              :key="post.id"
              class="post-row"
              data-testid="admin-blog-post-row"
              @click="router.push('/admin/blog/' + post.slug)"
            >
              <td class="title-cell">
                <div class="post-info">
                  <NuxtLink
                    :to="`/admin/blog/${post.slug}`"
                    class="post-title post-title--link truncate"
                    @click.stop
                  >{{ post.title }}</NuxtLink>
                  <div class="post-meta mobile-only">
                    <UBadge :variant="post.status === 'published' ? 'success' : 'warning'" size="sm">
                      {{ post.status === 'published' ? 'Опубликован' : 'Черновик' }}
                    </UBadge>
                    <span class="date">{{ formatDate(post.published_at, post.created_at) }}</span>
                  </div>
                </div>
              </td>
              <td class="desktop-only">
                <UBadge :variant="post.status === 'published' ? 'success' : 'warning'">
                  {{ post.status === 'published' ? 'Опубликован' : 'Черновик' }}
                </UBadge>
              </td>
              <td class="desktop-only">{{ formatDate(post.published_at, post.created_at) }}</td>
              <td class="actions-cell" @click.stop>
                <div class="actions">
                  <UButton variant="ghost" size="sm" :to="`/admin/blog/${post.slug}`" data-testid="admin-blog-edit-btn" aria-label="Редактировать">
                    <template #icon><Icon name="ph:pencil-simple-bold" size="20" /></template>
                  </UButton>
                  <UButton variant="danger" size="sm" @click="deletePost(post.id)" data-testid="admin-blog-delete-btn" aria-label="Удалить">
                    <template #icon><Icon name="ph:trash-bold" size="20" /></template>
                  </UButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="!posts.length" class="empty-state">
          Посты не найдены
        </div>

        <!-- Pagination controls -->
        <div v-if="total > 0" class="pagination" data-testid="admin-blog-pagination">
          <span class="pagination-info">Всего: {{ total }}</span>
          <div class="pagination-controls">
            <UButton
              variant="ghost"
              size="sm"
              :disabled="!hasPrev"
              data-testid="admin-blog-prev-btn"
              @click="goPrev"
            >
              <template #icon><Icon name="ph:caret-left-bold" /></template>
              Назад
            </UButton>
            <UButton
              variant="ghost"
              size="sm"
              :disabled="!hasNext"
              data-testid="admin-blog-next-btn"
              @click="goNext"
            >
              Далее
              <template #icon><Icon name="ph:caret-right-bold" /></template>
            </UButton>
          </div>
        </div>
      </div>
    </UCard>
  </div>
  </NuxtLayout>
</template>

<style scoped>
.admin-blog-index {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.table-card {
  overflow: hidden;
}

.table-card :deep(.card__body) {
  padding: 0;
}

.admin-table {
  table-layout: fixed;
}

.admin-table th:nth-child(1),
.admin-table td:nth-child(1) {
  width: auto;
}

@media (min-width: 768px) {
  .admin-table th:nth-child(1),
  .admin-table td:nth-child(1) {
    width: 50%;
  }
}

.title-cell {
  min-width: 0;
}

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.post-title {
  font-weight: 600;
  color: var(--color-text);
  font-size: var(--text-sm);
}

.post-title--link {
  text-decoration: none;
  color: var(--color-text);
  transition: color var(--transition-fast);
}

.post-title--link:hover {
  color: var(--color-accent);
}

.post-row {
  cursor: pointer;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-xs);
  color: var(--color-text-2);
}

.actions-col, .actions-cell {
  text-align: right;
  width: 120px;
}

.actions {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
}

.empty-state {
  padding: 48px;
  text-align: center;
  color: var(--color-text-2);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid var(--color-border);
}

.pagination-info {
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.pagination-controls {
  display: flex;
  gap: 8px;
}

.p-4 { padding: 16px; }
.space-y-4 > * + * { margin-top: 16px; }
</style>
