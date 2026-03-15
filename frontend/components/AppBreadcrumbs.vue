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
  <nav
    class="breadcrumbs"
    aria-label="Навигация"
    itemscope
    itemtype="https://schema.org/BreadcrumbList"
    data-testid="breadcrumbs-nav"
  >
    <ol class="breadcrumbs__list">
      <li
        v-for="(crumb, i) in crumbs"
        :key="i"
        class="breadcrumbs__item"
        itemprop="itemListElement"
        itemscope
        itemtype="https://schema.org/ListItem"
      >
        <!-- Separator (все кроме первого) -->
        <Icon
          v-if="i > 0"
          name="ph:caret-right-bold"
          class="breadcrumbs__sep"
          aria-hidden="true"
        />

        <!-- Ссылка (не последний элемент) -->
        <NuxtLink
          v-if="crumb.to"
          :to="crumb.to"
          class="breadcrumbs__link"
          itemprop="item"
          :data-testid="`breadcrumb-link-${i}`"
        >
          <Icon v-if="crumb.icon" :name="crumb.icon" class="breadcrumbs__icon" aria-hidden="true" />
          <span itemprop="name" class="breadcrumbs__text">{{ crumb.label }}</span>
        </NuxtLink>

        <!-- Текущая страница (последний элемент без to) -->
        <span
          v-else
          class="breadcrumbs__current"
          itemprop="name"
          data-testid="breadcrumb-current"
          :title="crumb.label"
        >
          <Icon v-if="crumb.icon" :name="crumb.icon" class="breadcrumbs__icon" aria-hidden="true" />
          <span class="breadcrumbs__text breadcrumbs__text--truncate">{{ crumb.label }}</span>
        </span>

        <meta itemprop="position" :content="String(i + 1)" />
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.breadcrumbs {
  padding: 10px 0;
  margin-bottom: 8px;
}

.breadcrumbs__list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 2px;
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: var(--text-sm);
}

.breadcrumbs__item {
  display: flex;
  align-items: center;
  gap: 2px;
  min-width: 0; /* важно для truncate */
}

.breadcrumbs__sep {
  color: var(--color-border-strong);
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.breadcrumbs__link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  color: var(--color-text-2);
  text-decoration: none;
  white-space: nowrap;
  transition: color var(--transition-fast), background var(--transition-fast);
}

.breadcrumbs__link:hover {
  color: var(--color-accent);
  background: var(--color-surface-2);
}

.breadcrumbs__link:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.breadcrumbs__current {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  color: var(--color-text);
  font-weight: 500;
  min-width: 0;
  max-width: 260px;
}

.breadcrumbs__text {
  line-height: 1.4;
}

.breadcrumbs__text--truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.breadcrumbs__icon {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

@media (max-width: 480px) {
  .breadcrumbs__current {
    max-width: 160px;
  }
}
</style>
