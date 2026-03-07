<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import { onBeforeUnmount } from 'vue'

const props = defineProps<{
  content: unknown
}>()

const editor = useEditor({
  content: props.content as Record<string, unknown>,
  editable: false,
  extensions: [
    StarterKit,
    Image.configure({
      inline: false,
      allowBase64: true
    })
  ]
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})
</script>

<template>
  <EditorContent :editor="editor" class="tiptap-viewer" />
</template>

<style scoped>
.tiptap-viewer {
  color: var(--color-text-2);
  line-height: 1.6;
  font-size: var(--text-base);
}

.tiptap-viewer :deep(p) {
  margin-bottom: 1em;
}

.tiptap-viewer :deep(h1),
.tiptap-viewer :deep(h2),
.tiptap-viewer :deep(h3),
.tiptap-viewer :deep(h4) {
  color: var(--color-text);
  font-weight: 700;
  margin-bottom: 0.5em;
  margin-top: 1.5em;
}

.tiptap-viewer :deep(ul),
.tiptap-viewer :deep(ol) {
  padding-left: 1.5em;
  margin-bottom: 1em;
}

.tiptap-viewer :deep(li) {
  margin-bottom: 0.25em;
}

.tiptap-viewer :deep(blockquote) {
  border-left: 4px solid var(--color-accent);
  padding-left: 1em;
  color: var(--color-muted);
  font-style: italic;
  margin: 1em 0;
}

.tiptap-viewer :deep(code) {
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 2px 6px;
  font-family: var(--font-mono);
  font-size: 0.9em;
  color: var(--color-neon);
}

.tiptap-viewer :deep(pre) {
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1em;
  overflow-x: auto;
  margin-bottom: 1em;
}

.tiptap-viewer :deep(pre code) {
  background: none;
  border: none;
  padding: 0;
}

.tiptap-viewer :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-md);
  margin: 1em 0;
}

.tiptap-viewer :deep(a) {
  color: var(--color-accent);
  text-decoration: underline;
}

.tiptap-viewer :deep(hr) {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: 2em 0;
}
</style>
