<script setup lang="ts">
import TipTapEditor from '~/components/blog/TipTapEditor.vue'
import BlogCarouselManager from '~/components/blog/BlogCarouselManager.vue'
import { useBlog } from '~/composables/useBlog'
import { useMediaUpload } from '~/composables/useMediaUpload'

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const router = useRouter()
const toast = useToast()
const apiFetch = useApiFetch()
const { getTags } = useBlog()
const { uploadImage } = useMediaUpload()

// Tags autocomplete
const { data: allTagsData } = await getTags()
const allTags = computed(() => allTagsData.value ?? [])

const form = reactive({
  title: '',
  slug: '',
  summary: '',
  content_json: null as Record<string, unknown> | null,
  tags: [] as string[],
  cover_url: '',
  carousel_images: [] as string[],
  status: 'draft' as 'draft' | 'published' | 'archived',
  is_featured: false,
  meta_title: '',
  meta_description: '',
})

// Auto-generate slug from title
watch(() => form.title, (val) => {
  if (!form.slug || form.slug === slugify(form.title.slice(0, -1))) {
    form.slug = slugify(val)
  }
})

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[а-я]/g, c => ({ а:'a',б:'b',в:'v',г:'g',д:'d',е:'e',ё:'yo',ж:'zh',з:'z',и:'i',й:'j',к:'k',л:'l',м:'m',н:'n',о:'o',п:'p',р:'r',с:'s',т:'t',у:'u',ф:'f',х:'h',ц:'ts',ч:'ch',ш:'sh',щ:'sch',ъ:'',ы:'y',ь:'',э:'e',ю:'yu',я:'ya' }[c] ?? c))
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
}

// Tags input
const tagInput = ref('')
const tagSuggestions = computed(() => {
  if (!tagInput.value) return []
  const q = tagInput.value.toLowerCase()
  return allTags.value.filter(t =>
    t.name.toLowerCase().includes(q) && !form.tags.includes(t.name)
  )
})
const showSuggestions = ref(false)

function addTag(name?: string) {
  const tagName = name || tagInput.value.trim()
  if (tagName && !form.tags.includes(tagName)) {
    form.tags.push(tagName)
    tagInput.value = ''
    showSuggestions.value = false
  }
}

function removeTag(tag: string) {
  form.tags = form.tags.filter(t => t !== tag)
}

function selectSuggestion(name: string) {
  addTag(name)
}

// Cover upload
const coverFileInput = ref<HTMLInputElement | null>(null)
const isUploadingCover = ref(false)

function triggerCoverUpload() {
  coverFileInput.value?.click()
}

async function handleCoverUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  isUploadingCover.value = true
  try {
    const url = await uploadImage(file, file.name, 'blog')
    form.cover_url = url
    toast.success('Обложка загружена')
  } catch {
    // error handled in useMediaUpload
  } finally {
    isUploadingCover.value = false
    if (target) target.value = ''
  }
}

const pending = ref(false)

async function save() {
  if (!form.title) {
    toast.error('Заголовок обязателен')
    return
  }

  pending.value = true
  try {
    await apiFetch('/admin/blog/posts', {
      method: 'POST',
      body: {
        title: form.title,
        slug: form.slug || undefined,
        summary: form.summary || undefined,
        content_json: form.content_json,
        tags: form.tags,
        cover_url: form.cover_url || undefined,
        carousel_images: form.carousel_images,
        status: form.status,
        is_featured: form.is_featured,
        meta_title: form.meta_title || undefined,
        meta_description: form.meta_description || undefined,
      },
    })
    toast.success('Пост создан')
    router.push('/admin/blog')
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.error(err.data?.detail || 'Ошибка при сохранении')
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Новый пост</template>
    <template #header-actions>
      <div class="flex gap-2">
        <UButton variant="ghost" to="/admin/blog" class="desktop-only">Отмена</UButton>
        <UButton @click="save" :loading="pending" data-testid="admin-save-btn">Сохранить</UButton>
      </div>
    </template>

    <div class="admin-blog-create">
      <div class="form-container">
        <!-- Main content -->
        <div class="main-content">
          <UCard>
            <div class="space-y-4">
              <UInput
                v-model="form.title"
                label="Заголовок *"
                placeholder="Введите заголовок статьи"
                required
                data-testid="admin-blog-title"
              />

              <UInput
                v-model="form.slug"
                label="Slug (URL)"
                placeholder="auto-generated-from-title"
              />

              <div class="form-group">
                <label class="label">Краткое описание</label>
                <textarea
                  v-model="form.summary"
                  class="textarea"
                  rows="3"
                  placeholder="Краткое описание статьи (отображается в карточке)"
                />
              </div>

              <div class="form-group">
                <label class="label">Содержимое</label>
                <ClientOnly>
                  <TipTapEditor
                    v-model="form.content_json"
                    placeholder="Начните писать статью..."
                  />
                  <template #fallback>
                    <div class="editor-placeholder skeleton" />
                  </template>
                </ClientOnly>
              </div>
            </div>
          </UCard>
        </div>

        <!-- Sidebar -->
        <div class="side-content">
          <UCard>
            <div class="space-y-6">
              <!-- Cover image -->
              <div class="form-group">
                <label class="label">Обложка</label>
                <div v-if="form.cover_url" class="cover-preview">
                  <img :src="form.cover_url" alt="Обложка" />
                  <button type="button" class="cover-remove" aria-label="Удалить обложку" @click="form.cover_url = ''">
                    <Icon name="ph:x-bold" size="14" />
                  </button>
                </div>
                <button
                  type="button"
                  class="upload-btn"
                  :disabled="isUploadingCover"
                  @click="triggerCoverUpload"
                >
                  <Icon v-if="isUploadingCover" name="ph:spinner" class="animate-spin" size="16" />
                  <Icon v-else name="ph:upload-simple-bold" size="16" />
                  {{ isUploadingCover ? 'Загрузка...' : 'Загрузить файл' }}
                </button>
                <input
                  ref="coverFileInput"
                  type="file"
                  accept="image/*"
                  class="hidden-input"
                  @change="handleCoverUpload"
                />
                <UInput
                  v-model="form.cover_url"
                  label=""
                  placeholder="или вставьте URL"
                  class="mt-2"
                />
              </div>

              <!-- Carousel manager -->
              <div class="form-group">
                <label class="label">Карусель изображений</label>
                <BlogCarouselManager v-model="form.carousel_images" />
              </div>

              <!-- Tags -->
              <div class="form-group">
                <label class="label">Теги</label>
                <div class="tag-input-wrapper">
                  <div class="tag-autocomplete">
                    <UInput
                      v-model="tagInput"
                      placeholder="Добавить тег"
                      @keydown.enter.prevent="addTag()"
                      @focus="showSuggestions = true"
                      @blur="() => setTimeout(() => { showSuggestions = false }, 150)"
                    />
                    <div v-if="showSuggestions && tagSuggestions.length" class="suggestions-list">
                      <button
                        v-for="s in tagSuggestions"
                        :key="s.id"
                        type="button"
                        class="suggestion-item"
                        @click="selectSuggestion(s.name)"
                      >
                        {{ s.name }}
                      </button>
                    </div>
                  </div>
                  <UButton type="button" variant="secondary" size="sm" @click="addTag()">
                    <Icon name="ph:plus-bold" />
                  </UButton>
                </div>
                <div v-if="form.tags.length" class="tags-list">
                  <UBadge
                    v-for="tag in form.tags"
                    :key="tag"
                    variant="info"
                    class="tag-badge"
                  >
                    {{ tag }}
                    <button type="button" class="tag-remove" aria-label="Удалить тег" @click="removeTag(tag)">&times;</button>
                  </UBadge>
                </div>
              </div>

              <!-- Status -->
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
                  <label class="radio-label">
                    <input type="radio" v-model="form.status" value="archived" />
                    <span class="radio-text">Архив</span>
                  </label>
                </div>
              </div>

              <!-- Featured -->
              <div class="form-group">
                <label class="toggle-label">
                  <input type="checkbox" v-model="form.is_featured" class="toggle-checkbox" />
                  <span class="toggle-text">Избранная статья</span>
                </label>
              </div>

              <!-- SEO -->
              <div class="form-group">
                <label class="label">SEO</label>
                <div class="space-y-3">
                  <UInput
                    v-model="form.meta_title"
                    label="Meta Title"
                    placeholder="Заголовок для поисковиков"
                  />
                  <div class="form-group">
                    <label class="label small">Meta Description</label>
                    <textarea
                      v-model="form.meta_description"
                      class="textarea"
                      rows="2"
                      placeholder="Описание для поисковиков"
                    />
                  </div>
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
.admin-blog-create {
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
.space-y-3 > * + * { margin-top: 12px; }
.mt-2 { margin-top: 8px; }
.mt-6 { margin-top: 24px; }

.label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--color-text-2);
}

.label.small {
  font-size: var(--text-xs);
  margin-bottom: 4px;
}

.textarea {
  width: 100%;
  padding: 10px 14px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: var(--text-sm);
  font-family: var(--font-sans);
  resize: vertical;
  transition: border-color var(--transition-fast);
  box-sizing: border-box;
}

.textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.editor-placeholder {
  height: 300px;
  border-radius: var(--radius-md);
}

/* Cover */
.cover-preview {
  position: relative;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-md);
  overflow: hidden;
  margin-bottom: 8px;
}

.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-remove {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.cover-remove:hover {
  background: var(--color-error);
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-2);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  width: 100%;
  justify-content: center;
  margin-bottom: 8px;
}

.upload-btn:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.upload-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.hidden-input {
  display: none;
}

/* Tags */
.tag-input-wrapper {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  margin-bottom: 8px;
}

.tag-autocomplete {
  flex: 1;
  position: relative;
}

.suggestions-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: var(--z-raised);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  margin-top: 4px;
  box-shadow: var(--shadow-card);
}

.suggestion-item {
  display: block;
  width: 100%;
  padding: 8px 12px;
  text-align: left;
  background: none;
  border: none;
  color: var(--color-text);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.suggestion-item:hover {
  background: var(--color-surface-2);
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.tag-badge {
  display: flex;
  align-items: center;
  gap: 4px;
}

.tag-remove {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: none;
  background: none;
  cursor: pointer;
  color: inherit;
  font-size: 14px;
  line-height: 1;
  transition: background var(--transition-fast);
}

.tag-remove:hover {
  background: rgba(0,0,0,0.15);
}

/* Status radio */
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

/* Toggle */
.toggle-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.toggle-checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--color-accent);
}

.toggle-text {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text);
}

/* Layout helpers */
.flex { display: flex; }
.gap-2 { gap: 8px; }

.desktop-only { display: none; }
@media (min-width: 768px) {
  .desktop-only { display: inline-flex; }
}

.mobile-only { display: block; }
@media (min-width: 768px) {
  .mobile-only { display: none; }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
