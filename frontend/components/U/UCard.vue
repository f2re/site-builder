<script setup lang="ts">
interface Props {
  tag?: string
  to?: string
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  tag: 'div',
  clickable: false,
})

const isNuxtLink = computed(() => !!props.to)
</script>

<template>
  <component
    :is="isNuxtLink ? 'NuxtLink' : tag"
    :to="to"
    class="card"
    :class="{ 'card--clickable': clickable || isNuxtLink }"
  >
    <slot />
  </component>
</template>

<style scoped>
.card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  transition:
    transform var(--transition-fast),
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    background-color var(--transition-theme);
  display: flex;
  flex-direction: column;
}

.card--clickable {
  cursor: pointer;
  text-decoration: none;
  color: inherit;
}

.card--clickable:hover {
  transform: translateY(-4px);
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}
</style>
