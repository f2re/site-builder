<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useProducts, type ProductCategory } from '~/composables/useProducts'
import { useToast } from '~/composables/useToast'
import UButton from '~/components/U/UButton.vue'
import UInput from '~/components/U/UInput.vue'
import UCard from '~/components/U/UCard.vue'
import UModal from '~/components/U/UModal.vue'

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const toast = useToast()
const { adminGetCategories, adminCreateCategory, adminUpdateCategory, adminDeleteCategory } = useProducts()

const { data, pending, error, refresh } = await adminGetCategories()
const categories = computed(() => data.value || [])

const isModalOpen = ref(false)
const isSubmitting = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const editingId = ref<string | null>(null)

const form = ref({
  name: '',
  slug: '',
  parent_id: null as string | null
})

const openCreateModal = () => {
  modalMode.value = 'create'
  editingId.value = null
  form.value = { name: '', slug: '', parent_id: null }
  isModalOpen.value = true
}

const openEditModal = (category: ProductCategory) => {
  modalMode.value = 'edit'
  editingId.value = category.id
  form.value = { 
    name: category.name, 
    slug: category.slug, 
    parent_id: category.parent_id 
  }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

// Slug auto-generation
watch(() => form.value.name, (newName) => {
  if (newName && !form.value.slug && modalMode.value === 'create') {
    form.value.slug = newName
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim()
  }
})

const handleSubmit = async () => {
  if (!form.value.name || !form.value.slug) {
    toast.error('Ошибка', 'Заполните обязательные поля')
    return
  }

  isSubmitting.value = true
  try {
    if (modalMode.value === 'create') {
      await adminCreateCategory(form.value)
      toast.success('Успех', 'Категория создана')
    } else if (editingId.value) {
      await adminUpdateCategory(editingId.value, form.value)
      toast.success('Успех', 'Категория обновлена')
    }
    await refresh()
    closeModal()
  } catch (err: any) {
    toast.error('Ошибка', err.data?.message || 'Не удалось сохранить категорию')
  } finally {
    isSubmitting.value = false
  }
}

const handleDelete = async (id: string) => {
  if (!confirm('Вы уверены, что хотите удалить эту категорию? Все товары останутся без категории.')) return

  try {
    await adminDeleteCategory(id)
    toast.success('Успех', 'Категория удалена')
    await refresh()
  } catch (err: any) {
    toast.error('Ошибка', err.data?.message || 'Не удалось удалить категорию')
  }
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Категории товаров</template>
    <template #header-actions>
      <UButton variant="primary" @click="openCreateModal" size="sm">
        <template #icon><Icon name="ph:plus-bold" /></template>
        Добавить
      </UButton>
    </template>

  <div class="admin-categories-page">
    <div class="page-header">
      <UButton variant="ghost" to="/admin/products" size="sm">
        <template #icon><Icon name="ph:arrow-left-bold" /></template>
        ← Товары
      </UButton>
    </div>

    <UCard class="table-card">
      <div v-if="pending" class="loading-state">Загрузка...</div>
      <div v-else-if="error" class="error-state">Ошибка при загрузке данных</div>
      <div v-else-if="categories.length === 0" class="empty-state">Категории не найдены</div>
      <div v-else class="admin-table-wrapper">
        <table class="admin-table">
          <thead>
            <tr>
              <th class="desktop-only">ID</th>
              <th>Название</th>
              <th class="desktop-only">Slug</th>
              <th>Товаров</th>
              <th class="actions-col">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="category in categories" :key="category.id">
              <td class="id-cell desktop-only" :title="category.id">{{ category.id.substring(0, 8) }}...</td>
              <td class="name-cell truncate">{{ category.name }}</td>
              <td class="slug-cell desktop-only truncate">{{ category.slug }}</td>
              <td>{{ category.product_count || 0 }}</td>
              <td class="actions-cell">
                <div class="flex gap-2 justify-end">
                  <UButton 
                    variant="ghost" 
                    size="sm" 
                    @click="openEditModal(category)"
                    aria-label="Редактировать"
                  >
                    <template #icon><Icon name="ph:pencil-simple-bold" /></template>
                  </UButton>
                  <UButton 
                    variant="danger" 
                    size="sm" 
                    @click="handleDelete(category.id)"
                    aria-label="Удалить"
                  >
                    <template #icon><Icon name="ph:trash-bold" /></template>
                  </UButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </UCard>

    <UModal 
      v-model="isModalOpen" 
      :title="modalMode === 'create' ? 'Новая категория' : 'Редактировать категорию'"
    >
      <div class="space-y-4 pt-4">
        <UInput 
          v-model="form.name" 
          label="Название" 
          placeholder="Электроника"
          required
        />
        <UInput 
          v-model="form.slug" 
          label="Slug (URL)" 
          placeholder="electronics"
          required
        />
        
        <div class="flex justify-end gap-3 mt-6">
          <UButton variant="ghost" @click="closeModal">Отмена</UButton>
          <UButton 
            variant="primary" 
            :loading="isSubmitting"
            @click="handleSubmit"
          >
            Сохранить
          </UButton>
        </div>
      </div>
    </UModal>
  </div>
  </NuxtLayout>
</template>

<style scoped>
.admin-categories-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  width: 100px;
}

.admin-table th:nth-child(2),
.admin-table td:nth-child(2) {
  width: auto;
}

.admin-table th:nth-child(4),
.admin-table td:nth-child(4) {
  width: 100px;
}

.actions-col, .actions-cell {
  width: 120px;
  text-align: right;
}

.id-cell {
  font-family: var(--font-mono);
  color: var(--color-muted);
}

.name-cell {
  font-weight: 600;
}

.slug-cell {
  color: var(--color-text-2);
  font-family: var(--font-mono);
}

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.loading-state, .error-state, .empty-state {
  padding: 48px;
  text-align: center;
  color: var(--color-text-2);
}

.flex { display: flex; }
.gap-2 { gap: 0.5rem; }
.gap-3 { gap: 0.75rem; }
.justify-end { justify-content: flex-end; }
.space-y-4 > * + * { margin-top: 1rem; }
.pt-4 { padding-top: 1rem; }
.mt-6 { margin-top: 1.5rem; }
</style>
