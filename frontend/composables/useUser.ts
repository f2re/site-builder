import { ref, unref, isRef } from 'vue'
import { useRuntimeConfig } from '#app'
import { useAuth } from './useAuth'
import type { Order } from './useOrders'

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

export interface UserAdminUpdate {
  full_name: string
  email: string
  phone: string
  role: string
  is_active: boolean
}

export interface UserAddress {
  id: string
  city?: string
  street?: string
  house?: string
  apartment?: string
  postal_code?: string
  country?: string
  full_address?: string
  is_default?: boolean
}

export interface AdminDeliveryAddressRead {
  id: string
  city: string
  address: string
  is_default: boolean
  created_at: string
}

export interface AdminUserDeviceRead {
  id: string
  device_id: string
  name: string | null
  last_activity: string | null
  is_online: boolean
}

export interface AdminDeviceRead {
  id: string
  user_id: string | null
  device_uid: string
  name: string | null
  model: string | null
  firmware_version: string | null
  is_active: boolean
  last_seen_at: string | null
  registered_at: string | null
  comment: string | null
  oc_device_id: number | null
}

export interface AdminUserFullResponse {
  id: string
  email: string
  full_name: string | null
  phone: string | null
  role: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  last_login_at: string | null
  last_login_ip: string | null
  last_login_device: string | null
  addresses: AdminDeliveryAddressRead[]
  orders: Order[]
  devices: AdminUserDeviceRead[]
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

  const adminUpdateUser = async (userId: string, data: Partial<UserAdminUpdate>) => {
    return await apiFetch<UserProfile>(`/admin/users/${userId}`, {
      method: 'PATCH',
      body: data
    })
  }

  const adminGetUserAddresses = (userId: string) => {
    return useApi<UserAddress[]>(`/admin/users/${userId}/addresses`, {
      key: `admin-user-addresses-${userId}`
    })
  }

  const adminDeleteUserAddress = async (userId: string, addrId: string) => {
    return await apiFetch(`/admin/users/${userId}/addresses/${addrId}`, {
      method: 'DELETE'
    })
  }

  const adminUpdateUserAddress = async (userId: string, addrId: string, data: Partial<UserAddress>) => {
    return await apiFetch<UserAddress>(`/admin/users/${userId}/addresses/${addrId}`, {
      method: 'PUT',
      body: data
    })
  }

  const adminGetUserFull = (userId: string) => {
    return useApi<AdminUserFullResponse>(`/admin/users/${userId}/full`, {
      key: `admin-user-full-${userId}`
    })
  }

  const adminGetUserDevices = (userId: string) => {
    return useApi<AdminDeviceRead[]>(`/admin/users/${userId}/devices`, {
      key: `admin-user-devices-${userId}`
    })
  }

  const adminGetDevices = (params: any) => {
    return useApi<{ items: AdminDeviceRead[], total: number }>('/admin/devices', {
      params,
      key: `admin-devices-${JSON.stringify(isRef(params) ? unref(params) : params)}`
    })
  }

  const adminPatchDevice = async (deviceId: string, data: Partial<Pick<AdminDeviceRead, 'name' | 'model' | 'is_active' | 'comment'>>) => {
    return await apiFetch<AdminDeviceRead>(`/admin/devices/${deviceId}`, {
      method: 'PATCH',
      body: data
    })
  }

  const adminDeleteDevice = async (deviceId: string) => {
    return await apiFetch(`/admin/devices/${deviceId}`, {
      method: 'DELETE'
    })
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
    adminExportUsers,
    adminUpdateUser,
    adminGetUserAddresses,
    adminDeleteUserAddress,
    adminUpdateUserAddress,
    adminGetUserFull,
    adminGetUserDevices,
    adminGetDevices,
    adminPatchDevice,
    adminDeleteDevice
  }
}
