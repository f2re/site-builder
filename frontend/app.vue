<script setup lang="ts">
import { onMounted } from 'vue'
import { useThemeStore } from '~/stores/themeStore'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.init()
})
</script>

<template>
  <div class="app-root">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<style>
/* Global styles using tokens */
body {
  background-color: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-sans);
  margin: 0;
  padding: 0;
  transition: background-color var(--transition-theme), color var(--transition-theme);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Base link styles */
a {
  color: var(--color-accent);
  text-decoration: none;
  transition: color var(--transition-fast);
}

a:hover {
  color: var(--color-accent-hover);
}
</style>
