<script setup lang="ts">
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

const props = defineProps<{
  comments: any[]
  pending?: boolean
}>()

const formatDate = (dateStr: string) => {
  try {
    return format(new Date(dateStr), 'd MMMM yyyy, HH:mm', { locale: ru })
  } catch (e) {
    return dateStr
  }
}
</script>

<template>
  <div class="comment-list">
    <h3 class="title">Комментарии ({{ comments.length }})</h3>

    <div v-if="pending" class="loading-state">
      <USkeleton v-for="i in 2" :key="i" height="120px" class="comment-skeleton" />
    </div>

    <div v-else-if="comments.length === 0" class="empty-state">
      Будьте первым, кто оставит комментарий!
    </div>

    <div v-else class="comments">
      <div v-for="comment in comments" :key="comment.id" class="comment-card">
        <div class="comment-header">
          <div class="author-info">
            <div class="avatar">
              {{ comment.author_name.charAt(0).toUpperCase() }}
            </div>
            <div class="meta">
              <span class="author-name">{{ comment.author_name }}</span>
              <span class="date">{{ formatDate(comment.created_at) }}</span>
            </div>
          </div>
        </div>
        <div class="comment-body">
          {{ comment.content }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
}

.loading-state, .comments {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.comment-skeleton {
  border-radius: var(--radius-lg);
}

.empty-state {
  color: var(--color-text-2);
  font-style: italic;
  padding: 2rem;
  text-align: center;
  background: var(--color-bg-subtle);
  border-radius: var(--radius-lg);
  border: 1px dashed var(--color-border);
}

.comment-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 1.5rem;
  border-radius: var(--radius-lg);
  transition: border-color var(--transition-fast);
}

.comment-card:hover {
  border-color: var(--color-border-strong);
}

.comment-header {
  margin-bottom: 1rem;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--color-accent);
}

.meta {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: var(--color-text);
  font-size: var(--text-sm);
}

.date {
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.comment-body {
  color: var(--color-text-2);
  font-size: var(--text-sm);
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>
