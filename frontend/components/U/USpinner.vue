<script setup lang="ts">
interface Props {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  color?: string // Optional override for var(--color-accent)
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const sizeClass = computed(() => `spinner--${props.size}`)
</script>

<template>
  <div class="spinner-container" :class="sizeClass">
    <svg 
      class="spinner-svg" 
      viewBox="0 0 50 50" 
      aria-hidden="true"
      :style="{ color: props.color }"
    >
      <circle 
        class="spinner-track" 
        cx="25" cy="25" r="20" 
        fill="none" 
        stroke-width="4"
      />
      <circle 
        class="spinner-head" 
        cx="25" cy="25" r="20" 
        fill="none" 
        stroke-width="4"
        stroke-linecap="round"
      />
    </svg>
    <span class="sr-only">Загрузка...</span>
  </div>
</template>

<style scoped>
.spinner-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.spinner-svg {
  animation: rotate 1.5s linear infinite;
  transform-origin: center;
}

.spinner-track {
  stroke: var(--color-border);
}

.spinner-head {
  stroke: var(--color-accent);
  stroke-dasharray: 90, 150;
  stroke-dashoffset: 0;
  animation: dash 1.5s ease-in-out infinite;
}

/* Racing-style glow */
.spinner-svg {
  filter: drop-shadow(0 0 4px var(--color-accent-glow));
}

.spinner--sm { width: 16px; height: 16px; }
.spinner--md { width: 32px; height: 32px; }
.spinner--lg { width: 48px; height: 48px; }
.spinner--xl { width: 64px; height: 64px; }

@keyframes rotate {
  100% { transform: rotate(360deg); }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
