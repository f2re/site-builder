import { useAuth } from './useAuth'

export interface OrderItemOption {
  group_id: string
  group_name: string
  value_id: string
  value_name: string
  price_modifier: number
}

export interface OrderItem {
  product_id: string
  slug: string
  name: string
  quantity: number
  price_rub: number
  selected_options?: OrderItemOption[]
}

export interface DeliveryInfo {
  type: 'cdek_pvz' | 'cdek_door'
  pvz_code?: string
  address?: string
}

export interface Order {
  id: string
  status: string
  total_rub: number
  items: OrderItem[]
  delivery: DeliveryInfo
  created_at: string
  payment_url?: string
}

export interface CreateOrderRequest {
  delivery_type: 'cdek_pvz' | 'cdek_door'
  pvz_code?: string
  address?: string
  payment_method: 'yoomoney'
}

export interface CreateOrderResponse {
  order_id: string
  payment_url: string
  expires_at: string
}

export interface DeliveryCalculateRequest {
  city_code: string
  tariff_code?: string
  weight_kg: number
  dimensions: { l: number; w: number; h: number }
}

export interface DeliveryCalculateResponse {
  cost_rub: number
  days_min: number
  days_max: number
  tariff_code: string
  tariff_name: string
}

export interface PVZ {
  code: string
  address: string
  name: string
  lat: number
  lon: number
  work_hours: string
}

export interface City {
  code: string
  city: string
  region?: string
  country?: string
}

export const useOrders = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase
  const { accessToken } = useAuth()

  const getHeaders = () => ({
    ...(accessToken.value ? { Authorization: `Bearer ${accessToken.value}` } : {})
  })

  const createOrder = (body: CreateOrderRequest) => {
    return useFetch<CreateOrderResponse>(`${apiBase}/orders`, {
      method: 'POST',
      body,
      headers: getHeaders()
    })
  }

  const getOrders = (params?: { page_cursor?: string, per_page?: number }) => {
    return useFetch<{ items: Order[], next_cursor: string | null, total: number }>(`${apiBase}/orders`, {
      params,
      headers: getHeaders(),
      key: `orders-${JSON.stringify(params)}`
    })
  }

  const getOrder = (orderId: string) => {
    return useFetch<Order>(`${apiBase}/orders/${orderId}`, {
      headers: getHeaders(),
      key: `order-${orderId}`
    })
  }

  const cancelOrder = (orderId: string) => {
    return useFetch<Order>(`${apiBase}/orders/${orderId}/cancel`, {
      method: 'POST',
      headers: getHeaders()
    })
  }

  const getPaymentLink = (orderId: string) => {
    return useFetch<{ payment_url: string }>(`${apiBase}/orders/${orderId}/payment-link`, {
      headers: getHeaders()
    })
  }

  const calculateDelivery = (params: DeliveryCalculateRequest) => {
    return useFetch<DeliveryCalculateResponse>(`${apiBase}/delivery/calculate`, {
      method: 'POST',
      body: {
        city_code: params.city_code,
        weight_kg: params.weight_kg,
        dimensions: params.dimensions
      },
      headers: getHeaders()
    })
  }

  const getPVZs = (cityCode: string) => {
    return useFetch<{ items: PVZ[] }>(`${apiBase}/delivery/pvz`, {
      params: { city_code: cityCode },
      headers: getHeaders(),
      key: `pvz-${cityCode}`
    })
  }

  const searchCities = (query: string) => {
    return useFetch<City[]>(`${apiBase}/delivery/cities`, {
      params: { query },
      headers: getHeaders(),
      key: `cities-${query}`
    })
  }

  return {
    createOrder,
    getOrders,
    getOrder,
    cancelOrder,
    getPaymentLink,
    calculateDelivery,
    getPVZs,
    searchCities
  }
}
