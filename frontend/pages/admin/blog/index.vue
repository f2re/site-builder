<script setup lang="ts">
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
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-xl font-bold">Блог</h1>
      <UButton to="/admin/blog/create" icon="ph:plus-bold">Новый пост</UButton>
    </div>

    <UCard class="overflow-hidden">
      <div v-if="pending" class="p-4 space-y-4">
        <USkeleton v-for="i in 5" :key="i" height="40px" />
      </div>
      <table v-else class="admin-table">
        <thead>
          <tr>
            <th>Заголовок</th>
            <th>Статус</th>
            <th>Опубликован</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="post in posts?.items" :key="post.id">
            <td class="title-cell">{{ post.title }}</td>
            <td>
              <UBadge :variant="post.status === 'published' ? 'success' : 'warning'">
                {{ post.status === 'published' ? 'Опубликован' : 'Черновик' }}
              </UBadge>
            </td>
            <td>{{ post.published_at ? new Date(post.published_at).toLocaleDateString() : '—' }}</td>
            <td>
              <div class="actions">
                <UButton variant="ghost" size="sm" :to="`/admin/blog/${post.slug}`">
                  <Icon name="ph:pencil-simple-bold" />
                </UButton>
                <UButton variant="ghost" size="sm" color="danger" @click="deletePost(post.slug)">
                  <Icon name="ph:trash-bold" />
                </UButton>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </UCard>
  </div>
</template>

<style scoped>
.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th {
  text-align: left;
  padding: 12px 16px;
  background: var(--color-surface-2);
  font-size: var(--text-xs);
  text-transform: uppercase;
  color: var(--color-text-2);
  border-bottom: 1px solid var(--color-border);
}

.admin-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
}

.title-cell {
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 8px;
}

.mb-6 { margin-bottom: 24px; }
.flex { display: flex; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.overflow-hidden { overflow: hidden; }
.p-4 { padding: 16px; }
.space-y-4 > * + * { margin-top: 16px; }
</style>
