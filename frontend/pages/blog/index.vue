<script setup lang="ts">
import { useSeo } from '~/composables/useSeo'
import { useBlog, type BlogPost } from '~/composables/useBlog'

const route = useRoute()
const router = useRouter()
const blog = useBlog()

// Query filters
const tag = computed(() => route.query.tag as string | undefined)
const category = computed(() => route.query.category as string | undefined)
const activeSection = computed(() => route.query.section as string | undefined)

const SECTION_TABS = [
  { key: 'all', label: 'Все', value: undefined as string | undefined, testid: 'blog-section-tab-all' },
  { key: 'news', label: 'Новости', value: 'news', testid: 'blog-section-tab-news' },
  { key: 'instructions', label: 'Инструкции', value: 'instructions', testid: 'blog-section-tab-instructions' },
]

function navigateToSection(sectionValue: string | undefined) {
  const query: Record<string, string> = {}
  if (sectionValue) query.section = sectionValue
  if (tag.value) query.tag = tag.value
  if (category.value) query.category = category.value
  router.push({ path: '/blog', query })
}

// Posts fetching state
const cursor = ref<string | null>(null)
const posts = ref<BlogPost[]>([])
const hasMore = ref(false)
const total = ref(0)

const { data: initialData, pending } = await blog.getPosts({
  tag: tag.value,
  category_slug: category.value,
  section: activeSection.value,
  per_page: 12
})

if (initialData.value) {
  posts.value = initialData.value.items
  cursor.value = initialData.value.next_cursor
  hasMore.value = !!initialData.value.next_cursor
  total.value = initialData.value.total
}

// Tags for tag cloud
const { data: tagsData } = await blog.getTags()
const allTags = computed(() => tagsData.value ?? [])

// Watch for filter changes and reset
watch([tag, category, activeSection], async () => {
  cursor.value = null
  const { data: newData } = await blog.getPosts({
    tag: tag.value,
    category_slug: category.value,
    section: activeSection.value,
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
    section: activeSection.value,
    per_page: 12,
    after: cursor.value
  })

  if (nextData.value) {
    posts.value.push(...nextData.value.items)
    cursor.value = nextData.value.next_cursor
    hasMore.value = !!nextData.value.next_cursor
  }
  loadingMore.value = false
}

// Hero post = first post
const heroPosts = computed(() => posts.value[0] ?? null)
const gridPosts = computed(() => posts.value.slice(1))

// Hero image
const getHeroImage = (post: BlogPost): string => {
  if (post.carousel_images?.length) return post.carousel_images[0]
  return post.cover_url || post.cover_image || ''
}

function navigateToTag(tagSlug: string) {
  router.push({ path: '/blog', query: { tag: tagSlug } })
}

function navigateToCategory(categorySlug: string) {
  router.push({ path: '/blog', query: { category: categorySlug } })
}

// SEO
useSeo({
  title: 'Блог — WifiOBD Shop',
  description: 'Статьи об OBD2 диагностике автомобилей, обзоры сканеров и руководства по использованию',
  type: 'website',
})

// Breadcrumbs
const breadcrumbs = computed(() => {
  const crumbs: { label: string; to?: string; icon?: string }[] = [
    { label: 'Главная', to: '/', icon: 'ph:house' },
    { label: 'Блог' },
  ]
  if (activeSection.value === 'news') crumbs.push({ label: 'Новости' })
  if (activeSection.value === 'instructions') crumbs.push({ label: 'Инструкции' })
  if (tag.value) crumbs.push({ label: `Тег: ${tag.value}` })
  if (category.value) crumbs.push({ label: `Категория: ${category.value}` })
  return crumbs
})
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

      <!-- Section Tabs -->
      <div class="section-tabs" data-testid="blog-section-tabs" role="tablist" aria-label="Фильтр по секции">
        <button
          v-for="tab in SECTION_TABS"
          :key="tab.key"
          type="button"
          role="tab"
          :aria-selected="activeSection === tab.value || (!activeSection && tab.key === 'all')"
          :class="['section-tab', { 'section-tab--active': activeSection === tab.value || (!activeSection && tab.key === 'all') }]"
          :data-testid="tab.testid"
          @click="navigateToSection(tab.value)"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Active filters display -->
      <div v-if="tag || category" class="active-filters">
        <span v-if="tag" class="filter-chip">
          Тег: {{ tag }}
          <NuxtLink :to="{ query: { ...route.query, tag: undefined } }" class="remove-filter" aria-label="Удалить фильтр по тегу">
            <Icon name="ph:x-circle-fill" />
          </NuxtLink>
        </span>
        <span v-if="category" class="filter-chip">
          Категория: {{ category }}
          <NuxtLink :to="{ query: { ...route.query, category: undefined } }" class="remove-filter" aria-label="Удалить фильтр по категории">
            <Icon name="ph:x-circle-fill" />
          </NuxtLink>
        </span>
        <NuxtLink to="/blog" class="clear-all">Сбросить всё</NuxtLink>
      </div>

      <!-- Skeleton while loading -->
      <div v-if="pending && !posts.length">
        <div class="hero-skeleton skeleton" />
        <div class="blog-grid mt-8">
          <USkeleton v-for="i in 6" :key="i" height="400px" />
        </div>
      </div>

      <template v-else-if="posts.length">
        <!-- HERO BLOCK -->
        <NuxtLink
          v-if="heroPosts"
          :to="`/blog/${heroPosts.slug}`"
          class="blog-hero"
          :style="{ backgroundImage: `url(${getHeroImage(heroPosts)})` }"
        >
          <div class="blog-hero__overlay" />
          <div class="blog-hero__content">
            <NuxtLink
              v-if="heroPosts.category"
              :to="`/blog?category=${heroPosts.category.slug}`"
              class="blog-hero__category"
              @click.prevent.stop="navigateToCategory(heroPosts.category!.slug)"
            >
              {{ heroPosts.category.name }}
            </NuxtLink>
            <h2 class="blog-hero__title">{{ heroPosts.title }}</h2>
            <p class="blog-hero__excerpt">{{ heroPosts.summary || heroPosts.excerpt }}</p>
            <div class="blog-hero__meta">
              <time v-if="heroPosts.published_at" :datetime="heroPosts.published_at">
                {{ new Date(heroPosts.published_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }) }}
              </time>
              <span v-if="(heroPosts.reading_time_minutes ?? heroPosts.reading_time)">
                · {{ heroPosts.reading_time_minutes ?? heroPosts.reading_time }} мин. чтения
              </span>
            </div>
          </div>
        </NuxtLink>

        <!-- TAG CLOUD -->
        <div v-if="allTags.length" class="tag-cloud" role="navigation" aria-label="Фильтр по тегам">
          <NuxtLink
            v-for="t in allTags"
            :key="t.id"
            :to="`/blog?tag=${t.slug}`"
            class="tag-cloud__item"
            :class="{ 'tag-cloud__item--active': t.slug === tag }"
          >
            {{ t.name }}
          </NuxtLink>
        </div>

        <!-- GRID of remaining posts -->
        <div v-if="gridPosts.length" class="blog-grid">
          <BlogCard
            v-for="post in gridPosts"
            :key="post.id"
            :post="post"
          />
        </div>

        <!-- Load more -->
        <div v-if="hasMore" class="load-more-container">
          <UButton
            variant="secondary"
            :loading="loadingMore"
            @click="loadMore"
          >
            Загрузить ещё ({{ posts.length }} / {{ total }})
          </UButton>
        </div>
      </template>

      <div v-else class="blog-empty">
        <Icon name="ph:newspaper-bold" size="48" />
        <p>Статей пока нет</p>
        <UButton v-if="tag || category" to="/blog" variant="ghost">
          Вернуться ко всем статьям
        </UButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.blog-index {
  padding-top: 2rem;
  padding-bottom: 4rem;
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 clamp(1rem, 5vw, 3rem);
}

.blog-header {
  text-align: center;
  margin-bottom: 2rem;
}

.blog-header h1 {
  font-size: var(--text-3xl);
  font-weight: 800;
  margin-bottom: 1rem;
  color: var(--color-text);
}

.blog-description {
  font-size: var(--text-lg);
  color: var(--color-text-2);
  max-width: 600px;
  margin: 0 auto;
}

/* Section Tabs */
.section-tabs {
  display: flex;
  flex-direction: row;
  gap: 0;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--color-border);
  overflow-x: auto;
  scrollbar-width: none;
}

.section-tabs::-webkit-scrollbar {
  display: none;
}

.section-tab {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.625rem 1.25rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--color-text-2);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: color var(--transition-fast), border-color var(--transition-fast);
  white-space: nowrap;
  margin-bottom: -1px;
}

.section-tab:hover {
  color: var(--color-text);
}

.section-tab--active {
  border-bottom-color: var(--color-accent);
  color: var(--color-text);
  font-weight: 700;
}

/* Active filters */
.active-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 2rem;
  align-items: center;
}

.filter-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
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

.remove-filter:hover { opacity: 1; }

.clear-all {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  text-decoration: underline;
  cursor: pointer;
}

/* Hero skeleton */
.hero-skeleton {
  width: 100%;
  aspect-ratio: 16 / 9;
  min-height: 300px;
  max-height: 520px;
  border-radius: var(--radius-xl);
  margin-bottom: 2rem;
}

/* Hero */
.blog-hero {
  display: block;
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  min-height: 300px;
  max-height: 520px;
  background-size: cover;
  background-position: center;
  background-color: var(--color-surface-2);
  border-radius: var(--radius-xl);
  overflow: hidden;
  text-decoration: none;
  margin-bottom: 2rem;
  cursor: pointer;
}

.blog-hero__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.3) 50%, transparent 100%);
  transition: opacity var(--transition-normal);
}

.blog-hero:hover .blog-hero__overlay {
  opacity: 0.9;
}

.blog-hero__content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: clamp(1.5rem, 4vw, 2.5rem);
  color: #fff;
}

.blog-hero__category {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-accent);
  text-decoration: none;
  margin-bottom: 0.75rem;
  background: rgba(230, 57, 70, 0.2);
  padding: 2px 10px;
  border-radius: var(--radius-full);
}

.blog-hero__title {
  font-size: clamp(1.5rem, 4vw, 2.25rem);
  font-weight: 800;
  line-height: 1.15;
  margin: 0 0 0.75rem;
  color: #ffffff;
}

.blog-hero__excerpt {
  font-size: var(--text-sm);
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
  margin: 0 0 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  max-width: 600px;
}

.blog-hero__meta {
  font-size: var(--text-xs);
  color: rgba(255, 255, 255, 0.65);
}

/* Tag Cloud */
.tag-cloud {
  display: flex;
  flex-wrap: nowrap;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
  padding-bottom: 4px;
  margin-bottom: 2rem;
}

.tag-cloud::-webkit-scrollbar {
  display: none;
}

.tag-cloud__item {
  flex-shrink: 0;
  display: inline-block;
  padding: 6px 16px;
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-2);
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  text-decoration: none;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.tag-cloud__item:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.tag-cloud__item--active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: var(--color-on-accent);
}

/* Grid */
.blog-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 1.5rem;
}

.mt-8 { margin-top: 2rem; }

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
  margin-top: 3rem;
}

.blog-empty {
  text-align: center;
  padding: 4rem 0;
  color: var(--color-text-2);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
</style>
