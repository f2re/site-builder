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
const hasHeader = useSlots().header
const hasFooter = useSlots().footer
</script>

<template>
  <component
    :is="isNuxtLink ? 'NuxtLink' : tag"
    :to="to"
    class="card"
    :class="{ 'card--clickable': clickable || isNuxtLink }"
  >
    <div v-if="hasHeader" class="card__header">
      <slot name="header" />
    </div>
    
    <div class="card__body">
      <slot />
    </div>
    
    <div v-if="hasFooter" class="card__footer">
      <slot name="footer" />
    </div>
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

.card__header {
  padding: 24px 24px 16px;
  border-bottom: 1px solid var(--color-border);
}

.card__body {
  padding: 24px;
  flex: 1;
}

.card__footer {
  padding: 16px 24px 24px;
  border-top: 1px solid var(--color-border);
  background-color: var(--color-bg-subtle);
}

/* On mobile, reduce padding slightly */
@media (max-width: 480px) {
  .card__header { padding: 20px 20px 12px; }
  .card__body { padding: 20px; }
  .card__footer { padding: 12px 20px 20px; }
}
</style>
