<script setup lang="ts">
import { useBlog } from '~/composables/useBlog'
import { useArticleSeo } from '~/composables/useSeo'

const route = useRoute()
const { getPost, getPosts } = useBlog()
const toast = useToast()

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

// Reading progress bar
const readingProgress = ref(0)
const articleRef = ref<HTMLElement | null>(null)

function updateProgress() {
  const scrollTop = window.scrollY
  const docHeight = document.documentElement.scrollHeight - window.innerHeight
  readingProgress.value = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0
}

onMounted(() => {
  window.addEventListener('scroll', updateProgress, { passive: true })
  updateProgress()
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateProgress)
})

// Computed helpers
const heroImages = computed(() => post.value?.carousel_images ?? [])
const hasCarousel = computed(() => heroImages.value.length > 1)
const singleCover = computed(() => {
  const p = post.value
  if (!p) return ''
  return p.cover_url || p.cover_image || ''
})
const readingTime = computed(() =>
  post.value?.reading_time_minutes ?? post.value?.reading_time ?? 5
)

const getTagSlug = (tag: string | { id: string; name: string; slug: string }) => {
  if (typeof tag === 'string') return tag
  return tag.slug || tag.name || ''
}

const getTagName = (tag: string | { id: string; name: string; slug: string }) => {
  if (typeof tag === 'string') return tag
  return tag.name || 'Тег'
}

const getTagKey = (tag: string | { id: string; name: string; slug: string }, index: number) => {
  if (typeof tag === 'string') return tag + index
  return (tag as { id?: string }).id || (tag as { name?: string }).name || String(index)
}

const pageUrl = computed(() => {
  if (!import.meta.client) return ''
  return window.location.href
})

async function copyLink() {
  if (!import.meta.client) return
  try {
    await navigator.clipboard.writeText(window.location.href)
    toast.success('Ссылка скопирована')
  } catch {
    toast.error('Не удалось скопировать ссылку')
  }
}

const formattedDate = computed(() => {
  if (!post.value?.published_at) return ''
  return new Date(post.value.published_at).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
})
</script>

<template>
  <div>
    <!-- Reading Progress Bar -->
    <div
      class="reading-progress"
      data-testid="reading-progress-bar"
      role="progressbar"
      :aria-valuenow="readingProgress"
      aria-valuemin="0"
      aria-valuemax="100"
      :style="{ width: `${readingProgress}%` }"
    />

    <article ref="articleRef" class="blog-post">
      <div class="container">
        <AppBreadcrumbs :crumbs="breadcrumbs" />

        <!-- Hero image / carousel -->
        <div v-if="hasCarousel || singleCover" class="post-hero-image">
          <BlogCarousel
            v-if="hasCarousel"
            :images="heroImages"
            :alt="post!.title"
            aspect-ratio="16/9"
          />
          <NuxtImg
            v-else
            :src="singleCover"
            :alt="post!.title"
            class="post-cover"
            loading="eager"
            width="800"
            height="450"
            fit="cover"
          />
        </div>

        <!-- Article header -->
        <header class="post-header">
          <NuxtLink
            v-if="post!.category"
            :to="`/blog?category=${post!.category!.slug}`"
            class="post-category"
          >
            {{ post!.category!.name }}
          </NuxtLink>

          <h1 class="post-title" data-testid="blog-post-title">{{ post!.title }}</h1>

          <div class="post-meta">
            <time v-if="post!.published_at" :datetime="post!.published_at">
              {{ formattedDate }}
            </time>
            <span v-if="readingTime" class="post-meta__item">
              <Icon name="ph:clock" size="14" aria-hidden="true" />
              {{ readingTime }} мин
            </span>
            <span v-if="post!.views > 0" class="post-meta__item">
              <Icon name="ph:eye" size="14" aria-hidden="true" />
              {{ post!.views }}
            </span>
          </div>

          <!-- Author -->
          <div class="post-author-mini" data-testid="blog-post-author">
            <div class="post-author-mini__avatar" :title="post!.author?.name || 'Аноним'">
              <img
                v-if="post!.author?.avatar_url"
                :src="post!.author.avatar_url"
                :alt="post!.author?.name || 'Аноним'"
              />
              <span v-else>{{ post!.author?.name?.charAt(0) || '?' }}</span>
            </div>
            <span class="post-author-mini__name">{{ post!.author?.name || 'Аноним' }}</span>
          </div>
        </header>

        <!-- Content -->
        <div
          class="post-content"
          v-html="post!.content_html"
          data-testid="blog-post-content"
        />

        <!-- Tags -->
        <div v-if="post!.tags?.length" class="post-tags" data-testid="blog-post-tags">
          <span class="post-tags__label">Теги:</span>
          <NuxtLink
            v-for="(tag, index) in post!.tags"
            :key="getTagKey(tag, index)"
            :to="`/blog?tag=${getTagSlug(tag)}`"
            class="post-tag"
          >
            {{ getTagName(tag) }}
          </NuxtLink>
        </div>

        <!-- Author section -->
        <div class="post-author" data-testid="blog-post-author-section">
          <div class="post-author__avatar">
            <img
              v-if="post!.author?.avatar_url"
              :src="post!.author.avatar_url"
              :alt="post!.author?.name || 'Аноним'"
            />
            <span v-else>{{ post!.author?.name?.charAt(0) || '?' }}</span>
          </div>
          <div class="post-author__info">
            <div class="post-author__name">{{ post!.author?.name || 'Аноним' }}</div>
            <div v-if="post!.author?.bio" class="post-author__bio">{{ post!.author.bio }}</div>
          </div>
        </div>

        <!-- Share section -->
        <div class="post-share">
          <a
            :href="`https://t.me/share/url?url=${encodeURIComponent(pageUrl)}&text=${encodeURIComponent(post!.title)}`"
            target="_blank"
            rel="noopener noreferrer"
            class="share-btn share-btn--telegram"
            data-testid="share-telegram"
            aria-label="Поделиться в Telegram"
          >
            <Icon name="ph:telegram-logo-bold" size="18" />
            Telegram
          </a>
          <a
            :href="`https://vk.com/share.php?url=${encodeURIComponent(pageUrl)}`"
            target="_blank"
            rel="noopener noreferrer"
            class="share-btn share-btn--vk"
            data-testid="share-vk"
            aria-label="Поделиться ВКонтакте"
          >
            <Icon name="ph:share-network-bold" size="18" />
            ВКонтакте
          </a>
          <button
            type="button"
            class="share-btn share-btn--copy"
            data-testid="share-copy"
            aria-label="Скопировать ссылку"
            @click="copyLink"
          >
            <Icon name="ph:link-bold" size="18" />
            Скопировать
          </button>
        </div>

        <!-- Back link -->
        <NuxtLink to="/blog" class="back-link">
          <Icon name="ph:arrow-left" />
          Вернуться к блогу
        </NuxtLink>

        <!-- Related Articles -->
        <section v-if="relatedPosts.length" class="related-posts">
          <h2 class="related-posts__title">Читайте также</h2>
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
  </div>
</template>

<style scoped>
/* Reading progress bar */
.reading-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: var(--color-accent);
  z-index: var(--z-overlay);
  transition: width 100ms linear;
  pointer-events: none;
}

.blog-post {
  padding: 2rem 0 4rem;
}

.container {
  max-width: 680px;
  margin: 0 auto;
  padding: 0 clamp(1.25rem, 5vw, 0px);
}

@media (min-width: 768px) {
  .container {
    padding: 0 1.5rem;
  }
}

/* Hero image */
.post-hero-image {
  margin-bottom: 2rem;
  border-radius: 0;
  overflow: hidden;
}

@media (min-width: 768px) {
  .post-hero-image {
    border-radius: var(--radius-xl);
  }
}

.post-cover {
  width: 100%;
  height: auto;
  display: block;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

/* Article header */
.post-header {
  margin-bottom: 2rem;
}

.post-category {
  display: inline-block;
  font-size: var(--text-sm);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-accent);
  text-decoration: none;
  margin-bottom: 0.75rem;
}

.post-category:hover {
  text-decoration: underline;
}

.post-title {
  font-size: clamp(1.75rem, 5vw, 2.5rem);
  font-weight: 800;
  line-height: 1.15;
  margin: 0 0 1rem;
  color: var(--color-text);
}

.post-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin-bottom: 1.25rem;
}

.post-meta__item {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Author mini */
.post-author-mini {
  display: flex;
  align-items: center;
  gap: 10px;
}

.post-author-mini__avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-accent);
  color: var(--color-on-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.post-author-mini__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.post-author-mini__name {
  font-weight: 600;
  font-size: var(--text-sm);
  color: var(--color-text);
}

/* Content */
.post-content {
  font-size: 1.125rem;
  line-height: 1.75;
  color: var(--color-text);
  margin-bottom: 2.5rem;
}

.post-content :deep(p) {
  margin-bottom: 1.5em;
}

.post-content :deep(h2) {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 2.5em 0 0.75em;
  border-left: 3px solid var(--color-accent);
  padding-left: 0.75em;
  color: var(--color-text);
  line-height: 1.25;
}

.post-content :deep(h3) {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 2em 0 0.5em;
  color: var(--color-text);
}

.post-content :deep(a) {
  color: var(--color-accent);
  text-decoration: underline dotted;
  text-underline-offset: 3px;
}

.post-content :deep(a:hover) {
  text-decoration: underline solid;
}

.post-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-md);
  margin: 2em auto;
  display: block;
}

.post-content :deep(blockquote) {
  border-left: 4px solid var(--color-accent);
  padding-left: 1.5em;
  margin: 2em 0;
  font-style: italic;
  color: var(--color-text-2);
}

.post-content :deep(pre) {
  background: var(--color-surface-2);
  padding: 1.5em;
  border-radius: var(--radius-md);
  overflow-x: auto;
  font-size: 0.875rem;
  margin: 1.5em 0;
}

.post-content :deep(code) {
  background: var(--color-surface-2);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.875em;
  font-family: var(--font-mono);
}

.post-content :deep(pre code) {
  background: none;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
}

.post-content :deep(ul),
.post-content :deep(ol) {
  padding-left: 1.5em;
  margin-bottom: 1.5em;
}

.post-content :deep(li) {
  margin-bottom: 0.5em;
}

.post-content :deep(hr) {
  border: none;
  height: 1px;
  background: var(--color-border);
  margin: 3em 0;
}

.post-content :deep(iframe) {
  max-width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-md);
  width: 100%;
}

.post-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid var(--color-border);
  margin: 1.5em 0;
}

.post-content :deep(th),
.post-content :deep(td) {
  padding: 0.75em 1em;
  border: 1px solid var(--color-border);
  text-align: left;
}

.post-content :deep(th) {
  background: var(--color-surface-2);
  font-weight: 700;
}

/* Tags */
.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  padding: 1.5rem 0;
  border-top: 1px solid var(--color-border);
  margin-bottom: 1.5rem;
}

.post-tags__label {
  font-weight: 600;
  color: var(--color-text-2);
  font-size: var(--text-sm);
}

.post-tag {
  display: inline-block;
  padding: 4px 14px;
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

/* Author section */
.post-author {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  border-top: 1px solid var(--color-border);
  margin-bottom: 2rem;
}

.post-author__avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-accent);
  color: var(--color-on-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  flex-shrink: 0;
}

.post-author__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.post-author__info {
  flex: 1;
}

.post-author__name {
  font-weight: 700;
  font-size: var(--text-base);
  color: var(--color-text);
  margin-bottom: 4px;
}

.post-author__bio {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  line-height: 1.5;
}

/* Share */
.post-share {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}

.share-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  transition: all var(--transition-fast);
  min-height: 44px;
}

.share-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.share-btn--telegram:hover {
  border-color: #2AABEE;
  color: #2AABEE;
}

.share-btn--vk:hover {
  border-color: #4C75A3;
  color: #4C75A3;
}

/* Back link */
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 500;
  transition: gap var(--transition-fast);
  margin-bottom: 3rem;
}

.back-link:hover {
  gap: 12px;
}

/* Related Posts */
.related-posts {
  padding-top: 2.5rem;
  border-top: 1px solid var(--color-border);
}

.related-posts__title {
  font-size: var(--text-2xl);
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: var(--color-text);
}

.related-posts__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 640px) {
  .related-posts__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
