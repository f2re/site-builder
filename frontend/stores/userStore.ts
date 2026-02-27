import { defineStore } from 'pinia'
import type { UserProfile } from '../composables/useUser'

export const useUserStore = defineStore('user', () => {
  const user = ref<UserProfile | null>(null)
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.role === 'manager')

  function setUser(u: UserProfile | null) {
    user.value = u
  }

  function clearUser() {
    user.value = null
  }

  return {
    user,
    isAuthenticated,
    isAdmin,
    setUser,
    clearUser
  }
})
