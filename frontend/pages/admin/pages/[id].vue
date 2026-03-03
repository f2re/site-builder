<script setup lang="ts">
import { useForm } from 'vee-validate'
import { z } from 'zod'
import { toFormValidator } from '@vee-validate/zod'

definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

const route = useRoute()
const router = useRouter()
const { getPageById, createPage, updatePage } = usePages()
const toast = useToast()

const isEdit = route.params.id !== 'create'
const pageId = isEdit ? route.params.id as string : null

// Form schema
const schema = z.object({
  title: z.string().min(2, 'Заголовок должен содержать минимум 2 символа').max(200),
  slug: z.string().min(1, 'Slug обязателен').regex(/^[a-z0-9-_]+$/, 'Slug может содержать только латинские буквы, цифры, тире и подчеркивания'),
  content: z.string().min(5, 'Контент слишком короткий'),
  meta_title: z.string().max(200).optional().nullable(),
  meta_description: z.string().max(500).optional().nullable(),
  is_active: z.boolean().default(true)
})

const { handleSubmit, resetForm, setFieldValue, errors, isSubmitting, defineField } = useForm({
  validationSchema: toFormValidator(schema),
  initialValues: {
    title: '',
    slug: '',
    content: '',
    meta_title: '',
    meta_description: '',
    is_active: true
  }
})

const [title, titleProps] = defineField('title')
const [slug, slugProps] = defineField('slug')
const [content] = defineField('content')
const [is_active] = defineField('is_active')
const [meta_title] = defineField('meta_title')
const [meta_description] = defineField('meta_description')

// Loading existing data
const isLoading = ref(isEdit)
onMounted(async () => {
  if (isEdit && pageId) {
    try {
      const { data: page, error } = await getPageById(pageId)
      if (error.value) throw error.value
      
      if (page.value) {
        resetForm({
          values: {
            title: page.value.title,
            slug: page.value.slug,
            content: page.value.content,
            meta_title: page.value.meta_title || '',
            meta_description: page.value.meta_description || '',
            is_active: page.value.is_active
          }
        })
      }
    } catch (e: any) {
      toast.error('Не удалось загрузить данные страницы')
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }
})

const onSubmit = handleSubmit(async (formValues) => {
  try {
    if (isEdit && pageId) {
      await updatePage(pageId, formValues)
      toast.success('Страница обновлена')
    } else {
      await createPage(formValues as any)
      toast.success('Страница создана')
    }
    router.push('/admin/pages')
  } catch (e: any) {
    toast.error(e.data?.detail || e.message || 'Ошибка при сохранении')
  }
})

// Helper to auto-generate slug from title
const generateSlug = () => {
  // Only generate if title exists and slug is empty
  if (!title.value || (isEdit && slug.value)) return
  
  const generated = title.value
    .toLowerCase()
    .replace(/[а-яё]/g, (match) => {
      const map: Record<string, string> = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya'
      }
      return map[match] || match
    })
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
  
  slug.value = generated
}
</script>

<template>
  <div class="admin-page-editor">
    <div class="mb-6">
      <NuxtLink to="/admin/pages" class="text-sm text-muted hover:text-accent flex items-center gap-1 mb-2">
        <Icon name="ph:arrow-left" />
        К списку страниц
      </NuxtLink>
      <h1>{{ isEdit ? 'Редактирование страницы' : 'Создание страницы' }}</h1>
    </div>

    <div v-if="isLoading" class="loading-state">
      <Icon name="ph:spinner-gap-bold" class="spin" size="32" />
      <p>Загрузка данных...</p>
    </div>

    <form v-else @submit.prevent="onSubmit" class="editor-form">
      <div class="main-content">
        <div class="form-section">
          <div class="field-group">
            <label for="title">Заголовок страницы</label>
            <input 
              id="title" 
              v-model="title" 
              v-bind="titleProps"
              @blur="generateSlug"
              type="text" 
              class="u-input"
              :class="{ 'is-error': errors.title }"
              placeholder="Введите заголовок"
            />
            <span v-if="errors.title" class="error-msg">{{ errors.title }}</span>
          </div>

          <div class="field-group">
            <label for="slug">URL Slug (человекопонятный URL)</label>
            <div class="slug-input-wrapper">
              <span class="url-prefix">/</span>
              <input 
                id="slug" 
                v-model="slug" 
                v-bind="slugProps"
                type="text" 
                class="u-input"
                :class="{ 'is-error': errors.slug }"
                placeholder="about-us"
              />
            </div>
            <span v-if="errors.slug" class="error-msg">{{ errors.slug }}</span>
          </div>

          <div class="field-group">
            <label>Содержимое страницы</label>
            <URichEditor 
              v-model="content"
              class="page-editor"
            />
            <span v-if="errors.content" class="error-msg">{{ errors.content }}</span>
          </div>
        </div>
      </div>

      <aside class="sidebar-content">
        <div class="form-section settings">
          <h3>Настройки</h3>
          
          <div class="field-group checkbox">
            <label class="toggle">
              <input type="checkbox" v-model="is_active" />
              <span class="slider"></span>
              <span class="label">Опубликована</span>
            </label>
          </div>

          <div class="divider"></div>

          <h3>SEO (Мета-теги)</h3>
          
          <div class="field-group">
            <label for="meta_title">Meta Title</label>
            <input 
              id="meta_title" 
              v-model="meta_title" 
              type="text" 
              class="u-input"
              placeholder="SEO заголовок"
            />
          </div>

          <div class="field-group">
            <label for="meta_description">Meta Description</label>
            <textarea 
              id="meta_description" 
              v-model="meta_description" 
              class="u-textarea"
              placeholder="SEO описание (рекомендуется 150-160 символов)"
              rows="4"
            ></textarea>
          </div>
        </div>

        <div class="actions">
          <button type="submit" class="btn-submit" :disabled="isSubmitting">
            <Icon v-if="isSubmitting" name="ph:spinner-gap-bold" class="spin" />
            <span>{{ isEdit ? 'Сохранить изменения' : 'Создать страницу' }}</span>
          </button>
          
          <NuxtLink to="/admin/pages" class="btn-cancel">Отмена</NuxtLink>
        </div>
      </aside>
    </form>
  </div>
</template>

<style scoped>
.admin-page-editor {
  max-width: 1200px;
}

.editor-form {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  align-items: start;
}

@media (max-width: 1024px) {
  .editor-form {
    grid-template-columns: 1fr;
  }
}

.form-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 24px;
}

.form-section h3 {
  font-size: var(--text-base);
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--color-text);
}

.field-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-group label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
}

.u-input, .u-textarea {
  width: 100%;
  padding: 10px 14px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-family: inherit;
  font-size: var(--text-base);
  transition: all var(--transition-fast);
}

.u-input:focus, .u-textarea:focus {
  border-color: var(--color-accent);
  outline: none;
  box-shadow: 0 0 0 4px var(--color-accent-glow);
}

.u-input.is-error {
  border-color: var(--color-error);
}

.error-msg {
  color: var(--color-error);
  font-size: var(--text-xs);
  margin-top: -4px;
}

.slug-input-wrapper {
  display: flex;
  align-items: center;
  gap: 0;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.url-prefix {
  padding: 0 12px;
  color: var(--color-muted);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  background: var(--color-bg-subtle);
  border-right: 1px solid var(--color-border);
  height: 44px;
  display: flex;
  align-items: center;
}

.slug-input-wrapper .u-input {
  border: none;
  border-radius: 0;
}

.toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.toggle input {
  display: none;
}

.slider {
  width: 44px;
  height: 24px;
  background: var(--color-border-strong);
  border-radius: var(--radius-full);
  position: relative;
  transition: var(--transition-fast);
}

.slider::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: var(--transition-fast);
}

.toggle input:checked + .slider {
  background: var(--color-success);
}

.toggle input:checked + .slider::after {
  transform: translateX(20px);
}

.divider {
  height: 1px;
  background: var(--color-border);
  margin: 20px 0;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-submit {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: var(--color-accent);
  color: var(--color-on-accent);
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-submit:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-accent);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  display: block;
  width: 100%;
  text-align: center;
  padding: 12px;
  color: var(--color-text-2);
  text-decoration: none;
  font-size: var(--text-sm);
  transition: color var(--transition-fast);
}

.btn-cancel:hover {
  color: var(--color-text);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state {
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
</style>
