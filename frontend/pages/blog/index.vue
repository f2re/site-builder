<script setup lang="ts">
import { useSeo } from '~/composables/useSeo'

const config = useRuntimeConfig()
const { data: posts, pending } = await useFetch(`${config.public.apiBase}/api/v1/blog/posts`, {
  query: {
    status: 'published',
    limit: 12,
  },
})

// SEO
useSeo({
  title: 'Блог — WifiOBD Shop',
  description: 'Статьи об OBD2 диагностике автомобилей, обзоры сканеров и руководства по использованию',
  type: 'website',
})

// Breadcrumbs
const breadcrumbs = [
  { label: 'Главная', to: '/', icon: 'ph:house' },
  { label: 'Блог' },
]
</script>

<template>
  <div class="blog-index">
    <div class="container">
      <AppBreadcrumbs :crumbs="breadcrumbs" />
      
      <header class="blog-header">
        <h1>Блог</h1>
        <p class="blog-description">
          Статьи об OBD2 диагностике автомобилей, обзоры сканеров и руководства по использованию
        </p>
      </header>

      <div v-if="pending" class="blog-loading">
        <p>Загрузка...</p>
      </div>

      <div v-else-if="posts?.items?.length" class="blog-grid">
        <article
          v-for="post in posts.items"
          :key="post.id"
          class="blog-card"
        >
          <NuxtLink :to="`/blog/${post.slug}`" class="blog-card-link">
            <img
              v-if="post.og_image_url"
              :src="post.og_image_url"
              :alt="post.title"
              class="blog-card-image"
              loading="lazy"
            />
            <div class="blog-card-content">
              <h2 class="blog-card-title">{{ post.title }}</h2>
              <p class="blog-card-excerpt">{{ post.excerpt }}</p>
              <div class="blog-card-meta">
                <span class="blog-card-date">
                  {{ new Date(post.published_at).toLocaleDateString('ru-RU') }}
                </span>
                <span class="blog-card-reading-time">
                  {{ post.reading_time_minutes }} мин чтения
                </span>
              </div>
            </div>
          </NuxtLink>
        </article>
      </div>

      <div v-else class="blog-empty">
        <p>Статей пока нет</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.blog-index {
  padding: var(--space-8) 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

.blog-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.blog-header h1 {
  font-size: var(--text-3xl);
  font-weight: 700;
  margin-bottom: var(--space-2);
  color: var(--color-text);
}

.blog-description {
  font-size: var(--text-lg);
  color: var(--color-text-2);
  max-width: 600px;
  margin: 0 auto;
}

.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-6);
}

.blog-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  transition: all var(--transition-normal);
}

.blog-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  border-color: var(--color-accent);
}

.blog-card-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.blog-card-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.blog-card-content {
  padding: var(--space-4);
}

.blog-card-title {
  font-size: var(--text-xl);
  font-weight: 600;
  margin-bottom: var(--space-2);
  color: var(--color-text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.blog-card-excerpt {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin-bottom: var(--space-3);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.blog-card-meta {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-xs);
  color: var(--color-text-3);
}

.blog-loading,
.blog-empty {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-text-2);
}
</style>
