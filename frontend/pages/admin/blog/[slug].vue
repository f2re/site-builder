<script setup lang="ts">
import BlogEditor from '@/components/Admin/BlogEditor.vue'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const router = useRouter()
const toast = useToast()
const apiFetch = useApiFetch()

const { data: post, pending: loading } = await useApi<any>(`/blog/posts/${route.params.slug}`)

const form = reactive({
  title: '',
  content_md: '',
  tags: [] as string[],
  cover_url: '',
  status: 'draft' as 'draft' | 'published',
})

watchEffect(() => {
  if (post.value) {
    form.title = post.value.title
    form.content_md = post.value.content_html || '' // Use HTML from API as base for editor
    form.tags = [...post.value.tags]
    form.cover_url = post.value.cover_url || ''
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
  pending.value = true
  try {
    await apiFetch(`/blog/posts/${route.params.slug}`, {
      method: 'PATCH',
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
  <div class="max-w-4xl">
    <div class="mb-6">
      <h1 class="text-xl font-bold">Редактирование поста</h1>
    </div>
    
    <div v-if="loading">
      <USkeleton height="400px" />
    </div>
    
    <div v-else class="space-y-6">
      <UCard>
        <div class="space-y-4">
          <UInput
            v-model="form.title"
            label="Заголовок"
            placeholder="Введите заголовок статьи"
            required
          />
          
          <div class="form-group">
            <label class="label">Содержимое</label>
            <BlogEditor v-model="form.content_md" />
          </div>
        </div>
      </UCard>
      
      <UCard>
        <div class="space-y-4">
          <UInput
            v-model="form.cover_url"
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
              <UButton type="button" variant="secondary" @click="addTag">Добавить</UButton>
            </div>
            <div class="tags-list mt-2">
              <UBadge
                v-for="tag in form.tags"
                :key="tag"
                variant="info"
                class="tag-badge"
              >
                {{ tag }}
                <button @click="removeTag(tag)" class="ml-1">&times;</button>
              </UBadge>
            </div>
          </div>
          
          <div class="form-group">
            <label class="label">Статус</label>
            <div class="radio-group">
              <label class="radio-label">
                <input type="radio" v-model="form.status" value="draft" />
                <span>Черновик</span>
              </label>
              <label class="radio-label">
                <input type="radio" v-model="form.status" value="published" />
                <span>Опубликован</span>
              </label>
            </div>
          </div>
        </div>
      </UCard>
      
      <div class="flex justify-end gap-4">
        <UButton variant="ghost" to="/admin/blog">Отмена</UButton>
        <UButton @click="save" :loading="pending">Сохранить</UButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Same styles as create.vue */
.max-w-4xl { max-width: 896px; margin: 0 auto; }
.space-y-6 > * + * { margin-top: 24px; }
.space-y-4 > * + * { margin-top: 16px; }

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
}

.ml-1 { margin-left: 4px; }

.radio-group {
  display: flex;
  gap: 24px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.flex { display: flex; }
.justify-end { justify-content: flex-end; }
.gap-4 { gap: 16px; }
.mt-2 { margin-top: 8px; }
</style>
