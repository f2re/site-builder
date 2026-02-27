<script setup lang="ts">
import DOMPurify from 'dompurify'

const props = defineProps<{
  content: string
}>()

const sanitizedContent = computed(() => {
  if (process.server) return props.content // Bleach already cleaned it on backend
  return DOMPurify.sanitize(props.content, {
    ADD_TAGS: ['iframe'], // YouTube/etc
    ADD_ATTR: ['allow', 'allowfullscreen', 'frameborder', 'scrolling']
  })
})
</script>

<template>
  <article 
    class="post-content prose prose-invert max-w-none"
    v-html="sanitizedContent"
  />
</template>

<style scoped>
.post-content {
  color: var(--color-text);
  line-height: 1.75;
  font-size: var(--text-base);
}

:deep(.post-content h2) {
  font-size: var(--text-xl);
  font-weight: 700;
  margin-top: 2.5rem;
  margin-bottom: 1.25rem;
  color: var(--color-text);
}

:deep(.post-content h3) {
  font-size: var(--text-lg);
  font-weight: 600;
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: var(--color-text);
}

:deep(.post-content p) {
  margin-bottom: 1.5rem;
}

:deep(.post-content a) {
  color: var(--color-accent);
  text-decoration: underline;
  text-underline-offset: 4px;
  transition: color var(--transition-fast);
}

:deep(.post-content a:hover) {
  color: var(--color-accent-hover);
}

:deep(.post-content img) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-lg);
  margin: 2rem 0;
  border: 1px solid var(--color-border);
}

:deep(.post-content blockquote) {
  padding-left: 1.5rem;
  border-left: 4px solid var(--color-accent);
  font-style: italic;
  color: var(--color-text-2);
  margin: 2rem 0;
}

:deep(.post-content pre) {
  background: var(--color-surface-2);
  padding: 1.5rem;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 1.5rem 0;
  border: 1px solid var(--color-border);
}

:deep(.post-content code) {
  font-family: var(--font-mono);
  font-size: 0.9em;
  background: var(--color-surface-2);
  padding: 0.2rem 0.4rem;
  border-radius: var(--radius-sm);
}

:deep(.post-content ul), :deep(.post-content ol) {
  margin-bottom: 1.5rem;
  padding-left: 1.5rem;
}

:deep(.post-content li) {
  margin-bottom: 0.5rem;
}

:deep(.post-content iframe) {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-lg);
  margin: 2rem 0;
  border: none;
}
</style>
