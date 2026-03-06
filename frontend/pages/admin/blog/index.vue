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
  <div>
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <h1 class="text-xl font-bold">Блог</h1>
      <UButton to="/admin/blog/create" icon="ph:plus-bold">Новый пост</UButton>
    </div>

    <UCard class="overflow-hidden">
      <div v-if="pending" class="p-4 space-y-4">
        <USkeleton v-for="i in 5" :key="i" height="40px" />
      </div>
      <div v-else class="admin-table-wrapper">
        <table class="admin-table">
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
      </div>
    </UCard>
  </div>
</template>

<style scoped>
.title-cell {
  font-weight: 500;
  min-width: 240px;
}

.actions {
  display: flex;
  gap: 8px;
}

.space-y-4 > * + * { margin-top: 16px; }
</style>
