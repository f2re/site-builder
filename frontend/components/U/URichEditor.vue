<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Typography from '@tiptap/extension-typography'

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

function openImageDialog() {
  imageInputRef.value?.click()
}

async function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file || !editor.value) return

  // Validate image
  if (!file.type.startsWith('image/')) {
    alert('Пожалуйста, выберите изображение')
    return
  }

  // Max 5MB
  if (file.size > 5 * 1024 * 1024) {
    alert('Размер изображения не должен превышать 5 МБ')
    return
  }

  isUploading.value = true

  try {
    // Get alt text from user (for SEO)
    const alt = prompt('Введите alt-текст для изображения (описание):') || ''

    // Upload to MinIO
    const publicUrl = await uploadImage(file, alt, 'content')

    // Insert into editor
    editor.value.chain().focus().setImage({ src: publicUrl, alt }).run()
  } catch (error: any) {
    alert(error.message || 'Ошибка загрузки изображения')
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
    </div>
    
    <EditorContent :editor="editor" class="editor-content" />
    
    <!-- Hidden file input for image upload -->
    <input
      ref="imageInputRef"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleImageUpload"
    />
    
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

.editor-content {
  padding: 16px;
  min-height: 300px;
  max-height: 600px;
  overflow-y: auto;
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

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
