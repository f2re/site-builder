<script setup lang="ts">
import type { BlogPost } from '~/composables/useBlog'

const props = defineProps<{
  post: BlogPost
}>()

const formatDate = (dateString?: string | null) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '—'
  // Check if date is too old (e.g. 1970)
  if (date.getFullYear() <= 1970) return '—'
  
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const getTagName = (tag: any) => {
  if (typeof tag === 'string') return tag
  return tag.name || 'Тег'
}

const getTagKey = (tag: any, index: number) => {
  if (typeof tag === 'string') return tag + index
  return tag.id || tag.name || index
}
</script>

<template>
  <NuxtLink :to="`/blog/${post.slug}`" class="blog-card" data-testid="blog-post-card">
    <div class="blog-card__image-wrapper">
      <img
        :src="post.cover_url || '/placeholder-blog.png'"
        :alt="post.title"
        class="blog-card__image"
        loading="lazy"
      />
    </div>

    <div class="blog-card__content">
      <div class="blog-card__meta">
        <span class="blog-card__date">{{ formatDate(post.published_at) }}</span>
        <span class="blog-card__divider">·</span>
        <span class="blog-card__reading-time">{{ post.reading_time_minutes || 0 }} мин. чтения</span>
      </div>

      <h3 class="blog-card__title" data-testid="blog-post-title">{{ post.title }}</h3>
      <p class="blog-card__excerpt">{{ post.excerpt }}</p>

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

        <div class="blog-card__tags">
          <span v-for="(tag, index) in post.tags?.slice(0, 2)" :key="getTagKey(tag, index)" class="blog-card__tag">
            #{{ getTagName(tag) }}
          </span>
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

.blog-card__content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
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
  gap: 8px;
}

.blog-card__tag {
  font-size: var(--text-xs);
  color: var(--color-accent);
  font-weight: 600;
  background: var(--color-accent-glow);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}
</style>
