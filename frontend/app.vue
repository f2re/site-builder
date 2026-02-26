<script setup lang="ts">
import { onMounted } from 'vue'
import { useThemeStore } from '~/stores/themeStore'
import { useCartStore } from '~/stores/cartStore'

const themeStore = useThemeStore()
const cartStore  = useCartStore()

onMounted(() => {
  themeStore.init()
  cartStore.init()
})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<style>
/* Global base styles */
*, *::before, *::after {
  box-sizing: border-box;
}

body {
  background-color: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: 1.6;
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  color: inherit;
  text-decoration: none;
}
</style>
