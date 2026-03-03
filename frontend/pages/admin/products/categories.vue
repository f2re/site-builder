<script setup lang="ts">
import { ref, computed } from 'vue'
import { useProducts, type ProductCategory } from '~/composables/useProducts'
import { useToast } from '~/composables/useToast'
import UButton from '~/components/U/UButton.vue'
import UInput from '~/components/U/UInput.vue'
import UCard from '~/components/U/UCard.vue'
import UModal from '~/components/U/UModal.vue'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const toast = useToast()
const { adminGetCategories, adminCreateCategory, adminUpdateCategory, adminDeleteCategory } = useProducts()

const { data, pending, error, refresh } = await adminGetCategories()
const categories = computed(() => data.value?.items || [])

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
    refresh()
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
    refresh()
  } catch (err: any) {
    toast.error('Ошибка', err.data?.message || 'Не удалось удалить категорию')
  }
}
</script>

<template>
  <div class="admin-categories-page">
    <div class="page-header">
      <div class="flex items-center gap-4">
        <UButton variant="ghost" to="/admin/products" icon="ph:arrow-left-bold" />
        <h1 class="page-title">Категории товаров</h1>
      </div>
      <UButton variant="primary" @click="openCreateModal" icon="ph:plus-bold">
        Добавить категорию
      </UButton>
    </div>

    <UCard class="table-card">
      <div v-if="pending" class="loading-state">Загрузка...</div>
      <div v-else-if="error" class="error-state">Ошибка при загрузке данных</div>
      <div v-else-if="categories.length === 0" class="empty-state">Категории не найдены</div>
      <div v-else class="table-responsive">
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Slug</th>
              <th>Товаров</th>
              <th class="actions-col">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="category in categories" :key="category.id">
              <td class="id-cell" :title="category.id">{{ category.id.substring(0, 8) }}...</td>
              <td class="name-cell">{{ category.name }}</td>
              <td class="slug-cell">{{ category.slug }}</td>
              <td>{{ category.product_count || 0 }}</td>
              <td class="actions-cell">
                <div class="flex gap-2 justify-end">
                  <UButton 
                    variant="ghost" 
                    size="sm" 
                    icon="ph:pencil-simple-bold"
                    @click="openEditModal(category)"
                  />
                  <UButton 
                    variant="ghost" 
                    size="sm" 
                    icon="ph:trash-bold"
                    color="danger"
                    @click="handleDelete(category.id)"
                  />
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

.page-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin: 0;
}

.table-card {
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

.name-cell {
  font-weight: 600;
}

.slug-cell {
  color: var(--color-text-2);
  font-family: var(--font-mono);
}

.actions-col {
  text-align: right;
}

.loading-state, .error-state, .empty-state {
  padding: 48px;
  text-align: center;
  color: var(--color-text-2);
}

.flex { display: flex; }
.items-center { align-items: center; }
.gap-2 { gap: 0.5rem; }
.gap-3 { gap: 0.75rem; }
.gap-4 { gap: 1rem; }
.justify-end { justify-content: flex-end; }
.space-y-4 > * + * { margin-top: 1rem; }
.pt-4 { padding-top: 1rem; }
.mt-6 { margin-top: 1.5rem; }
</style>
