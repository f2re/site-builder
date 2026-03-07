<script setup lang="ts">
import type { BlogPost } from '~/composables/useBlog'

const props = defineProps<{
  post: BlogPost
}>()

const formatDate = (dateString?: string | null) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '—'
  if (date.getFullYear() <= 1970) return '—'
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const getTagName = (tag: string | { id: string; name: string; slug: string }) => {
  if (typeof tag === 'string') return tag
  return tag.name || 'Тег'
}

const getTagSlug = (tag: string | { id: string; name: string; slug: string }) => {
  if (typeof tag === 'string') return tag
  return tag.slug || tag.name || ''
}

const getTagKey = (tag: string | { id: string; name: string; slug: string }, index: number) => {
  if (typeof tag === 'string') return tag + index
  return tag.id || tag.name || index
}

const coverImage = computed(() => {
  if (props.post.carousel_images?.length) return props.post.carousel_images[0]
  return props.post.cover_url || props.post.cover_image || '/placeholder-blog.png'
})

const hasCarousel = computed(() =>
  (props.post.carousel_images?.length ?? 0) > 1
)

const readingTime = computed(() =>
  props.post.reading_time_minutes ?? props.post.reading_time ?? 0
)
</script>

<template>
  <NuxtLink :to="`/blog/${post.slug}`" class="blog-card" data-testid="blog-post-card">
    <!-- Image / Carousel -->
    <div class="blog-card__image-wrapper">
      <BlogCarousel
        v-if="hasCarousel"
        :images="post.carousel_images!"
        :alt="post.title"
        :autoplay="false"
        aspect-ratio="16/9"
        class="blog-card__carousel"
      />
      <NuxtImg
        v-else
        :src="coverImage"
        :alt="post.title"
        class="blog-card__image"
        loading="lazy"
        width="400"
        height="225"
        fit="cover"
      />
      <!-- Hover read overlay -->
      <div class="blog-card__hover-overlay" aria-hidden="true">
        <Icon name="ph:book-open-bold" size="24" />
        <span>Читать</span>
      </div>
    </div>

    <div class="blog-card__content">
      <!-- Category -->
      <NuxtLink
        v-if="post.category"
        :to="`/blog?category=${post.category.slug}`"
        class="blog-card__category"
        @click.prevent.stop="$router.push(`/blog?category=${post.category!.slug}`)"
      >
        {{ post.category.name }}
      </NuxtLink>

      <div class="blog-card__meta">
        <span class="blog-card__date">{{ formatDate(post.published_at) }}</span>
        <span class="blog-card__divider">·</span>
        <span class="blog-card__reading-time">{{ readingTime }} мин. чтения</span>
      </div>

      <h3 class="blog-card__title" data-testid="blog-post-title">{{ post.title }}</h3>
      <p class="blog-card__excerpt">{{ post.summary || post.excerpt }}</p>

      <div class="blog-card__footer">
        <div class="blog-card__author">
          <img
            v-if="post.author?.avatar_url"
            :src="post.author.avatar_url"
            :alt="post.author?.name || 'Аноним'"
            class="blog-card__author-avatar"
          />
          <div v-else class="blog-card__author-avatar-placeholder">
            {{ post.author?.name?.charAt(0) || '?' }}
          </div>
          <span class="blog-card__author-name">{{ post.author?.name || 'Аноним' }}</span>
        </div>

        <div class="blog-card__tags" data-testid="blog-post-tags">
          <NuxtLink
            v-for="(tag, index) in post.tags?.slice(0, 2)"
            :key="getTagKey(tag, index)"
            :to="`/blog?tag=${getTagSlug(tag)}`"
            class="blog-card__tag"
            @click.prevent.stop="$router.push(`/blog?tag=${getTagSlug(tag)}`)"
          >
            #{{ getTagName(tag) }}
          </NuxtLink>
        </div>
      </div>
    </div>
  </NuxtLink>
</template>

<style scoped>
.blog-card {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition:
    transform var(--transition-fast),
    border-color var(--transition-fast),
    box-shadow var(--transition-fast);
  text-decoration: none;
  color: inherit;
  height: 100%;
}

.blog-card:hover {
  transform: translateY(-4px);
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.blog-card__image-wrapper {
  aspect-ratio: 16 / 9;
  background: var(--color-bg-subtle);
  overflow: hidden;
  position: relative;
}

.blog-card__carousel {
  width: 100%;
  height: 100%;
}

.blog-card__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.blog-card:hover .blog-card__image {
  transform: scale(1.05);
}

/* Hover overlay */
.blog-card__hover-overlay {
  position: absolute;
  bottom: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--color-accent);
  color: var(--color-on-accent);
  padding: 6px 12px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  opacity: 0;
  transform: translateY(4px);
  transition: opacity var(--transition-fast), transform var(--transition-fast);
  pointer-events: none;
}

.blog-card:hover .blog-card__hover-overlay {
  opacity: 1;
  transform: translateY(0);
}

.blog-card__content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.blog-card__category {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: 700;
  color: var(--color-accent);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  text-decoration: none;
  margin-bottom: 8px;
}

.blog-card__category:hover {
  text-decoration: underline;
}

.blog-card__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-xs);
  color: var(--color-muted);
  margin-bottom: 12px;
}

.blog-card__divider {
  opacity: 0.5;
}

.blog-card__title {
  font-size: var(--text-lg);
  font-weight: 700;
  line-height: 1.3;
  margin: 0 0 12px;
  color: var(--color-text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.blog-card__excerpt {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  line-height: 1.6;
  margin: 0 0 20px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.blog-card__footer {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.blog-card__author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.blog-card__author-avatar,
.blog-card__author-avatar-placeholder {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.blog-card__author-avatar-placeholder {
  background: var(--color-accent);
  color: var(--color-on-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
}

.blog-card__author-name {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text);
}

.blog-card__tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.blog-card__tag {
  font-size: var(--text-xs);
  color: var(--color-accent);
  font-weight: 600;
  background: var(--color-accent-glow);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  text-decoration: none;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.blog-card__tag:hover {
  background: var(--color-accent);
  color: var(--color-on-accent);
}
</style>
