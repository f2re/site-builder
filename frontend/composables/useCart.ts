import { useAuth } from './useAuth'

export interface ApiCartItem {
  variant_id: string
  name: string
  price: number
  quantity: number
  subtotal: number
  image_url?: string
}

export interface CartResponse {
  items: ApiCartItem[]
  total_quantity: number
  total_price: number
}

export const useCart = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase
  const { useApi } = useAuth()
  
  const fetchCart = async () => {
    return await useApi(`${apiBase}/cart`, {
      key: 'cart-data'
    })
  }

  const addToCart = async (variantId: string, quantity: number = 1) => {
    return await useApi(`${apiBase}/cart/add`, {
      method: 'POST',
      body: { variant_id: variantId, quantity }
    })
  }

  const removeFromCart = async (variantId: string) => {
    return await useApi(`${apiBase}/cart/${variantId}`, {
      method: 'DELETE'
    })
  }

  return {
    fetchCart,
    addToCart,
    removeFromCart
  }
}
