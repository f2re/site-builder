<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useBlog, type BlogCategory } from '~/composables/useBlog'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
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
const { confirm } = useConfirm()
const blog = useBlog()

const { data, pending, error, refresh } = await blog.adminGetCategories()
const categories = computed<BlogCategory[]>(() => data.value ?? [])

const isModalOpen = ref(false)
const isSubmitting = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const editingId = ref<string | null>(null)

const form = ref({
  name: '',
  slug: '',
  description: '',
})

const openCreateModal = () => {
  modalMode.value = 'create'
  editingId.value = null
  form.value = { name: '', slug: '', description: '' }
  isModalOpen.value = true
}

const openEditModal = (category: BlogCategory) => {
  modalMode.value = 'edit'
  editingId.value = category.id
  form.value = {
    name: category.name,
    slug: category.slug,
    description: category.description ?? '',
  }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

// Slug auto-generation from name
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
    const payload = {
      name: form.value.name,
      slug: form.value.slug,
      description: form.value.description || undefined,
    }
    if (modalMode.value === 'create') {
      await blog.adminCreateCategory(payload)
      toast.success('Успех', 'Категория создана')
    } else if (editingId.value) {
      await blog.adminUpdateCategory(editingId.value, payload)
      toast.success('Успех', 'Категория обновлена')
    }
    await refresh()
    closeModal()
  } catch (err: unknown) {
    const apiErr = err as { data?: { message?: string } }
    toast.error('Ошибка', apiErr.data?.message || 'Не удалось сохранить категорию')
  } finally {
    isSubmitting.value = false
  }
}

const handleDelete = async (category: BlogCategory) => {
  if (!await confirm({
    title: 'Удалить категорию?',
    message: `Категория "${category.name}" будет удалена. Посты останутся без категории.`,
    confirmLabel: 'Удалить',
    variant: 'danger',
  })) return

  try {
    await blog.adminDeleteCategory(category.id)
    toast.success('Успех', 'Категория удалена')
    await refresh()
  } catch (err: unknown) {
    const apiErr = err as { data?: { message?: string } }
    toast.error('Ошибка', apiErr.data?.message || 'Не удалось удалить категорию')
  }
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Категории блога</template>
    <template #header-actions>
      <UButton variant="primary" size="sm" data-testid="admin-blog-cat-add-btn" @click="openCreateModal">
        <template #icon><Icon name="ph:plus-bold" /></template>
        Добавить
      </UButton>
    </template>

    <div class="admin-blog-categories">
      <div class="page-header">
        <UButton variant="ghost" to="/admin/blog" size="sm">
          <template #icon><Icon name="ph:arrow-left-bold" /></template>
          Посты блога
        </UButton>
      </div>

      <UCard class="table-card">
        <div v-if="pending" class="loading-state">Загрузка...</div>
        <div v-else-if="error" class="error-state">Ошибка при загрузке данных</div>
        <div v-else-if="categories.length === 0" class="empty-state" data-testid="admin-blog-cat-empty">
          Категории не найдены
        </div>
        <div v-else class="admin-table-wrapper">
          <table class="admin-table" data-testid="admin-blog-cat-table">
            <thead>
              <tr>
                <th>Название</th>
                <th class="desktop-only">Slug</th>
                <th>Постов</th>
                <th class="actions-col">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="category in categories"
                :key="category.id"
                data-testid="admin-blog-cat-row"
              >
                <td class="name-cell">{{ category.name }}</td>
                <td class="slug-cell desktop-only">{{ category.slug }}</td>
                <td>{{ category.posts_count }}</td>
                <td class="actions-cell">
                  <div class="actions">
                    <UButton
                      variant="ghost"
                      size="sm"
                      aria-label="Редактировать"
                      data-testid="admin-blog-cat-edit-btn"
                      @click="openEditModal(category)"
                    >
                      <template #icon><Icon name="ph:pencil-simple-bold" size="20" /></template>
                    </UButton>
                    <UButton
                      variant="danger"
                      size="sm"
                      aria-label="Удалить"
                      data-testid="admin-blog-cat-delete-btn"
                      @click="handleDelete(category)"
                    >
                      <template #icon><Icon name="ph:trash-bold" size="20" /></template>
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
        :title="modalMode === 'create' ? 'Новая категория блога' : 'Редактировать категорию'"
        data-testid="admin-blog-cat-modal"
      >
        <div class="form-body">
          <UInput
            v-model="form.name"
            label="Название"
            placeholder="Обзоры"
            required
            data-testid="admin-blog-cat-name-input"
          />
          <UInput
            v-model="form.slug"
            label="Slug (URL)"
            placeholder="reviews"
            required
            data-testid="admin-blog-cat-slug-input"
          />
          <UInput
            v-model="form.description"
            label="Описание (необязательно)"
            placeholder="Обзоры OBD2 адаптеров"
            data-testid="admin-blog-cat-desc-input"
          />

          <div class="form-actions">
            <UButton variant="ghost" @click="closeModal">Отмена</UButton>
            <UButton
              variant="primary"
              :loading="isSubmitting"
              data-testid="admin-blog-cat-save-btn"
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
.admin-blog-categories {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
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
  width: auto;
}

@media (min-width: 768px) {
  .admin-table th:nth-child(2),
  .admin-table td:nth-child(2) {
    width: 200px;
  }
}

.admin-table th:nth-child(3),
.admin-table td:nth-child(3) {
  width: 80px;
}

.actions-col,
.actions-cell {
  width: 100px;
  text-align: right;
}

.name-cell {
  font-weight: 600;
  color: var(--color-text);
}

.slug-cell {
  color: var(--color-text-2);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

.actions {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
}

.loading-state,
.error-state,
.empty-state {
  padding: 48px;
  text-align: center;
  color: var(--color-text-2);
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 16px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}
</style>
