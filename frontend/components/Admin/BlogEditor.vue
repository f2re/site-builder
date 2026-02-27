<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Typography from '@tiptap/extension-typography'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits(['update:modelValue'])

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    Link.configure({
      openOnClick: false,
    }),
    Image,
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
</script>

<template>
  <div class="blog-editor">
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
  </div>
</template>

<style scoped>
.blog-editor {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  overflow: hidden;
  transition: border-color var(--transition-fast);
}

.blog-editor:focus-within {
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

.editor-toolbar button:hover {
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
</style>
