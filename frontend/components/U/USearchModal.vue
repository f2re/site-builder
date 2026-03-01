<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits<{ close: [] }>()
const query = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

onMounted(() => {
  inputRef.value?.focus()
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') emit('close')
}

const handleSubmit = () => {
  if (!query.value.trim()) return
  // TODO: navigate to /products?q=...
  navigateTo({ path: '/products', query: { q: query.value.trim() } })
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div class="search-overlay" @click.self="emit('close')" role="dialog" aria-modal="true" aria-label="Поиск">
      <div class="search-modal">
        <form class="search-form" @submit.prevent="handleSubmit">
          <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20"
            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            ref="inputRef"
            v-model="query"
            type="search"
            class="search-input"
            placeholder="Поиск товаров, статей..."
            autocomplete="off"
          />
          <kbd class="search-esc" @click="emit('close')">Esc</kbd>
        </form>
        <p class="search-hint">Нажмите Enter для поиска или Esc для закрытия</p>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.search-overlay {
  position: fixed;
  inset: 0;
  background-color: var(--color-overlay);
  z-index: 11000;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 100px;
  backdrop-filter: blur(4px);
}

.search-modal {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 600px;
  box-shadow: var(--shadow-modal);
  overflow: hidden;
  margin: 0 20px;
}

.search-form {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
}

.search-icon {
  color: var(--color-muted);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: var(--text-lg);
  color: var(--color-text);
  font-family: var(--font-sans);
}

.search-input::placeholder { color: var(--color-muted); }

.search-esc {
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 2px 8px;
  font-size: var(--text-xs);
  color: var(--color-muted);
  cursor: pointer;
  white-space: nowrap;
  font-family: var(--font-mono);
  transition: border-color var(--transition-fast);
}
.search-esc:hover { border-color: var(--color-border-strong); }

.search-hint {
  padding: 12px 20px;
  font-size: var(--text-sm);
  color: var(--color-muted);
}
</style>
