import { ref, unref, isRef } from 'vue'
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
  created_at?: string
}

export interface UserProfileUpdate {
  full_name?: string | null
  phone?: string | null
  address?: string | null
}

export interface UserCreate {
  email: string
  full_name?: string
  password?: string
  role: string
}

export const useUser = () => {
  const config = useRuntimeConfig()
  const { accessToken } = useAuth()
  const apiFetch = useApiFetch()
  
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

  // Admin methods
  const adminGetUsers = (params: any) => {
    return useApi<{ items: UserProfile[], total: number }>('/admin/users', {
      params,
      // Use unref to ensure we don't stringify reactive proxies which can be cyclic
      key: `admin-users-${JSON.stringify(isRef(params) ? unref(params) : params)}`
    })
  }

  const adminCreateUser = async (data: UserCreate) => {
    return await apiFetch<UserProfile>('/admin/users', {
      method: 'POST',
      body: data
    })
  }

  const adminSetUserBlockStatus = async (userId: string, isActive: boolean) => {
    return await apiFetch<UserProfile>(`/admin/users/${userId}/block`, {
      method: 'PUT',
      body: { is_active: isActive }
    })
  }

  const adminExportUsers = async () => {
    const response = await $fetch(`${config.public.apiBase}/admin/users/export`, {
      headers: {
        Authorization: `Bearer ${accessToken.value}`
      },
      responseType: 'blob'
    })
    return response as Blob
  }

  return {
    user,
    pending,
    error,
    fetchProfile,
    updateProfile,
    adminGetUsers,
    adminCreateUser,
    adminSetUserBlockStatus,
    adminExportUsers
  }
}
