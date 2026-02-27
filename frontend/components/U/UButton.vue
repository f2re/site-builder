<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'neon'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  to?: string
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false,
  type: 'button',
})

const isNuxtLink = computed(() => !!props.to)
</script>

<template>
  <component
    :is="isNuxtLink ? 'NuxtLink' : 'button'"
    :to="to"
    :type="isNuxtLink ? undefined : type"
    :disabled="disabled || loading"
    class="btn"
    :class="[
      `btn--${variant}`,
      `btn--${size}`,
      { 'btn--loading': loading }
    ]"
  >
    <div v-if="loading" class="btn__loader"></div>
    <div :class="['btn__content', { 'btn__content--hidden': loading }]">
      <slot name="icon" />
      <slot />
      <slot name="iconRight" />
    </div>
  </component>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: relative;
  font-family: var(--font-sans);
  font-weight: 600;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition:
    transform var(--transition-fast),
    background-color var(--transition-fast),
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    opacity var(--transition-fast);
  border: 1px solid transparent;
  text-decoration: none;
  white-space: nowrap;
  user-select: none;
  outline: none;
}

.btn:active:not(:disabled) {
  transform: scale(0.97);
}

.btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Variants */
.btn--primary {
  background-color: var(--color-accent);
  color: var(--color-on-accent);
}
.btn--primary:hover:not(:disabled) {
  background-color: var(--color-accent-hover);
  box-shadow: var(--shadow-glow-accent);
}

.btn--secondary {
  background-color: transparent;
  border-color: var(--color-accent);
  color: var(--color-accent);
}
.btn--secondary:hover:not(:disabled) {
  background-color: var(--color-accent-glow);
}

.btn--ghost {
  background-color: transparent;
  color: var(--color-text-2);
}
.btn--ghost:hover:not(:disabled) {
  background-color: var(--color-surface-2);
  color: var(--color-text);
}

.btn--danger {
  background-color: var(--color-error);
  color: var(--color-on-accent);
}
.btn--danger:hover:not(:disabled) {
  background-color: var(--color-accent-hover);
}

.btn--neon {
  background-color: var(--color-surface);
  border-color: var(--color-neon);
  color: var(--color-neon);
  box-shadow: var(--shadow-glow-neon);
}
.btn--neon:hover:not(:disabled) {
  background-color: var(--color-neon);
  color: var(--color-bg);
}

/* Sizes */
.btn--sm {
  padding: 6px 12px;
  font-size: var(--text-xs);
  height: 32px;
}
.btn--md {
  padding: 10px 20px;
  font-size: var(--text-sm);
  height: 44px;
}
.btn--lg {
  padding: 14px 28px;
  font-size: var(--text-base);
  height: 56px;
}

/* Loader */
.btn__loader {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.btn__content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn__content--hidden {
  opacity: 0;
}
</style>
