<script setup lang="ts">
interface Props {
  variant?: 'success' | 'warning' | 'error' | 'info' | 'accent' | 'neon'
  size?: 'sm' | 'md'
}

withDefaults(defineProps<Props>(), {
  variant: 'accent',
  size: 'md'
})
</script>

<template>
  <span class="badge" :class="[`badge--${variant}`, `badge--${size}`]">
    <slot />
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-sans);
  font-weight: 600;
  border-radius: var(--radius-full);
  white-space: nowrap;
}

/* Sizes */
.badge--sm {
  padding: 2px 8px;
  font-size: var(--text-xs);
}
.badge--md {
  padding: 4px 12px;
  font-size: var(--text-sm);
}

/* Variants */
.badge--accent {
  background-color: var(--color-accent-glow);
  color: var(--color-accent);
  border: 1px solid var(--color-accent);
}
.badge--neon {
  background-color: var(--color-neon-glow);
  color: var(--color-neon);
  border: 1px solid var(--color-neon);
}
.badge--success {
  background-color: var(--color-success-bg);
  color: var(--color-success);
  border: 1px solid var(--color-success);
}
.badge--warning {
  background-color: var(--color-warning-bg);
  color: var(--color-warning);
  border: 1px solid var(--color-warning);
}
.badge--error {
  background-color: var(--color-error-bg);
  color: var(--color-error);
  border: 1px solid var(--color-error);
}
.badge--info {
  background-color: var(--color-info-bg);
  color: var(--color-info);
  border: 1px solid var(--color-info);
}
</style>
