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
    console.log('[DEBUG] authStore: login started', email)
    try {
      const data = await $fetch<any>(`${apiBase}/auth/login`, {
        method: 'POST',
        body: { email, password }
      })
      console.log('[DEBUG] authStore: login response received', !!data.access_token)
      
      if (data.access_token) {
        accessToken.value = data.access_token
        if (data.refresh_token) {
           refreshTokenCookie.value = data.refresh_token
        }
        
        const userStore = useUserStore()
        console.log('[DEBUG] authStore: fetching profile...')
        await userStore.fetchProfile()
        console.log('[DEBUG] authStore: profile fetched', !!userStore.user)

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
        body: { full_name: name, email, password }
      })
      return { success: true }
    } catch (err: any) {
      return { success: false, error: err.data?.detail || err.data?.message || 'Registration failed' }
    }
  }

  async function handleOAuthCallback(provider: string, code: string, redirectUri: string) {
    try {
      const data = await $fetch<any>(`${apiBase}/auth/${provider}/callback`, {
        params: { code, redirect_uri: redirectUri }
      })
      
      if (data.access_token) {
        accessToken.value = data.access_token
        if (data.refresh_token) {
           refreshTokenCookie.value = data.refresh_token
        }
        
        const userStore = useUserStore()
        await userStore.fetchProfile()

        return { success: true }
      }
      return { success: false, error: 'Invalid response' }
    } catch (err: any) {
      return { success: false, error: err.data?.detail || err.data?.message || 'OAuth login failed' }
    }
  }

  async function handleTelegramAuth(tgData: any) {
    try {
      const data = await $fetch<any>(`${apiBase}/auth/telegram`, {
        method: 'POST',
        body: tgData
      })
      
      if (data.access_token) {
        accessToken.value = data.access_token
        if (data.refresh_token) {
           refreshTokenCookie.value = data.refresh_token
        }
        
        const userStore = useUserStore()
        await userStore.fetchProfile()

        return { success: true }
      }
      return { success: false, error: 'Invalid response' }
    } catch (err: any) {
      return { success: false, error: err.data?.detail || err.data?.message || 'Telegram auth failed' }
    }
  }

  async function forgotPassword(email: string) {
    try {
      await $fetch(`${apiBase}/auth/forgot-password`, {
        method: 'POST',
        body: { email }
      })
      return { success: true }
    } catch (err: any) {
      return { success: false, error: err.data?.detail || 'Failed to send reset email' }
    }
  }

  async function resetPassword(token: string, new_password: string) {
    try {
      await $fetch(`${apiBase}/auth/reset-password`, {
        method: 'POST',
        body: { token, new_password }
      })
      return { success: true }
    } catch (err: any) {
      return { success: false, error: err.data?.detail || 'Failed to reset password' }
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
    handleOAuthCallback,
    handleTelegramAuth,
    forgotPassword,
    resetPassword,
    logout,
    refreshToken
  }
})
