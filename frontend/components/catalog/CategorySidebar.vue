<script setup lang="ts">
import type { Category } from '~/composables/useProducts'

const props = defineProps<{
  categories: Category[]
  activeSlug?: string
}>()

const emit = defineEmits<{
  (e: 'select', slug: string | undefined): void
}>()

// Simple tree builder for flat categories
const categoryTree = computed(() => {
  const map = new Map<string | null, Category[]>()
  props.categories.forEach(cat => {
    const parentId = cat.parent_id
    if (!map.has(parentId)) map.set(parentId, [])
    map.get(parentId)!.push(cat)
  })
  return map
})

const rootCategories = computed(() => categoryTree.value.get(null) || [])
const getChildren = (parentId: string) => categoryTree.value.get(parentId) || []
</script>

<template>
  <aside class="category-sidebar">
    <div class="category-sidebar__header">
      <h2 class="category-sidebar__title">Категории</h2>
      <button
        v-if="activeSlug"
        class="category-sidebar__reset"
        @click="emit('select', undefined)"
      >
        Сбросить
      </button>
    </div>

    <nav class="category-sidebar__nav">
      <ul class="category-list">
        <li v-for="cat in rootCategories" :key="cat.id" class="category-item">
          <button
            class="category-link"
            :class="{ 'is-active': activeSlug === cat.slug }"
            @click="emit('select', cat.slug)"
          >
            <span class="category-link__name">{{ cat.name }}</span>
            <span class="category-link__count">{{ cat.product_count }}</span>
          </button>

          <!-- Subcategories -->
          <ul v-if="getChildren(cat.id).length > 0" class="category-list category-list--sub">
            <li v-for="sub in getChildren(cat.id)" :key="sub.id" class="category-item">
              <button
                class="category-link"
                :class="{ 'is-active': activeSlug === sub.slug }"
                @click="emit('select', sub.slug)"
              >
                <span class="category-link__name">{{ sub.name }}</span>
                <span class="category-link__count">{{ sub.product_count }}</span>
              </button>
            </li>
          </ul>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<style scoped>
.category-sidebar {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  position: sticky;
  top: 100px;
}

.category-sidebar__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.category-sidebar__title {
  font-size: var(--text-base);
  font-weight: 700;
  margin: 0;
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.category-sidebar__reset {
  background: none;
  border: none;
  color: var(--color-accent);
  font-size: var(--text-xs);
  font-weight: 600;
  cursor: pointer;
  padding: 4px;
}

.category-sidebar__reset:hover {
  text-decoration: underline;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.category-list--sub {
  margin-left: 16px;
  margin-top: 4px;
  margin-bottom: 8px;
  border-left: 1px solid var(--color-border);
  padding-left: 12px;
}

.category-link {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-text-2);
  font-size: var(--text-sm);
  transition:
    background var(--transition-fast),
    color var(--transition-fast);
  text-align: left;
}

.category-link:hover {
  background: var(--color-bg-subtle);
  color: var(--color-text);
}

.category-link.is-active {
  background: var(--color-accent-glow);
  color: var(--color-accent);
  font-weight: 600;
}

.category-link__count {
  font-size: var(--text-xs);
  opacity: 0.6;
}
</style>
