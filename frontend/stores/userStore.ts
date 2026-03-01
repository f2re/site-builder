import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserProfile } from '../composables/useUser'

export const useUserStore = defineStore('user', () => {
  const user = ref<UserProfile | null>(null)
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  function setUser(u: UserProfile | null) {
    user.value = u
  }

  function clearUser() {
    user.value = null
  }

  async function fetchProfile() {
    const config = useRuntimeConfig()
    const authStore = useAuthStore()
    
    if (!authStore.accessToken) return null

    try {
      const data = await $fetch<UserProfile>(`${config.public.apiBase}/users/me`, {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`
        }
      })
      setUser(data)
      return data
    } catch (err) {
      clearUser()
      return null
    }
  }

  return {
    user,
    isAuthenticated,
    isAdmin,
    setUser,
    clearUser,
    fetchProfile
  }
})
