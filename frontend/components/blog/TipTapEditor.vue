<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import Youtube from '@tiptap/extension-youtube'
import Placeholder from '@tiptap/extension-placeholder'
import CharacterCount from '@tiptap/extension-character-count'
import { common, createLowlight } from 'lowlight'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import { Markdown } from 'tiptap-markdown'
import { useToast } from '~/composables/useToast'
import { usePrompt } from '~/composables/usePrompt'

const props = defineProps<{
  modelValue: any
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: any]
}>()

const lowlight = createLowlight(common)
const toast = useToast()
const { prompt: showPrompt } = usePrompt()

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit.configure({
      codeBlock: false, // Use lowlight instead
    }),
    CodeBlockLowlight.configure({
      lowlight,
    }),
    Image.configure({
      HTMLAttributes: {
        class: 'rounded-lg border border-border max-w-full h-auto my-8',
      },
    }),
    Link.configure({
      openOnClick: false,
      HTMLAttributes: {
        class: 'text-accent underline underline-offset-4 hover:text-accent-hover transition-colors',
      },
    }),
    Youtube.configure({
      HTMLAttributes: {
        class: 'aspect-video w-full rounded-lg my-8',
      },
    }),
    Placeholder.configure({
      placeholder: props.placeholder || 'Начните писать историю...',
    }),
    CharacterCount,
    Markdown,
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getJSON())
  },
})

// Update editor content if modelValue changes externally (e.g. on load)
// Handles both HTML strings (from OpenCart migration) and TipTap JSON objects
watch(() => props.modelValue, (val) => {
  if (!editor.value) return
  if (typeof val === 'string') {
    // HTML string — compare via getHTML() to avoid unnecessary updates
    if (editor.value.getHTML() !== val) {
      editor.value.commands.setContent(val, false)
    }
  } else {
    const isSame = JSON.stringify(val) === JSON.stringify(editor.value.getJSON())
    if (!isSame) {
      editor.value.commands.setContent(val ?? '', false)
    }
  }
})

const setLink = async () => {
  const previousUrl = editor.value?.getAttributes('link').href as string | undefined
  const url = await showPrompt({
    title: 'Вставить ссылку',
    label: 'URL',
    placeholder: 'https://example.com',
    defaultValue: previousUrl ?? '',
    inputType: 'url',
    confirmLabel: 'Вставить',
  })

  if (url === null) return
  if (url === '') {
    editor.value?.chain().focus().extendMarkRange('link').unsetLink().run()
    return
  }
  editor.value?.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
}

const { uploadImage } = useMediaUpload()
const imageInputRef = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)

const openImageDialog = () => {
  imageInputRef.value?.click()
}

const handleImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file || !editor.value) return

  if (!file.type.startsWith('image/')) return
  if (file.size > 5 * 1024 * 1024) {
    toast.warning('Файл слишком большой', 'Размер изображения не должен превышать 5 МБ')
    return
  }

  isUploading.value = true
  try {
    const url = await uploadImage(file, file.name, 'content')
    editor.value.chain().focus().setImage({ src: url, alt: file.name }).run()
  } catch {
    // useMediaUpload уже показывает toast с ошибкой
  } finally {
    isUploading.value = false
    if (target) target.value = ''
  }
}

const addYoutube = async () => {
  const url = await showPrompt({
    title: 'Вставить YouTube видео',
    label: 'URL видео',
    placeholder: 'https://youtube.com/watch?v=...',
    inputType: 'url',
    confirmLabel: 'Вставить',
  })
  if (url) {
    editor.value?.chain().focus().setYoutubeVideo({ src: url }).run()
  }
}

// HTML import
const showImportHtml = ref(false)
const htmlInput = ref('')

const openImportHtml = () => {
  htmlInput.value = ''
  showImportHtml.value = true
}

const applyHtml = () => {
  if (!editor.value || !htmlInput.value.trim()) return
  editor.value.commands.setContent(htmlInput.value.trim(), true)
  showImportHtml.value = false
  htmlInput.value = ''
}

// Markdown import/export
const showImportMd = ref(false)
const showExportMd = ref(false)
const markdownInput = ref('')
const markdownOutput = ref('')

const openImportMd = () => {
  markdownInput.value = ''
  showImportMd.value = true
}

const applyMarkdown = () => {
  if (!editor.value || !markdownInput.value.trim()) return
  editor.value.commands.setContent(markdownInput.value)
  showImportMd.value = false
  markdownInput.value = ''
}

const openExportMd = () => {
  if (!editor.value) return
  markdownOutput.value = (editor.value.storage.markdown as { getMarkdown: () => string }).getMarkdown()
  showExportMd.value = true
}

const copyMarkdown = async () => {
  try {
    await navigator.clipboard.writeText(markdownOutput.value)
    toast.success('Скопировано', 'Markdown скопирован в буфер обмена')
  } catch {
    toast.error('Ошибка', 'Не удалось скопировать текст')
  }
}
</script>

<template>
  <div v-if="editor" class="tiptap-editor-wrapper">
    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-group">
        <button 
          type="button" 
          @click="editor.chain().focus().toggleBold().run()" 
          :class="{ 'is-active': editor.isActive('bold') }"
          title="Bold"
        >
          <Icon name="ph:text-b-bold" />
        </button>
        <button 
          type="button" 
          @click="editor.chain().focus().toggleItalic().run()" 
          :class="{ 'is-active': editor.isActive('italic') }"
          title="Italic"
        >
          <Icon name="ph:text-italic-bold" />
        </button>
        <button 
          type="button" 
          @click="editor.chain().focus().toggleStrike().run()" 
          :class="{ 'is-active': editor.isActive('strike') }"
          title="Strike"
        >
          <Icon name="ph:text-strikethrough-bold" />
        </button>
      </div>

      <div class="divider" />

      <div class="toolbar-group">
        <button 
          type="button" 
          @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" 
          :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
          title="H2"
        >
          H2
        </button>
        <button 
          type="button" 
          @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" 
          :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }"
          title="H3"
        >
          H3
        </button>
      </div>

      <div class="divider" />

      <div class="toolbar-group">
        <button 
          type="button" 
          @click="editor.chain().focus().toggleBulletList().run()" 
          :class="{ 'is-active': editor.isActive('bulletList') }"
          title="Bullet List"
        >
          <Icon name="ph:list-bullets-bold" />
        </button>
        <button 
          type="button" 
          @click="editor.chain().focus().toggleOrderedList().run()" 
          :class="{ 'is-active': editor.isActive('orderedList') }"
          title="Ordered List"
        >
          <Icon name="ph:list-numbers-bold" />
        </button>
      </div>

      <div class="divider" />

      <div class="toolbar-group">
        <button 
          type="button" 
          @click="editor.chain().focus().toggleBlockquote().run()" 
          :class="{ 'is-active': editor.isActive('blockquote') }"
          title="Blockquote"
        >
          <Icon name="ph:quotes-bold" />
        </button>
        <button 
          type="button" 
          @click="editor.chain().focus().toggleCodeBlock().run()" 
          :class="{ 'is-active': editor.isActive('codeBlock') }"
          title="Code Block"
        >
          <Icon name="ph:code-bold" />
        </button>
      </div>

      <div class="divider" />

      <div class="toolbar-group">
        <button type="button" @click="setLink" :class="{ 'is-active': editor.isActive('link') }" title="Link">
          <Icon name="ph:link-bold" />
        </button>
        <button type="button" @click="openImageDialog" :disabled="isUploading" title="Image">
          <Icon v-if="!isUploading" name="ph:image-bold" />
          <Icon v-else name="ph:spinner" class="spin" />
        </button>
        <button type="button" @click="addYoutube" title="YouTube">
          <Icon name="ph:youtube-logo-bold" />
        </button>
      </div>

      <div class="divider" />

      <div class="toolbar-group">
        <button
          type="button"
          class="md-btn"
          @click="openImportHtml"
          title="Вставить HTML"
          data-testid="tiptap-import-html-btn"
          aria-label="Вставить HTML"
        >
          HTML↑
        </button>
        <button
          type="button"
          class="md-btn"
          @click="openImportMd"
          title="Вставить Markdown"
          data-testid="tiptap-import-md-btn"
          aria-label="Вставить Markdown"
        >
          MD↑
        </button>
        <button
          type="button"
          class="md-btn"
          @click="openExportMd"
          title="Экспортировать в Markdown"
          data-testid="tiptap-export-md-btn"
          aria-label="Экспортировать в Markdown"
        >
          MD↓
        </button>
      </div>
    </div>

    <!-- Editor Surface -->
    <EditorContent :editor="editor" class="editor-content" />

    <!-- Footer -->
    <div class="editor-footer">
      <div class="char-count">
        {{ editor.storage.characterCount.characters() }} символов
      </div>
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
      <div class="md-modal" data-testid="tiptap-import-html-modal">
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
          data-testid="tiptap-html-input"
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
            data-testid="tiptap-apply-html-btn"
          >
            Применить
          </button>
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
      <div class="md-modal" data-testid="tiptap-import-md-modal">
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
          data-testid="tiptap-md-input"
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
            data-testid="tiptap-apply-md-btn"
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
      <div class="md-modal" data-testid="tiptap-export-md-modal">
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
          data-testid="tiptap-md-output"
        />
        <div class="md-modal-footer">
          <button type="button" class="md-action-btn" @click="showExportMd = false">
            Закрыть
          </button>
          <button
            type="button"
            class="md-action-btn md-action-btn--primary"
            @click="copyMarkdown"
            data-testid="tiptap-copy-md-btn"
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
.tiptap-editor-wrapper {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: border-color var(--transition-fast);
}

.tiptap-editor-wrapper:focus-within {
  border-color: var(--color-accent);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--color-surface-2);
  border-bottom: 1px solid var(--color-border);
}

.toolbar-group {
  display: flex;
  gap: 0.25rem;
}

.divider {
  width: 1px;
  height: 24px;
  background: var(--color-border);
  margin: 0 0.25rem;
  align-self: center;
}

.toolbar button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--color-text-2);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-weight: 600;
  font-size: 14px;
}

.toolbar button:hover {
  background: var(--color-surface-3);
  color: var(--color-text);
}

.toolbar button.is-active {
  background: var(--color-accent);
  color: var(--color-on-accent);
}

.editor-content {
  padding: 1.5rem;
  min-height: 300px;
  cursor: text;
}

:deep(.ProseMirror) {
  outline: none;
  min-height: 300px;
}

:deep(.ProseMirror p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: var(--color-muted);
  pointer-events: none;
  height: 0;
}

:deep(.ProseMirror pre) {
  background: var(--color-surface-2);
  color: var(--color-text);
  padding: 1rem;
  border-radius: var(--radius-md);
  font-family: var(--font-mono);
}

.editor-footer {
  padding: 0.5rem 1rem;
  background: var(--color-surface-2);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
}

.char-count {
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.md-btn {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.03em;
  width: auto;
  padding: 0 6px;
  min-width: 32px;
  color: var(--color-neon);
}

.md-btn:hover {
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
</style>
