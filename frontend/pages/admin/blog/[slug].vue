<script setup lang="ts">
import BlogEditor from '@/components/Admin/BlogEditor.vue'

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const route = useRoute()
const router = useRouter()
const toast = useToast()
const apiFetch = useApiFetch()

const { data: post, pending: loading } = await useApi<any>(`/blog/posts/${route.params.slug}`)

const form = reactive({
  title: '',
  content_html: '',
  tags: [] as string[],
  cover_image: '',
  status: 'draft' as 'draft' | 'published',
})

watchEffect(() => {
  if (post.value) {
    form.title = post.value.title
    form.content_html = post.value.content_html || ''
    form.tags = post.value.tags?.map((t: any) => typeof t === 'string' ? t : t.name) || []
    form.cover_image = post.value.cover_image || ''
    form.status = post.value.status || 'draft'
  }
})

const tagInput = ref('')

function addTag() {
  if (tagInput.value && !form.tags.includes(tagInput.value)) {
    form.tags.push(tagInput.value)
    tagInput.value = ''
  }
}

function removeTag(tag: string) {
  form.tags = form.tags.filter(t => t !== tag)
}

const pending = ref(false)

async function save() {
  if (!post.value?.id) return
  if (!form.title) {
    toast.error('Заголовок обязателен')
    return
  }
  
  pending.value = true
  try {
    await apiFetch(`/blog/posts/${post.value.id}`, {
      method: 'PUT',
      body: form,
    })
    toast.success('Пост обновлен')
    router.push('/admin/blog')
  } catch (e: any) {
    toast.error(e.data?.detail || 'Ошибка при сохранении')
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Редактирование</template>
    <template #header-actions>
      <div class="flex gap-2">
        <UButton variant="ghost" to="/admin/blog" class="desktop-only">Отмена</UButton>
        <UButton @click="save" :loading="pending" data-testid="admin-save-btn">Сохранить</UButton>
      </div>
    </template>

    <div class="admin-blog-edit">
      <div v-if="loading">
      <USkeleton height="400px" />
    </div>
    
    <div v-else class="form-container">
      <div class="main-content">
        <UCard>
          <div class="space-y-4">
            <UInput
              v-model="form.title"
              label="Заголовок"
              placeholder="Введите заголовок статьи"
              required
              data-testid="admin-blog-title"
            />
            
            <div class="form-group">
              <label class="label">Содержимое</label>
              <BlogEditor v-model="form.content_html" />
            </div>
          </div>
        </UCard>
      </div>
      
      <div class="side-content">
        <UCard>
          <div class="space-y-6">
            <UInput
              v-model="form.cover_image"
              label="URL обложки"
              placeholder="https://..."
            />
            
            <div class="form-group">
              <label class="label">Теги</label>
              <div class="tag-input-wrapper">
                <UInput
                  v-model="tagInput"
                  placeholder="Добавить тег"
                  @keydown.enter.prevent="addTag"
                />
                <UButton type="button" variant="secondary" @click="addTag">
                  <Icon name="ph:plus-bold" />
                </UButton>
              </div>
              <div class="tags-list mt-2" v-if="form.tags.length">
                <UBadge
                  v-for="tag in form.tags"
                  :key="tag"
                  variant="info"
                  class="tag-badge"
                >
                  {{ tag }}
                  <button @click="removeTag(tag)" class="ml-1" aria-label="Удалить тег">&times;</button>
                </UBadge>
              </div>
            </div>
            
            <div class="form-group">
              <label class="label">Статус</label>
              <div class="radio-group">
                <label class="radio-label">
                  <input type="radio" v-model="form.status" value="draft" />
                  <span class="radio-text">Черновик</span>
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="form.status" value="published" />
                  <span class="radio-text">Опубликован</span>
                </label>
              </div>
            </div>
          </div>
        </UCard>

        <div class="mobile-only mt-6">
          <UButton variant="ghost" to="/admin/blog" block>Отмена</UButton>
        </div>
      </div>
      </div>
      </div>
      </NuxtLayout>
      </template>
<style scoped>
.admin-blog-edit {
  max-width: 1200px;
  margin: 0 auto;
}

.form-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 1024px) {
  .form-container {
    grid-template-columns: 1fr 320px;
  }
}

.space-y-4 > * + * { margin-top: 16px; }
.space-y-6 > * + * { margin-top: 24px; }

.label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--color-text-2);
}

.tag-input-wrapper {
  display: flex;
  gap: 8px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-badge {
  display: flex;
  align-items: center;
  padding-right: 4px;
}

.ml-1 {
  margin-left: 4px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color var(--transition-fast);
}

.ml-1:hover {
  background: rgba(0,0,0,0.1);
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  transition: all var(--transition-fast);
}

.radio-label:has(input:checked) {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
}

.radio-text {
  font-size: var(--text-sm);
  font-weight: 500;
}

.flex { display: flex; }
.gap-2 { gap: 8px; }
.mt-2 { margin-top: 8px; }
.mt-6 { margin-top: 24px; }

.desktop-only {
  display: none;
}

@media (min-width: 768px) {
  .desktop-only {
    display: inline-flex;
  }
}

.mobile-only {
  display: block;
}

@media (min-width: 768px) {
  .mobile-only {
    display: none;
  }
}
</style>
