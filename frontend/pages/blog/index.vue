<script setup lang="ts">
import { useBlog } from '~/composables/useBlog'
import BlogCard from '~/components/blog/BlogCard.vue'
import AppBreadcrumbs from '~/components/AppBreadcrumbs.vue'

const { getPosts } = useBlog()
const route = useRoute()
const config = useRuntimeConfig()

const activeTag = computed(() => route.query.tag as string | undefined)

const { data: postsData, pending } = await getPosts({
  tag: activeTag.value,
  per_page: 12
})

// SEO
useSeoMeta({
  title: 'Блог | WifiOBD',
  description: 'Полезные статьи, обзоры оборудования и новости мира автодиагностики. Читайте наш блог, чтобы быть в курсе последних тенденций.',
  ogTitle: 'Блог | WifiOBD — Оборудование для диагностики авто',
  ogDescription: 'Полезные статьи, обзоры оборудования и новости мира автодиагностики.',
  ogType: 'website',
  ogImage: `${config.public.siteUrl}/img/og-blog.jpg`
})

useHead({
  link: [
    { 
      rel: 'canonical', 
      href: () => {
        const url = new URL(`${config.public.siteUrl}/blog`)
        if (activeTag.value) {
          url.searchParams.set('tag', activeTag.value)
        }
        return url.toString()
      }
    }
  ]
})

const breadcrumbItems = computed(() => {
  const items = [{ name: 'Блог', path: '/blog' }]
  if (activeTag.value) {
    items.push({ name: activeTag.value, path: `/blog?tag=${activeTag.value}` })
  }
  return items
})
</script>

<template>
  <div class="blog-page">
    <div class="container">
      <AppBreadcrumbs :items="breadcrumbItems" />

      <header class="blog-page__header">
        <h1 class="blog-page__title">Блог</h1>
        <p class="blog-page__subtitle">Экспертные статьи и обзоры для профессионалов</p>

        <!-- Tags filter (Simple horizontal list) -->
        <div class="blog-tags" v-if="postsData">
          <NuxtLink
            to="/blog"
            class="tag-link"
            :class="{ 'is-active': !activeTag }"
          >
            Все
          </NuxtLink>
          <NuxtLink
            v-for="tag in ['Диагностика', 'Новости', 'Обзоры', 'Прошивка']"
            :key="tag"
            :to="{ path: '/blog', query: { tag } }"
            class="tag-link"
            :class="{ 'is-active': activeTag === tag }"
          >
            #{{ tag }}
          </NuxtLink>
        </div>
      </header>

      <!-- Loading State -->
      <div v-if="pending" class="blog-grid">
        <div v-for="i in 6" :key="i" class="blog-card-skeleton skeleton"></div>
      </div>

      <!-- Blog List -->
      <div v-else-if="postsData?.items.length" class="blog-grid">
        <TransitionGroup name="list">
          <BlogCard
            v-for="post in postsData.items"
            :key="post.id"
            :post="post"
          />
        </TransitionGroup>
      </div>

      <!-- Empty State -->
      <div v-else class="blog-page__empty">
        <h2>Статей пока нет</h2>
        <p>Мы работаем над новым контентом. Заходите позже!</p>
        <NuxtLink to="/blog" class="btn btn--primary">Сбросить фильтры</NuxtLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.blog-page {
  padding: 40px 0 60px;
}

.blog-page__header {
  text-align: center;
  max-width: 800px;
  margin: 0 auto 60px;
}

.blog-page__title {
  font-size: var(--text-3xl);
  font-weight: 900;
  margin-bottom: 16px;
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: -0.02em;
}

.blog-page__subtitle {
  font-size: var(--text-lg);
  color: var(--color-text-2);
  margin-bottom: 32px;
}

.blog-tags {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
}

.tag-link {
  padding: 8px 16px;
  border-radius: var(--radius-full);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text-2);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: 600;
  transition: all var(--transition-fast);
}

.tag-link:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.tag-link.is-active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: var(--color-on-accent);
  box-shadow: var(--shadow-glow-accent);
}

.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 32px;
}

.blog-card-skeleton {
  aspect-ratio: 4 / 5;
  border-radius: var(--radius-lg);
}

.blog-page__empty {
  text-align: center;
  padding: 100px 20px;
}

@media (max-width: 768px) {
  .blog-grid {
    grid-template-columns: 1fr;
  }
}
</style>
