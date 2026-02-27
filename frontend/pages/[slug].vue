<script setup lang="ts">
const route = useRoute()
const { getPageBySlug } = usePages()
const slug = route.params.slug as string

const { data: page, pending, error } = await getPageBySlug(slug)

if (!page.value && !pending.value) {
  throw createError({ statusCode: 404, statusMessage: 'Страница не найдена' })
}

watchEffect(() => {
  if (page.value) {
    useSeo({
      title: page.value.meta_title || page.value.title,
      description: page.value.meta_description || '',
    })
  }
})
</script>

<template>
  <div class="page-container">
    <div v-if="pending" class="page-loading">
      <div class="skeleton-title"></div>
      <div class="skeleton-content"></div>
    </div>

    <div v-else-if="error" class="page-error">
      <h1>Ошибка загрузки</h1>
      <p>{{ error.message }}</p>
      <UButton to="/" variant="primary">На главную</UButton>
    </div>

    <article v-else-if="page" class="dynamic-page">
      <header class="page-header">
        <h1 class="page-title">{{ page.title }}</h1>
      </header>

      <div class="page-content" v-html="page.content"></div>
    </article>
  </div>
</template>

<style scoped>
.page-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 4rem 1.5rem;
  min-height: 60vh;
}

.page-header {
  margin-bottom: 3rem;
  text-align: center;
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: 1rem;
}

.page-content {
  color: var(--color-text-2);
  line-height: 1.8;
  font-size: var(--text-base);
}

.page-content :deep(h2) {
  font-size: var(--text-xl);
  color: var(--color-text);
  margin-top: 2.5rem;
  margin-bottom: 1rem;
}

.page-content :deep(p) {
  margin-bottom: 1.5rem;
}

.page-content :deep(ul), .page-content :deep(ol) {
  margin-bottom: 1.5rem;
  padding-left: 1.5rem;
}

.page-content :deep(li) {
  margin-bottom: 0.5rem;
}

.skeleton-title {
  height: 3rem;
  width: 60%;
  margin: 0 auto 3rem;
  background: var(--color-skeleton);
  border-radius: var(--radius-md);
  animation: skeleton-shimmer 1.4s ease-in-out infinite;
}

.skeleton-content {
  height: 20rem;
  width: 100%;
  background: var(--color-skeleton);
  border-radius: var(--radius-md);
  animation: skeleton-shimmer 1.4s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
  0% { opacity: 0.5; }
  50% { opacity: 0.8; }
  100% { opacity: 0.5; }
}

@media (max-width: 768px) {
  .page-container {
    padding: 2rem 1rem;
  }
}
</style>
