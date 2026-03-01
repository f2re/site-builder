<script setup lang="ts">
import { useBlog } from '~/composables/useBlog'
import { useArticleSeo } from '~/composables/useSeo'
import BlogCard from '~/components/blog/BlogCard.vue'
import AppBreadcrumbs from '~/components/AppBreadcrumbs.vue'
import { watchEffect, computed } from 'vue'

const route = useRoute()
const config = useRuntimeConfig()
const { getPost, getPosts } = useBlog()

const { data: post, error } = await getPost(route.params.slug as string)

if (error.value || !post.value) {
  throw createError({
    statusCode: 404,
    message: 'Статья не найдена',
  })
}

// SEO & Schema.org
watchEffect(() => {
  if (post.value) {
    useArticleSeo(post)
  }
})

// Related articles
const { data: relatedResponse } = await getPosts({
  category_slug: post.value.category?.slug,
  per_page: 4,
})

const relatedPosts = computed(() => {
  if (!relatedResponse.value?.items) return []
  return relatedResponse.value.items
    .filter(p => p.slug !== post.value?.slug)
    .slice(0, 3)
})

// Breadcrumbs
const breadcrumbs = [
  { label: 'Главная', to: '/', icon: 'ph:house' },
  { label: 'Блог', to: '/blog' },
  { label: post.value.title },
]
</script>

<template>
  <article class="blog-post">
    <div class="container">
      <AppBreadcrumbs :crumbs="breadcrumbs" />

      <header class="post-header">
        <h1 class="post-title">{{ post.title }}</h1>
        
        <div class="post-meta">
          <time :datetime="post.published_at" class="post-date">
            {{ new Date(post.published_at).toLocaleDateString('ru-RU', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            }) }}
          </time>
          <span class="post-reading-time">
            <Icon name="ph:clock" />
            {{ post.reading_time_minutes }} мин
          </span>
          <span v-if="post.views" class="post-views">
            <Icon name="ph:eye" />
            {{ post.views }}
          </span>
        </div>

        <img
          v-if="post.og_image_url || post.cover_url"
          :src="post.og_image_url || post.cover_url"
          :alt="post.title"
          class="post-cover"
          loading="eager"
          fetchpriority="high"
        />
      </header>

      <div class="post-content" v-html="post.content_html" />

      <footer class="post-footer">
        <div v-if="post.tags?.length" class="post-tags">
          <span class="post-tags-label">Теги:</span>
          <NuxtLink
            v-for="tag in post.tags"
            :key="typeof tag === 'string' ? tag : tag.id"
            :to="`/blog?tag=${typeof tag === 'string' ? tag : tag.slug}`"
            class="post-tag"
          >
            {{ typeof tag === 'string' ? tag : tag.name }}
          </NuxtLink>
        </div>

        <NuxtLink to="/blog" class="back-link">
          <Icon name="ph:arrow-left" />
          Вернуться к блогу
        </NuxtLink>
      </footer>

      <!-- Related Articles -->
      <section v-if="relatedPosts.length" class="related-posts">
        <h2 class="related-posts__title">Похожие статьи</h2>
        <div class="related-posts__grid">
          <BlogCard
            v-for="related in relatedPosts"
            :key="related.id"
            :post="related"
          />
        </div>
      </section>
    </div>
  </article>
</template>

<style scoped>
.blog-post {
  padding: var(--space-8) 0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

.post-header {
  margin-bottom: var(--space-8);
}

.post-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  margin-bottom: var(--space-4);
  color: var(--color-text);
  line-height: 1.2;
}

.post-meta {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin-bottom: var(--space-6);
}

.post-reading-time,
.post-views {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.post-cover {
  width: 100%;
  height: auto;
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-6);
}

.post-content {
  font-size: var(--text-base);
  line-height: 1.7;
  color: var(--color-text);
  margin-bottom: var(--space-8);
}

.post-content :deep(h2) {
  font-size: var(--text-2xl);
  font-weight: 700;
  margin: var(--space-8) 0 var(--space-4);
  color: var(--color-accent);
}

.post-content :deep(h3) {
  font-size: var(--text-xl);
  font-weight: 600;
  margin: var(--space-6) 0 var(--space-3);
}

.post-content :deep(p) {
  margin-bottom: var(--space-4);
}

.post-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
}

.post-content :deep(a) {
  color: var(--color-accent);
  text-decoration: underline;
}

.post-content :deep(blockquote) {
  border-left: 4px solid var(--color-accent);
  padding-left: var(--space-4);
  font-style: italic;
  color: var(--color-text-2);
  margin: var(--space-6) 0;
}

.post-content :deep(ul),
.post-content :deep(ol) {
  padding-left: var(--space-6);
  margin-bottom: var(--space-4);
}

.post-content :deep(code) {
  background: var(--color-surface-2);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.post-content :deep(pre) {
  background: var(--color-surface-2);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: var(--space-4) 0;
}

.post-footer {
  border-top: 1px solid var(--color-border);
  padding-top: var(--space-6);
  margin-bottom: var(--space-12);
}

.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
  margin-bottom: var(--space-6);
}

.post-tags-label {
  font-weight: 600;
  color: var(--color-text-2);
}

.post-tag {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  background: var(--color-surface-2);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  color: var(--color-text-2);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.post-tag:hover {
  background: var(--color-accent-glow);
  color: var(--color-accent);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 500;
  transition: gap var(--transition-fast);
}

.back-link:hover {
  gap: var(--space-3);
}

/* Related Posts */
.related-posts {
  margin-top: var(--space-12);
  padding-top: var(--space-8);
  border-top: 1px solid var(--color-border);
}

.related-posts__title {
  font-size: var(--text-2xl);
  font-weight: 700;
  margin-bottom: var(--space-6);
}

.related-posts__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-6);
}

@media (min-width: 640px) {
  .related-posts__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
