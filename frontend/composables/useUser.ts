import { ref } from 'vue'
import { useRuntimeConfig } from '#app'
import { useAuth } from './useAuth'

export interface UserProfile {
  id: string
  email: string
  full_name: string | null
  phone: string | null
  address: string | null
  role: string
  is_active: boolean
}

export interface UserProfileUpdate {
  full_name?: string | null
  phone?: string | null
  address?: string | null
}

export const useUser = () => {
  const config = useRuntimeConfig()
  const { accessToken } = useAuth()
  
  const user = ref<UserProfile | null>(null)
  const pending = ref(false)
  const error = ref<any>(null)

  const fetchProfile = async () => {
    pending.value = true
    error.value = null
    try {
      const response = await $fetch<UserProfile>(`${config.public.apiBase}/users/me`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`
        }
      })
      user.value = response
      return response
    } catch (err: any) {
      error.value = err
      throw err
    } finally {
      pending.value = false
    }
  }

  const updateProfile = async (data: UserProfileUpdate) => {
    pending.value = true
    error.value = null
    try {
      const response = await $fetch<UserProfile>(`${config.public.apiBase}/users/me`, {
        method: 'PUT',
        body: data,
        headers: {
          Authorization: `Bearer ${accessToken.value}`
        }
      })
      user.value = response
      return response
    } catch (err: any) {
      error.value = err
      throw err
    } finally {
      pending.value = false
    }
  }

  return {
    user,
    pending,
    error,
    fetchProfile,
    updateProfile
  }
}
