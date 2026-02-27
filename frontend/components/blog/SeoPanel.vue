<script setup lang="ts">
interface Props {
  modelValue: {
    meta_title: string
    meta_description: string
  }
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const localState = reactive({
  meta_title: props.modelValue.meta_title || '',
  meta_description: props.modelValue.meta_description || ''
})

watch(() => props.modelValue, (newVal) => {
  localState.meta_title = newVal.meta_title || ''
  localState.meta_description = newVal.meta_description || ''
}, { deep: true })

watch(localState, (newVal) => {
  emit('update:modelValue', { ...newVal })
}, { deep: true })

const TITLE_LIMIT = 60
const DESC_LIMIT = 160

const titleCount = computed(() => localState.meta_title.length)
const descCount = computed(() => localState.meta_description.length)

const isTitleOver = computed(() => titleCount.value > TITLE_LIMIT)
const isDescOver = computed(() => descCount.value > DESC_LIMIT)
</script>

<template>
  <div class="seo-panel">
    <div class="seo-field">
      <div class="field-header">
        <label for="meta_title">Meta Title (SEO)</label>
        <span class="char-counter" :class="{ 'over-limit': isTitleOver }">
          {{ titleCount }} / {{ TITLE_LIMIT }}
        </span>
      </div>
      <UInput
        id="meta_title"
        v-model="localState.meta_title"
        placeholder="Введите заголовок для поисковых систем..."
        :class="{ 'input-error': isTitleOver }"
      />
      <p class="field-hint">
        Заголовок, который отображается в результатах поиска. Оптимально до 60 символов.
      </p>
    </div>

    <div class="seo-field">
      <div class="field-header">
        <label for="meta_description">Meta Description (SEO)</label>
        <span class="char-counter" :class="{ 'over-limit': isDescOver }">
          {{ descCount }} / {{ DESC_LIMIT }}
        </span>
      </div>
      <UTextarea
        id="meta_description"
        v-model="localState.meta_description"
        placeholder="Введите описание для поисковых систем..."
        :rows="3"
        :class="{ 'input-error': isDescOver }"
      />
      <p class="field-hint">
        Краткое описание страницы для поисковых систем. Оптимально до 160 символов.
      </p>
    </div>

    <div class="seo-preview">
      <h3 class="preview-title">Предпросмотр в Google</h3>
      <div class="google-card">
        <div class="google-url">https://wifiobd.shop/blog/your-post-slug</div>
        <div class="google-title">{{ localState.meta_title || 'Заголовок статьи появится здесь' }}</div>
        <div class="google-desc">
          {{ localState.meta_description || 'Введите описание, чтобы увидеть, как оно будет выглядеть в результатах поиска Google.' }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.seo-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  padding: var(--space-6);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.seo-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.field-header label {
  font-weight: 600;
  color: var(--color-text);
  font-size: var(--text-sm);
}

.char-counter {
  font-size: var(--text-xs);
  color: var(--color-text-2);
  font-family: var(--font-mono);
}

.char-counter.over-limit {
  color: var(--color-error);
  font-weight: 700;
}

.input-error :deep(input),
.input-error :deep(textarea) {
  border-color: var(--color-error) !important;
}

.field-hint {
  font-size: var(--text-xs);
  color: var(--color-text-2);
}

.seo-preview {
  margin-top: var(--space-4);
  padding-top: var(--space-6);
  border-top: 1px solid var(--color-border);
}

.preview-title {
  font-size: var(--text-sm);
  font-weight: 600;
  margin-bottom: var(--space-4);
  color: var(--color-text-2);
}

.google-card {
  background: white;
  padding: var(--space-4);
  border-radius: var(--radius-md);
  box-shadow: 0 1px 6px rgba(32, 33, 36, 0.28);
  max-width: 600px;
}

[data-theme="dark"] .google-card {
  background: #202124;
}

.google-url {
  color: #202124;
  font-size: 14px;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

[data-theme="dark"] .google-url {
  color: #bdc1c6;
}

.google-title {
  color: #1a0dab;
  font-size: 20px;
  line-height: 1.3;
  margin-bottom: 3px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

[data-theme="dark"] .google-title {
  color: #8ab4f8;
}

.google-desc {
  color: #4d5156;
  font-size: 14px;
  line-height: 1.58;
  word-wrap: break-word;
}

[data-theme="dark"] .google-desc {
  color: #bdc1c6;
}
</style>
