<script setup lang="ts">
import { useBreadcrumbSchema } from '~/composables/useSchemaOrg'

interface BreadcrumbItem {
  label: string
  to: string
}

const props = defineProps<{
  items: BreadcrumbItem[]
}>()

// Register JSON-LD schema
useBreadcrumbSchema(props.items.map(i => ({ name: i.label, item: i.to })))
</script>

<template>
  <nav class="breadcrumbs" aria-label="Breadcrumb">
    <ol class="breadcrumbs__list">
      <li class="breadcrumbs__item">
        <NuxtLink to="/" class="breadcrumbs__link">Главная</NuxtLink>
        <span class="breadcrumbs__separator" aria-hidden="true">/</span>
      </li>
      <li 
        v-for="(item, index) in items" 
        :key="item.to" 
        class="breadcrumbs__item"
      >
        <NuxtLink 
          v-if="index < items.length - 1" 
          :to="item.to" 
          class="breadcrumbs__link"
        >
          {{ item.label }}
        </NuxtLink>
        <span v-else class="breadcrumbs__current" aria-current="page">
          {{ item.label }}
        </span>
        <span v-if="index < items.length - 1" class="breadcrumbs__separator" aria-hidden="true">
          /
        </span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.breadcrumbs {
  margin-bottom: 24px;
}

.breadcrumbs__list {
  display: flex;
  flex-wrap: wrap;
  list-style: none;
  padding: 0;
  margin: 0;
  gap: 8px;
}

.breadcrumbs__item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.breadcrumbs__link {
  color: inherit;
  text-decoration: none;
  transition: color var(--transition-fast);
}

.breadcrumbs__link:hover {
  color: var(--color-accent);
}

.breadcrumbs__current {
  color: var(--color-text);
  font-weight: 500;
}

.breadcrumbs__separator {
  user-select: none;
  opacity: 0.5;
}
</style>
