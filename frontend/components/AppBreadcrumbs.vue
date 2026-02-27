<script setup lang="ts">
interface BreadcrumbItem {
  name: string
  path: string
}

const props = defineProps<{
  items: BreadcrumbItem[]
}>()

const siteUrl = useRuntimeConfig().public.siteUrl

// Automatically generate Schema.org BreadcrumbList
const breadcrumbItems = props.items.map((item, index) => ({
  name: item.name,
  item: item.path === '/' ? siteUrl : `${siteUrl}${item.path}`
}))

useBreadcrumbSchema(breadcrumbItems)
</script>

<template>
  <nav class="breadcrumbs" aria-label="Breadcrumb">
    <ol class="breadcrumbs__list">
      <li class="breadcrumbs__item">
        <NuxtLink to="/" class="breadcrumbs__link">Главная</NuxtLink>
        <Icon name="ph:caret-right-bold" size="12" class="breadcrumbs__separator" />
      </li>
      <li 
        v-for="(item, index) in items" 
        :key="index"
        class="breadcrumbs__item"
      >
        <template v-if="index === items.length - 1">
          <span class="breadcrumbs__current" aria-current="page">{{ item.name }}</span>
        </template>
        <template v-else>
          <NuxtLink :to="item.path" class="breadcrumbs__link">{{ item.name }}</NuxtLink>
          <Icon name="ph:caret-right-bold" size="12" class="breadcrumbs__separator" />
        </template>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.breadcrumbs {
  margin-bottom: 1.5rem;
}
.breadcrumbs__list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  list-style: none;
  padding: 0;
  margin: 0;
}
.breadcrumbs__item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--text-xs);
}
.breadcrumbs__link {
  color: var(--color-text-2);
  text-decoration: none;
  transition: color var(--transition-fast);
}
.breadcrumbs__link:hover {
  color: var(--color-accent);
}
.breadcrumbs__separator {
  color: var(--color-muted);
}
.breadcrumbs__current {
  color: var(--color-text);
  font-weight: 500;
}
</style>
