import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const accessToken = useCookie<string | null>('access_token', {
    maxAge: 60 * 30, // 30 minutes
    path: '/'
  })
  
  const refreshTokenCookie = useCookie<string | null>('refresh_token', {
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: '/'
  })

  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(email: string, password: string) {
    try {
      const data = await $fetch<any>(`${apiBase}/auth/login`, {
        method: 'POST',
        body: { email, password }
      })
      
      if (data.access_token) {
        accessToken.value = data.access_token
        // Note: according to api_contracts.md, refresh_token is set as httpOnly cookie by backend.
        // But if it's returned in JSON, we can save it to cookie if needed (though it says httpOnly).
        // Let's stick with what's in the store already.
        if (data.refresh_token) {
           refreshTokenCookie.value = data.refresh_token
        }
        return { success: true }
      }
      return { success: false, error: 'Invalid response' }
    } catch (err: any) {
      return { success: false, error: err.data?.detail || err.data?.message || 'Login failed' }
    }
  }

  async function register(name: string, email: string, password: string) {
    try {
      await $fetch<any>(`${apiBase}/auth/register`, {
        method: 'POST',
        body: { name, email, password }
      })
      return { success: true }
    } catch (err: any) {
      return { success: false, error: err.data?.detail || err.data?.message || 'Registration failed' }
    }
  }

  function logout() {
    accessToken.value = null
    refreshTokenCookie.value = null
    const userStore = useUserStore()
    userStore.clearUser()
    navigateTo('/auth/login')
  }

  async function refreshToken() {
    if (!refreshTokenCookie.value) {
      logout()
      return null
    }

    try {
      const data = await $fetch<any>(`${apiBase}/auth/refresh`, {
        method: 'POST',
        body: { refresh_token: refreshTokenCookie.value }
      })

      if (data.access_token) {
        accessToken.value = data.access_token
        if (data.refresh_token) {
          refreshTokenCookie.value = data.refresh_token
        }
        return data.access_token
      }
      return null
    } catch (err) {
      logout()
      return null
    }
  }

  return {
    accessToken,
    refreshTokenCookie,
    isAuthenticated,
    login,
    register,
    logout,
    refreshToken
  }
})
