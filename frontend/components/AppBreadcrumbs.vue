<script setup lang="ts">
import { useBreadcrumbSchema } from '~/composables/useSchemaOrg'

interface Crumb {
  label: string
  to?: string
  icon?: string
}

const props = withDefaults(defineProps<{
  crumbs: Crumb[]
}>(), {
  crumbs: () => []
})

const config = useRuntimeConfig()
const siteUrl = config.public.siteUrl

// Inject Schema.org BreadcrumbList
useBreadcrumbSchema(
  props.crumbs.map(c => ({
    name: c.label,
    url: c.to ? `${siteUrl}${c.to}` : siteUrl,
  }))
)
</script>

<template>
  <nav class="breadcrumbs" aria-label="Хлебные крошки" itemscope itemtype="https://schema.org/BreadcrumbList">
    <ol class="breadcrumbs-list">
      <li
        v-for="(crumb, i) in crumbs"
        :key="i"
        class="breadcrumbs-item"
        itemprop="itemListElement"
        itemscope
        itemtype="https://schema.org/ListItem"
      >
        <NuxtLink
          v-if="crumb.to"
          :to="crumb.to"
          class="breadcrumbs-link"
          itemprop="item"
        >
          <Icon v-if="crumb.icon" :name="crumb.icon" class="breadcrumbs-icon" />
          <span itemprop="name">{{ crumb.label }}</span>
        </NuxtLink>
        <span v-else class="breadcrumbs-current" itemprop="name">
          <Icon v-if="crumb.icon" :name="crumb.icon" class="breadcrumbs-icon" />
          {{ crumb.label }}
        </span>
        <meta itemprop="position" :content="String(i + 1)" />
        <span v-if="i < crumbs.length - 1" class="breadcrumbs-separator" aria-hidden="true">/</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.breadcrumbs {
  margin-bottom: var(--space-4);
}

.breadcrumbs-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: var(--text-sm);
}

.breadcrumbs-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.breadcrumbs-link {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  color: var(--color-text-2);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.breadcrumbs-link:hover {
  color: var(--color-accent);
  text-decoration: underline;
}

.breadcrumbs-current {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  color: var(--color-text);
  font-weight: 500;
}

.breadcrumbs-icon {
  width: 16px;
  height: 16px;
}

.breadcrumbs-separator {
  color: var(--color-text-3);
  user-select: none;
}
</style>
