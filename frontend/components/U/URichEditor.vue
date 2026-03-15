<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Typography from '@tiptap/extension-typography'
import { Markdown } from 'tiptap-markdown'
import { useToast } from '~/composables/useToast'
import { usePrompt } from '~/composables/usePrompt'

const props = defineProps<{
  modelValue: string
  placeholder?: string
}>()

const emit = defineEmits(['update:modelValue'])

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    Link.configure({
      openOnClick: false,
    }),
    Image.configure({
      HTMLAttributes: {
        class: 'editor-image',
      },
    }),
    Typography,
    Markdown,
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
})

watch(() => props.modelValue, (value) => {
  const isSame = editor.value?.getHTML() === value
  if (isSame) return
  editor.value?.commands.setContent(value, false)
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})

// Image upload
const { uploadImage } = useMediaUpload()
const imageInputRef = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)
const toast = useToast()
const { prompt: showPrompt } = usePrompt()

function openImageDialog() {
  imageInputRef.value?.click()
}

async function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file || !editor.value) return

  // Validate image
  if (!file.type.startsWith('image/')) {
    toast.warning('Неверный тип файла', 'Пожалуйста, выберите изображение')
    return
  }

  // Max 5MB
  if (file.size > 5 * 1024 * 1024) {
    toast.warning('Файл слишком большой', 'Размер изображения не должен превышать 5 МБ')
    return
  }

  isUploading.value = true

  try {
    // Get alt text from user (for SEO)
    const alt = await showPrompt({
      title: 'Alt-текст для изображения',
      label: 'Описание (для SEO и доступности)',
      placeholder: 'Описание изображения...',
    }) || ''

    // Upload to MinIO
    const publicUrl = await uploadImage(file, alt, 'content')

    // Insert into editor
    editor.value.chain().focus().setImage({ src: publicUrl, alt }).run()
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Ошибка загрузки изображения'
    toast.error('Ошибка загрузки', msg)
  } finally {
    isUploading.value = false
    // Reset input
    if (target) target.value = ''
  }
}

// Link dialog
const showLinkDialog = ref(false)
const linkUrl = ref('')

function openLinkDialog() {
  const previousUrl = editor.value?.getAttributes('link').href || ''
  linkUrl.value = previousUrl
  showLinkDialog.value = true
}

function setLink() {
  if (!editor.value) return

  if (linkUrl.value === '') {
    editor.value.chain().focus().extendMarkRange('link').unsetLink().run()
  } else {
    editor.value.chain().focus().extendMarkRange('link').setLink({ href: linkUrl.value }).run()
  }

  showLinkDialog.value = false
  linkUrl.value = ''
}

// Markdown import/export
const showImportMd = ref(false)
const showExportMd = ref(false)
const markdownInput = ref('')
const markdownOutput = ref('')

function openImportMd() {
  markdownInput.value = ''
  showImportMd.value = true
}

function applyMarkdown() {
  if (!editor.value || !markdownInput.value.trim()) return
  editor.value.commands.setContent(markdownInput.value)
  showImportMd.value = false
  markdownInput.value = ''
}

function openExportMd() {
  if (!editor.value) return
  markdownOutput.value = (editor.value.storage.markdown as { getMarkdown: () => string }).getMarkdown()
  showExportMd.value = true
}

async function copyMarkdown() {
  try {
    await navigator.clipboard.writeText(markdownOutput.value)
    toast.success('Скопировано', 'Markdown скопирован в буфер обмена')
  } catch {
    toast.error('Ошибка', 'Не удалось скопировать текст')
  }
}

// HTML import
const showImportHtml = ref(false)
const htmlInput = ref('')

function openImportHtml() {
  htmlInput.value = ''
  showImportHtml.value = true
}

function applyHtml() {
  if (!editor.value || !htmlInput.value.trim()) return
  editor.value.commands.setContent(htmlInput.value.trim(), true)
  showImportHtml.value = false
  htmlInput.value = ''
}
</script>

<template>
  <div class="rich-editor">
    <div v-if="editor" class="editor-toolbar">
      <button
        type="button"
        @click="editor.chain().focus().toggleBold().run()"
        :class="{ 'is-active': editor.isActive('bold') }"
        title="Жирный"
      >
        <Icon name="ph:text-b-bold" />
      </button>
      <button
        type="button"
        @click="editor.chain().focus().toggleItalic().run()"
        :class="{ 'is-active': editor.isActive('italic') }"
        title="Курсив"
      >
        <Icon name="ph:text-italic-bold" />
      </button>
      <button
        type="button"
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
        :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
        title="Заголовок 2"
      >
        <Icon name="ph:text-h-two-bold" />
      </button>
      <button
        type="button"
        @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
        :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }"
        title="Заголовок 3"
      >
        <Icon name="ph:text-h-three-bold" />
      </button>
      <div class="divider" />
      <button
        type="button"
        @click="editor.chain().focus().toggleBulletList().run()"
        :class="{ 'is-active': editor.isActive('bulletList') }"
        title="Список"
      >
        <Icon name="ph:list-bullets-bold" />
      </button>
      <button
        type="button"
        @click="editor.chain().focus().toggleOrderedList().run()"
        :class="{ 'is-active': editor.isActive('orderedList') }"
        title="Нумерованный список"
      >
        <Icon name="ph:list-numbers-bold" />
      </button>
      <button
        type="button"
        @click="editor.chain().focus().toggleBlockquote().run()"
        :class="{ 'is-active': editor.isActive('blockquote') }"
        title="Цитата"
      >
        <Icon name="ph:quotes-bold" />
      </button>
      <div class="divider" />
      <button
        type="button"
        @click="openLinkDialog"
        :class="{ 'is-active': editor.isActive('link') }"
        title="Ссылка"
      >
        <Icon name="ph:link-bold" />
      </button>
      <button
        type="button"
        @click="openImageDialog"
        :disabled="isUploading"
        title="Изображение"
      >
        <Icon v-if="!isUploading" name="ph:image-bold" />
        <Icon v-else name="ph:spinner" class="spin" />
      </button>
      <div class="divider" />
      <button
        type="button"
        @click="editor.chain().focus().undo().run()"
        :disabled="!editor.can().undo()"
        title="Отменить"
      >
        <Icon name="ph:arrow-u-up-left-bold" />
      </button>
      <button
        type="button"
        @click="editor.chain().focus().redo().run()"
        :disabled="!editor.can().redo()"
        title="Повторить"
      >
        <Icon name="ph:arrow-u-up-right-bold" />
      </button>
      <div class="divider" />
      <button
        type="button"
        class="md-btn"
        @click="openImportHtml"
        title="Вставить HTML"
        data-testid="richeditor-import-html-btn"
        aria-label="Вставить HTML"
      >
        HTML↑
      </button>
      <button
        type="button"
        class="md-btn"
        @click="openImportMd"
        title="Вставить Markdown"
        data-testid="richeditor-import-md-btn"
        aria-label="Вставить Markdown"
      >
        MD↑
      </button>
      <button
        type="button"
        class="md-btn"
        @click="openExportMd"
        title="Экспортировать в Markdown"
        data-testid="richeditor-export-md-btn"
        aria-label="Экспортировать в Markdown"
      >
        MD↓
      </button>
    </div>

    <div class="editor-body" @click="editor?.chain().focus().run()">
      <EditorContent
        :editor="editor"
        class="editor-content"
      />
    </div>

    <!-- Hidden file input for image upload -->
    <input
      ref="imageInputRef"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleImageUpload"
    />

    <!-- Import HTML modal -->
    <div
      v-if="showImportHtml"
      class="md-modal-overlay"
      @mousedown.self="showImportHtml = false"
      role="dialog"
      aria-modal="true"
      aria-label="Вставить HTML"
    >
      <div class="md-modal" data-testid="richeditor-import-html-modal">
        <div class="md-modal-header">
          <h3 class="md-modal-title">Вставить HTML</h3>
          <button
            type="button"
            class="md-modal-close"
            aria-label="Закрыть"
            @click="showImportHtml = false"
          >
            <Icon name="ph:x-bold" size="16" />
          </button>
        </div>
        <textarea
          v-model="htmlInput"
          class="md-textarea"
          placeholder="<p>Вставьте HTML-контент...</p>"
          rows="12"
          autofocus
          data-testid="richeditor-html-input"
        />
        <div class="md-modal-footer">
          <button type="button" class="md-action-btn" @click="showImportHtml = false">
            Отмена
          </button>
          <button
            type="button"
            class="md-action-btn md-action-btn--primary"
            :disabled="!htmlInput.trim()"
            @click="applyHtml"
            data-testid="richeditor-apply-html-btn"
          >
            Применить
          </button>
        </div>
      </div>
    </div>

    <!-- Link dialog -->
    <div v-if="showLinkDialog" class="link-dialog-overlay" @click="showLinkDialog = false">
      <div class="link-dialog" @click.stop>
        <h3>Добавить ссылку</h3>
        <input
          v-model="linkUrl"
          type="url"
          placeholder="https://example.com"
          @keydown.enter="setLink"
          autofocus
        />
        <div class="link-dialog-actions">
          <button type="button" @click="showLinkDialog = false">Отмена</button>
          <button type="button" @click="setLink" class="primary">Вставить</button>
        </div>
      </div>
    </div>

    <!-- Import Markdown modal -->
    <div
      v-if="showImportMd"
      class="md-modal-overlay"
      @mousedown.self="showImportMd = false"
      role="dialog"
      aria-modal="true"
      aria-label="Вставить Markdown"
    >
      <div class="md-modal" data-testid="richeditor-import-md-modal">
        <div class="md-modal-header">
          <h3 class="md-modal-title">Вставить Markdown</h3>
          <button
            type="button"
            class="md-modal-close"
            aria-label="Закрыть"
            @click="showImportMd = false"
          >
            <Icon name="ph:x-bold" size="16" />
          </button>
        </div>
        <textarea
          v-model="markdownInput"
          class="md-textarea"
          placeholder="# Заголовок&#10;&#10;Введите Markdown текст..."
          rows="12"
          autofocus
          data-testid="richeditor-md-input"
        />
        <div class="md-modal-footer">
          <button type="button" class="md-action-btn" @click="showImportMd = false">
            Отмена
          </button>
          <button
            type="button"
            class="md-action-btn md-action-btn--primary"
            :disabled="!markdownInput.trim()"
            @click="applyMarkdown"
            data-testid="richeditor-apply-md-btn"
          >
            Применить
          </button>
        </div>
      </div>
    </div>

    <!-- Export Markdown modal -->
    <div
      v-if="showExportMd"
      class="md-modal-overlay"
      @mousedown.self="showExportMd = false"
      role="dialog"
      aria-modal="true"
      aria-label="Экспортировать Markdown"
    >
      <div class="md-modal" data-testid="richeditor-export-md-modal">
        <div class="md-modal-header">
          <h3 class="md-modal-title">Экспорт Markdown</h3>
          <button
            type="button"
            class="md-modal-close"
            aria-label="Закрыть"
            @click="showExportMd = false"
          >
            <Icon name="ph:x-bold" size="16" />
          </button>
        </div>
        <textarea
          :value="markdownOutput"
          class="md-textarea md-textarea--readonly"
          rows="12"
          readonly
          data-testid="richeditor-md-output"
        />
        <div class="md-modal-footer">
          <button type="button" class="md-action-btn" @click="showExportMd = false">
            Закрыть
          </button>
          <button
            type="button"
            class="md-action-btn md-action-btn--primary"
            @click="copyMarkdown"
            data-testid="richeditor-copy-md-btn"
          >
            <Icon name="ph:copy-bold" size="14" />
            Копировать
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rich-editor {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  overflow: hidden;
  transition: border-color var(--transition-fast);
}

.rich-editor:focus-within {
  border-color: var(--color-accent);
}

.editor-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 8px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-2);
}

.editor-toolbar button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-text-2);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.editor-toolbar button:hover:not(:disabled) {
  background: var(--color-surface-3);
  color: var(--color-text);
}

.editor-toolbar button.is-active {
  background: var(--color-accent-glow);
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.editor-toolbar button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.divider {
  width: 1px;
  height: 24px;
  background: var(--color-border);
  margin: 4px 4px;
}

.editor-body {
  padding: 24px;
  min-height: 300px;
  max-height: 600px;
  overflow-y: auto;
  cursor: text;
}

.editor-content {
  color: var(--color-text);
  line-height: 1.6;
}

.editor-content :deep(.tiptap) {
  outline: none;
}

.editor-content :deep(.tiptap p) {
  margin-bottom: 1em;
}

.editor-content :deep(.tiptap h2) {
  font-size: var(--text-xl);
  font-weight: 700;
  margin: 1.5em 0 0.5em;
  color: var(--color-accent);
}

.editor-content :deep(.tiptap h3) {
  font-size: var(--text-lg);
  font-weight: 600;
  margin: 1.2em 0 0.4em;
}

.editor-content :deep(.tiptap ul), 
.editor-content :deep(.tiptap ol) {
  padding-left: 1.5em;
  margin-bottom: 1em;
}

.editor-content :deep(.tiptap blockquote) {
  border-left: 4px solid var(--color-accent);
  padding-left: 16px;
  font-style: italic;
  color: var(--color-text-2);
  margin: 1.5em 0;
}

.editor-content :deep(.tiptap img.editor-image) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-md);
  margin: 1em 0;
}

.editor-content :deep(.tiptap a) {
  color: var(--color-accent);
  text-decoration: underline;
}

.md-btn {
  width: auto;
  padding: 0 6px;
  min-width: 32px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.03em;
  color: var(--color-neon);
}

.md-btn:hover:not(:disabled) {
  background: var(--color-neon-glow);
  color: var(--color-neon);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Markdown modals */
.md-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  background: var(--color-overlay);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.md-modal {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-modal);
  width: 100%;
  max-width: 640px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: md-modal-in 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes md-modal-in {
  from { transform: translateY(16px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.md-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.md-modal-title {
  margin: 0;
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text);
}

.md-modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-text-2);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.md-modal-close:hover {
  background: var(--color-surface-2);
  color: var(--color-accent);
}

.md-textarea {
  width: 100%;
  padding: 1rem;
  border: none;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-2);
  color: var(--color-text);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.6;
  resize: vertical;
  outline: none;
  box-sizing: border-box;
}

.md-textarea:focus {
  background: var(--color-surface);
  box-shadow: inset 0 0 0 2px var(--color-accent);
}

.md-textarea--readonly {
  cursor: text;
  color: var(--color-text-2);
}

.md-modal-footer {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  padding: 0.875rem 1.25rem;
  background: var(--color-surface-2);
}

.md-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.md-action-btn:hover:not(:disabled) {
  background: var(--color-surface-3);
}

.md-action-btn--primary {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: var(--color-on-accent);
}

.md-action-btn--primary:hover:not(:disabled) {
  background: var(--color-accent-hover);
  border-color: var(--color-accent-hover);
}

.md-action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .md-modal-overlay {
    align-items: flex-end;
    padding: 0;
  }
  .md-modal {
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    max-height: 85vh;
  }
}

/* Link dialog */
.link-dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.link-dialog {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.link-dialog h3 {
  margin: 0 0 16px;
  font-size: var(--text-lg);
  font-weight: 600;
}

.link-dialog input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  color: var(--color-text);
  font-size: var(--text-base);
  margin-bottom: 16px;
}

.link-dialog-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.link-dialog-actions button {
  padding: 8px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface-2);
  color: var(--color-text);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
}

.link-dialog-actions button:hover {
  background: var(--color-surface-3);
}

.link-dialog-actions button.primary {
  background: var(--color-accent);
  color: white;
  border-color: var(--color-accent);
}

.link-dialog-actions button.primary:hover {
  opacity: 0.9;
}
</style>
