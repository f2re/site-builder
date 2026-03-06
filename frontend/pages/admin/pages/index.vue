<script setup lang="ts">
definePageMeta({
  layout: false,
  pageTransition: false,
})

const { getPages, deletePage } = usePages()
const { data: pages, pending, refresh } = await getPages()
const toast = useToast()

const handleDelete = async (id: string) => {
  if (!confirm('Вы уверены, что хотите удалить эту страницу?')) return

  try {
    await deletePage(id)
    toast.success('Страница успешно удалена')
    refresh()
  } catch (e: any) {
    toast.error(e.message || 'Ошибка при удалении страницы')
  }
}
</script>

<template>
  <div class="admin-pages-list">
    <div class="mb-6 flex items-center justify-between">
      <h1>Управление страницами</h1>
      <NuxtLink to="/admin/pages/create" class="btn-create">
        <Icon name="ph:plus-bold" />
        <span>Создать страницу</span>
      </NuxtLink>
    </div>

    <div v-if="pending" class="loading-state">
      <Icon name="ph:spinner-gap-bold" class="spin" size="32" />
      <p>Загрузка страниц...</p>
    </div>

    <div v-else-if="!pages?.length" class="empty-state">
      <Icon name="ph:files-bold" size="48" />
      <p>Страницы не найдены</p>
      <NuxtLink to="/admin/pages/create" class="btn-primary">Создать первую страницу</NuxtLink>
    </div>

    <div v-else class="pages-grid">
      <div v-for="page in pages" :key="page.id" class="page-card">
        <div class="page-info">
          <h3 class="page-title">{{ page.title }}</h3>
          <p class="page-slug">/{{ page.slug }}</p>
        </div>
        
        <div class="page-status" :class="{ active: page.is_active }">
          {{ page.is_active ? 'Активна' : 'Черновик' }}
        </div>
        
        <div class="page-actions">
          <NuxtLink :to="`/${page.slug}`" target="_blank" class="action-btn" title="Просмотр">
            <Icon name="ph:eye-bold" />
          </NuxtLink>
          <NuxtLink :to="`/admin/pages/${page.id}`" class="action-btn" title="Редактировать">
            <Icon name="ph:pencil-simple-bold" />
          </NuxtLink>
          <button @click="handleDelete(page.id)" class="action-btn delete" title="Удалить">
            <Icon name="ph:trash-bold" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-pages-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.btn-create {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--color-accent);
  color: var(--color-on-accent);
  padding: 10px 20px;
  border-radius: var(--radius-md);
  text-decoration: none;
  font-weight: 600;
  transition: all var(--transition-fast);
}

.btn-create:hover {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-accent);
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  color: var(--color-text-2);
  text-align: center;
  gap: 16px;
}

.pages-grid {
  display: grid;
  gap: 16px;
}

.page-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.page-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-sm);
}

.page-info {
  flex: 1;
}

.page-title {
  font-size: var(--text-base);
  font-weight: 600;
  margin-bottom: 4px;
}

.page-slug {
  font-size: var(--text-xs);
  color: var(--color-muted);
  font-family: var(--font-mono);
}

.page-status {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
  background: var(--color-bg-subtle);
  color: var(--color-muted);
}

.page-status.active {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.page-actions {
  display: flex;
  gap: 8px;
  margin-left: 24px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--color-surface-2);
  color: var(--color-text-2);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
}

.action-btn:hover {
  background: var(--color-surface-3);
  color: var(--color-text);
  border-color: var(--color-border-strong);
}

.action-btn.delete:hover {
  background: var(--color-error-bg);
  color: var(--color-error);
  border-color: var(--color-error);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
