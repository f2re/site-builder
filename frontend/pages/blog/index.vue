<script setup lang="ts">
import { useSeo } from '~/composables/useSeo'
import { useBlog } from '~/composables/useBlog'

const route = useRoute()
const blog = useBlog()

// Query filters
const tag = computed(() => route.query.tag as string)
const category = computed(() => route.query.category as string)

// Posts fetching state
const cursor = ref<string | null>(null)
const posts = ref<any[]>([])
const hasMore = ref(false)
const total = ref(0)

const { data: initialData, pending, error } = await blog.getPosts({
  tag: tag.value,
  category_slug: category.value,
  per_page: 12
})

if (initialData.value) {
  posts.value = initialData.value.items
  cursor.value = initialData.value.next_cursor
  hasMore.value = !!initialData.value.next_cursor
  total.value = initialData.value.total
}

// Watch for filter changes and reset
watch([tag, category], async () => {
  const { data: newData } = await blog.getPosts({
    tag: tag.value,
    category_slug: category.value,
    per_page: 12
  })
  
  if (newData.value) {
    posts.value = newData.value.items
    cursor.value = newData.value.next_cursor
    hasMore.value = !!newData.value.next_cursor
    total.value = newData.value.total
  }
})

// Pagination
const loadingMore = ref(false)
const loadMore = async () => {
  if (!cursor.value || loadingMore.value) return
  
  loadingMore.value = true
  const { data: nextData } = await blog.getPosts({
    tag: tag.value,
    category_slug: category.value,
    per_page: 12,
    page_cursor: cursor.value
  })

  if (nextData.value) {
    posts.value.push(...nextData.value.items)
    cursor.value = nextData.value.next_cursor
    hasMore.value = !!nextData.value.next_cursor
  }
  loadingMore.value = false
}

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

if (tag.value) breadcrumbs.push({ label: `Тег: ${tag.value}` })
if (category.value) breadcrumbs.push({ label: `Категория: ${category.value}` })
</script>

<template>
  <div class="blog-index">
    <div class="container">
      <UBreadcrumbs :crumbs="breadcrumbs" />
      
      <header class="blog-header">
        <h1>Блог</h1>
        <p class="blog-description">
          Статьи об OBD2 диагностике автомобилей, обзоры сканеров и руководства по использованию
        </p>
      </header>

      <!-- Active filters display -->
      <div v-if="tag || category" class="active-filters">
        <span v-if="tag" class="filter-chip">
          Тег: {{ tag }}
          <NuxtLink :to="{ query: { ...route.query, tag: undefined } }" class="remove-filter">
            <Icon name="ph:x-circle-fill" />
          </NuxtLink>
        </span>
        <span v-if="category" class="filter-chip">
          Категория: {{ category }}
          <NuxtLink :to="{ query: { ...route.query, category: undefined } }" class="remove-filter">
            <Icon name="ph:x-circle-fill" />
          </NuxtLink>
        </span>
        <NuxtLink to="/blog" class="clear-all">Сбросить всё</NuxtLink>
      </div>

      <div v-if="pending && !posts.length" class="blog-grid">
        <USkeleton v-for="i in 6" :key="i" height="400px" />
      </div>

      <div v-else-if="posts.length" class="blog-container">
        <div class="blog-grid">
          <BlogCard
            v-for="post in posts"
            :key="post.id"
            :post="post"
          />
        </div>

        <div v-if="hasMore" class="load-more-container">
          <UButton
            variant="secondary"
            :loading="loadingMore"
            @click="loadMore"
          >
            Загрузить ещё
          </UButton>
        </div>
      </div>

      <div v-else class="blog-empty">
        <Icon name="ph:article-slash" size="48" />
        <p>Статей пока нет</p>
        <UButton v-if="tag || category" to="/blog" variant="ghost" class="mt-4">
          Вернуться ко всем статьям
        </UButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.blog-index {
  padding: var(--space-8) 0;
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

.blog-header {
  text-align: center;
  margin-bottom: var(--space-12);
}

.blog-header h1 {
  font-size: var(--text-3xl);
  font-weight: 800;
  margin-bottom: var(--space-4);
  color: var(--color-text);
}

.blog-description {
  font-size: var(--text-lg);
  color: var(--color-text-2);
  max-width: 600px;
  margin: 0 auto;
}

.active-filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-bottom: var(--space-8);
  align-items: center;
}

.filter-chip {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--color-accent-glow);
  color: var(--color-accent);
  border-radius: var(--radius-full);
  font-weight: 600;
  font-size: var(--text-sm);
}

.remove-filter {
  display: flex;
  align-items: center;
  color: var(--color-accent);
  opacity: 0.7;
  transition: opacity var(--transition-fast);
}

.remove-filter:hover {
  opacity: 1;
}

.clear-all {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  text-decoration: underline;
  cursor: pointer;
}

.blog-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--space-6);
}

@media (min-width: 768px) {
  .blog-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .blog-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.load-more-container {
  display: flex;
  justify-content: center;
  margin-top: var(--space-12);
}

.blog-empty {
  text-align: center;
  padding: var(--space-16) 0;
  color: var(--color-text-2);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.mt-4 { margin-top: 1rem; }
</style>
