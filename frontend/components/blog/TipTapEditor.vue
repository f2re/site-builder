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

const props = defineProps<{
  modelValue: any
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: any]
}>()

const lowlight = createLowlight(common)

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
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getJSON())
  },
})

// Update editor content if modelValue changes externally (e.g. on load)
watch(() => props.modelValue, (val) => {
  const isSame = JSON.stringify(val) === JSON.stringify(editor.value?.getJSON())
  if (isSame) return
  editor.value?.commands.setContent(val, false)
})

const setLink = () => {
  const previousUrl = editor.value?.getAttributes('link').href
  const url = window.prompt('URL', previousUrl)

  if (url === null) return
  if (url === '') {
    editor.value?.chain().focus().extendMarkRange('link').unsetLink().run()
    return
  }
  editor.value?.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
}

const addImage = () => {
  const url = window.prompt('URL изображения')
  if (url) {
    editor.value?.chain().focus().setImage({ src: url }).run()
  }
}

const addYoutube = () => {
  const url = window.prompt('URL YouTube видео')
  if (url) {
    editor.value?.chain().focus().setYoutubeVideo({ src: url }).run()
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
        <button type="button" @click="addImage" title="Image">
          <Icon name="ph:image-bold" />
        </button>
        <button type="button" @click="addYoutube" title="YouTube">
          <Icon name="ph:youtube-logo-bold" />
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
</style>
