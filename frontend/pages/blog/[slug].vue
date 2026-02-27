<script setup lang="ts">
import { useBlog } from '~/composables/useBlog'
import { useArticleSchema } from '~/composables/useSchemaOrg'
import AppBreadcrumbs from '~/components/AppBreadcrumbs.vue'

const route = useRoute()
const config = useRuntimeConfig()
const { getPost } = useBlog()
const slug = route.params.slug as string

const { data: post, pending, error } = await getPost(slug)

if (!post.value && !pending.value) {
  throw createError({ statusCode: 404, statusMessage: 'Статья не найдена' })
}

// SEO Meta
useSeoMeta({
  title: () => post.value?.title ? `${post.value.title} | WifiOBD Blog` : 'Блог',
  description: () => post.value?.summary || '',
  ogTitle: () => post.value?.title,
  ogDescription: () => post.value?.summary,
  ogImage: () => post.value?.cover_url ? (post.value.cover_url.startsWith('http') ? post.value.cover_url : `${config.public.siteUrl}${post.value.cover_url}`) : undefined,
  twitterCard: 'summary_large_image',
})

useHead({
  link: [
    { rel: 'canonical', href: () => `${config.public.siteUrl}/blog/${slug}` }
  ]
})

// Schema.org
watchEffect(() => {
  if (post.value) {
    useArticleSchema(post.value)
  }
})

const breadcrumbItems = computed(() => [
  { name: 'Блог', path: '/blog' },
  { name: post.value?.title || '...', path: `/blog/${slug}` }
])
</script>

<template>
  <div class="post-page">
    <div class="container">
      <AppBreadcrumbs :items="breadcrumbItems" />

      <div v-if="pending" class="loading-container">
        <div class="skeleton-hero"></div>
        <div class="skeleton-text" v-for="i in 10" :key="i"></div>
      </div>

      <article v-else-if="post" class="post-content">
        <header class="post-header">
          <div class="post-meta">
            <span class="category" v-if="post.category">{{ post.category.name }}</span>
            <span class="date">{{ new Date(post.published_at).toLocaleDateString('ru-RU') }}</span>
            <span class="dot">·</span>
            <span class="reading-time">{{ post.reading_time_min || 5 }} мин чтения</span>
          </div>
          <h1 class="post-title">{{ post.title }}</h1>
          <div class="author-info" v-if="post.author">
            <NuxtImg 
              :src="post.author.avatar_url || '/img/avatar-placeholder.png'" 
              alt="" 
              class="author-avatar"
              width="32"
              height="32"
            />
            <span class="author-name">{{ post.author.name }}</span>
          </div>
        </header>

        <div class="post-hero" v-if="post.cover_url">
          <NuxtImg 
            :src="post.cover_url" 
            :alt="post.title" 
            class="hero-image"
            format="webp"
            loading="eager"
          />
        </div>

        <div class="post-body" v-html="post.content"></div>

        <footer class="post-footer">
          <div class="tags" v-if="post.tags && post.tags.length">
            <span v-for="tag in post.tags" :key="tag.id" class="tag">#{{ tag.name }}</span>
          </div>
        </footer>
      </article>

      <div v-else-if="error" class="error-container">
        <h2>Ошибка загрузки</h2>
        <p>{{ error.message }}</p>
        <NuxtLink to="/blog" class="btn">Вернуться в блог</NuxtLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-page {
  padding: 40px 0;
}

.post-content {
  max-width: 800px;
  margin: 0 auto;
}

.post-header {
  margin-bottom: 40px;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--color-text-2);
  font-size: var(--text-sm);
  margin-bottom: 16px;
}

.category {
  color: var(--color-accent);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.post-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 24px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: var(--color-surface-2);
}

.author-name {
  font-weight: 600;
  color: var(--color-text);
}

.post-hero {
  margin-bottom: 48px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-card);
}

.hero-image {
  width: 100%;
  aspect-ratio: 16/9;
  object-fit: cover;
  display: block;
}

.post-body {
  font-size: var(--text-base);
  line-height: 1.7;
  color: var(--color-text);
}

/* Typography for v-html content */
:deep(.post-body) h2 { margin: 48px 0 24px; font-size: var(--text-xl); font-weight: 700; }
:deep(.post-body) p { margin-bottom: 24px; }
:deep(.post-body) img { max-width: 100%; border-radius: var(--radius-md); margin: 32px 0; }
:deep(.post-body) blockquote {
  border-left: 4px solid var(--color-accent);
  padding: 16px 24px;
  background: var(--color-surface-2);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  margin: 32px 0;
  font-style: italic;
}

.post-footer {
  margin-top: 64px;
  padding-top: 32px;
  border-top: 1px solid var(--color-border);
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tag {
  color: var(--color-text-2);
  font-size: var(--text-sm);
  transition: color var(--transition-fast);
  cursor: pointer;
}

.tag:hover {
  color: var(--color-accent);
}

.loading-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-hero {
  height: 400px;
  background: var(--color-surface-2);
  border-radius: var(--radius-lg);
}

.skeleton-text {
  height: 20px;
  background: var(--color-surface-2);
  border-radius: var(--radius-sm);
}

@media (max-width: 768px) {
  .post-title {
    font-size: var(--text-xl);
  }
}
</style>
