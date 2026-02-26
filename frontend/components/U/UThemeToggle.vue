<script setup lang="ts">
import { useThemeStore } from '~/stores/themeStore'

const themeStore = useThemeStore()

const toggleTheme = () => {
  themeStore.toggle()
}
</script>

<template>
  <button
    class="theme-toggle"
    @click="toggleTheme"
    :aria-label="themeStore.isDark ? 'Переключить на светлую тему' : 'Переключить на темную тему'"
  >
    <!-- Sun icon for Dark Mode -->
    <svg v-if="themeStore.isDark" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="5"></circle>
      <line x1="12" y1="1" x2="12" y2="3"></line>
      <line x1="12" y1="21" x2="12" y2="23"></line>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
      <line x1="1" y1="12" x2="3" y2="12"></line>
      <line x1="21" y1="12" x2="23" y2="12"></line>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
    </svg>
    <!-- Moon icon for Light Mode -->
    <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
    </svg>
  </button>
</template>

<style scoped>
.theme-toggle {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 8px;
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-normal);
  width: 40px;
  height: 40px;
}

.theme-toggle:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: var(--color-surface-2);
  box-shadow: var(--shadow-glow-accent);
}

.theme-toggle:active {
  transform: scale(0.95);
}
</style>
