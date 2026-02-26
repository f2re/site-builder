import { defineStore } from 'pinia'
import { computed, ref, onMounted } from 'vue'

export type Theme = 'dark' | 'light'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>('dark')

  const isDark = computed(() => theme.value === 'dark')

  const setTheme = (t: Theme) => {
    theme.value = t
    if (process.client) {
      document.documentElement.dataset.theme = t
      localStorage.setItem('theme', t)
      // cookie for SSR
      document.cookie = `theme=${t}; path=/; max-age=31536000; SameSite=Lax`
    }
  }

  const toggle = () => {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  const init = () => {
    if (process.client) {
      const saved = localStorage.getItem('theme') as Theme | null
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      
      const initialTheme = saved || (prefersDark ? 'dark' : 'light')
      setTheme(initialTheme)
    }
  }

  return {
    theme,
    isDark,
    toggle,
    setTheme,
    init
  }
})
