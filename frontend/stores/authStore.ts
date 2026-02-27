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
        refreshTokenCookie.value = data.refresh_token
        return { success: true }
      }
      return { success: false, error: 'Invalid response' }
    } catch (err: any) {
      return { success: false, error: err.data?.message || 'Login failed' }
    }
  }

  function logout() {
    accessToken.value = null
    refreshTokenCookie.value = null
    navigateTo('/login')
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
    logout,
    refreshToken
  }
})
