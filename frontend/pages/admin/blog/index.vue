<script setup lang="ts">
import UButton from '~/components/U/UButton.vue'
import UCard from '~/components/U/UCard.vue'
import UBadge from '~/components/U/UBadge.vue'
import USkeleton from '~/components/U/USkeleton.vue'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { data: posts, pending, refresh } = await useApi<any>('/blog/posts')
const apiFetch = useApiFetch()

async function deletePost(slug: string) {
  if (!confirm('Удалить статью?')) return
  try {
    await apiFetch(`/blog/posts/${slug}`, {
      method: 'DELETE',
    })
    await refresh()
  } catch (e) {
    console.error(e)
  }
}
</script>

<template>
  <div class="admin-blog-index">
    <template #header-title>Блог</template>
    <template #header-actions>
      <UButton to="/admin/blog/create" icon="ph:plus-bold" data-testid="admin-blog-create-btn">
        <span class="desktop-only">Новый пост</span>
      </UButton>
    </template>

    <UCard class="table-card">
      <div v-if="pending" class="p-4 space-y-4">
        <USkeleton v-for="i in 5" :key="i" height="48px" />
      </div>
      <div v-else class="admin-table-wrapper">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Заголовок</th>
              <th class="desktop-only">Статус</th>
              <th class="desktop-only">Опубликован</th>
              <th class="actions-col">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="post in posts?.items" :key="post.id">
              <td class="title-cell">
                <div class="post-info">
                  <span class="post-title">{{ post.title }}</span>
                  <div class="post-meta mobile-only">
                    <UBadge :variant="post.status === 'published' ? 'success' : 'warning'" size="sm">
                      {{ post.status === 'published' ? 'Опубликован' : 'Черновик' }}
                    </UBadge>
                    <span class="date">{{ post.published_at ? new Date(post.published_at).toLocaleDateString() : '—' }}</span>
                  </div>
                </div>
              </td>
              <td class="desktop-only">
                <UBadge :variant="post.status === 'published' ? 'success' : 'warning'">
                  {{ post.status === 'published' ? 'Опубликован' : 'Черновик' }}
                </UBadge>
              </td>
              <td class="desktop-only">{{ post.published_at ? new Date(post.published_at).toLocaleDateString() : '—' }}</td>
              <td class="actions-cell">
                <div class="actions">
                  <UButton variant="ghost" size="sm" :to="`/admin/blog/${post.slug}`" data-testid="admin-blog-edit-btn">
                    <Icon name="ph:pencil-simple-bold" size="20" />
                  </UButton>
                  <UButton variant="ghost" size="sm" color="danger" @click="deletePost(post.slug)" data-testid="admin-blog-delete-btn">
                    <Icon name="ph:trash-bold" size="20" />
                  </UButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!posts?.items?.length" class="empty-state">
          Посты не найдены
        </div>
      </div>
    </UCard>
  </div>
</template>

<style scoped>
.admin-blog-index {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.table-card {
  padding: 0;
  overflow: hidden;
}

.admin-table-wrapper {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.admin-table th {
  padding: 12px 16px;
  background: var(--color-surface-2);
  font-size: var(--text-xs);
  text-transform: uppercase;
  color: var(--color-text-2);
  border-bottom: 1px solid var(--color-border);
  font-weight: 700;
}

.admin-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
}

.title-cell {
  min-width: 200px;
}

.post-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.post-title {
  font-weight: 600;
  color: var(--color-text);
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
  width: 100px;
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

.desktop-only {
  display: none;
}

@media (min-width: 768px) {
  .desktop-only {
    display: table-cell;
  }
  
  span.desktop-only {
    display: inline;
  }
}

.mobile-only {
  display: flex;
}

@media (min-width: 768px) {
  .mobile-only {
    display: none;
  }
}

.p-4 { padding: 16px; }
.space-y-4 > * + * { margin-top: 16px; }
</style>
