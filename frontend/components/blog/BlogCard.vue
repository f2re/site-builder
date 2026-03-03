<script setup lang="ts">
import type { BlogPost } from '~/composables/useBlog'

defineProps<{
  post: BlogPost
}>()

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}
</script>

<template>
  <NuxtLink :to="`/blog/${post.slug}`" class="blog-card">
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
        <span class="blog-card__reading-time">{{ post.reading_time_min }} мин. чтения</span>
      </div>

      <h3 class="blog-card__title">{{ post.title }}</h3>
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
          <span v-for="tag in post.tags?.slice(0, 2)" :key="tag" class="blog-card__tag">
            #{{ tag }}
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
  padding: 20px;
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
  font-weight: 500;
}
</style>
