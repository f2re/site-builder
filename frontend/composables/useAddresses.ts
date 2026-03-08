export interface DeliveryAddress {
  id: string
  name: string
  recipient_name: string
  recipient_phone: string
  address_type: 'home' | 'pickup'
  full_address: string
  city: string
  postal_code: string | null
  provider: 'cdek' | 'pochta' | 'ozon' | 'wb'
  pickup_point_code: string | null
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface CreateAddressRequest {
  name: string
  recipient_name: string
  recipient_phone: string
  address_type: 'home' | 'pickup'
  full_address: string
  city: string
  postal_code?: string
  provider: 'cdek' | 'pochta' | 'ozon' | 'wb'
  pickup_point_code?: string
  is_default: boolean
}

export const useAddresses = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const getAddresses = () => {
    return useFetch<{ items: DeliveryAddress[] }>(`${apiBase}/users/me/addresses`, {
      key: 'user-addresses'
    })
  }

  const createAddress = async (body: CreateAddressRequest) => {
    return await $fetch<DeliveryAddress>(`${apiBase}/users/me/addresses`, {
      method: 'POST',
      body
    })
  }

  const updateAddress = async (id: string, body: Partial<CreateAddressRequest>) => {
    return await $fetch<DeliveryAddress>(`${apiBase}/users/me/addresses/${id}`, {
      method: 'PATCH',
      body
    })
  }

  const deleteAddress = async (id: string) => {
    return await $fetch(`${apiBase}/users/me/addresses/${id}`, {
      method: 'DELETE'
    })
  }

  const setDefaultAddress = async (id: string) => {
    return await $fetch<DeliveryAddress>(`${apiBase}/users/me/addresses/${id}/set-default`, {
      method: 'POST'
    })
  }

  return {
    getAddresses,
    createAddress,
    updateAddress,
    deleteAddress,
    setDefaultAddress
  }
}
