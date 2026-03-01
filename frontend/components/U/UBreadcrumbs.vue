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
const siteUrl = (config.public.siteUrl as string) || ''

// Inject Schema.org BreadcrumbList
useBreadcrumbSchema(
  props.crumbs.map((c, i) => ({
    name: c.label,
    url: c.to ? `${siteUrl}${c.to}` : (i === props.crumbs.length - 1 ? `${siteUrl}${useRoute().path}` : siteUrl),
  }))
)
</script>

<template>
  <nav class="u-breadcrumbs" aria-label="Хлебные крошки">
    <ol class="u-breadcrumbs-list">
      <li 
        v-for="(crumb, i) in crumbs" 
        :key="i"
        class="u-breadcrumbs-item"
      >
        <NuxtLink
          v-if="crumb.to"
          :to="crumb.to"
          class="u-breadcrumbs-link"
        >
          <Icon v-if="crumb.icon" :name="crumb.icon" class="u-breadcrumbs-icon" />
          <span class="u-breadcrumbs-text">{{ crumb.label }}</span>
        </NuxtLink>
        <span v-else class="u-breadcrumbs-current">
          <Icon v-if="crumb.icon" :name="crumb.icon" class="u-breadcrumbs-icon" />
          <span class="u-breadcrumbs-text">{{ crumb.label }}</span>
        </span>
        
        <span v-if="i < crumbs.length - 1" class="u-breadcrumbs-separator" aria-hidden="true">
          <Icon name="ph:caret-right-bold" size="12" />
        </span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.u-breadcrumbs {
  margin-block: 1rem;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.u-breadcrumbs::-webkit-scrollbar { display: none; }

.u-breadcrumbs-list {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  list-style: none;
  padding: 0;
  margin: 0;
  white-space: nowrap;
}

.u-breadcrumbs-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.u-breadcrumbs-link {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--color-text-2);
  font-size: var(--text-sm);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.u-breadcrumbs-link:hover {
  color: var(--color-accent);
}

.u-breadcrumbs-current {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--color-text);
  font-size: var(--text-sm);
  font-weight: 500;
}

.u-breadcrumbs-icon {
  flex-shrink: 0;
  opacity: 0.8;
}

.u-breadcrumbs-separator {
  display: flex;
  align-items: center;
  color: var(--color-muted);
  user-select: none;
}
</style>
