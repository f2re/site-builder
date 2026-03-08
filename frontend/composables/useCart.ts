import { useAuth } from './useAuth'

export interface ApiCartItem {
  item_id: string
  product_id: string  // This is variant_id in backend but named product_id in schema
  slug: string
  name: string
  price_rub: number
  quantity: number
  stock_available: number
  selected_options: Array<{
    group_id: string
    group_name: string
    value_id: string
    value_name: string
    price_modifier: number
  }>
}

export interface CartResponse {
  cart_id: string
  items: ApiCartItem[]
  subtotal_rub: number
  reserved_until?: string | null
}

export const useCart = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase
  const { useApi } = useAuth()
  const apiFetch = useApiFetch()
  
  const fetchCart = async () => {
    return await apiFetch<CartResponse>(`${apiBase}/cart`)
  }

  const addToCart = async (variantId: string, quantity: number = 1, selectedOptionValueIds: string[] = []) => {
    return await apiFetch<CartResponse>(`${apiBase}/cart/add`, {
      method: 'POST',
      body: { product_id: variantId, quantity, selected_option_value_ids: selectedOptionValueIds }
    })
  }

  const updateQuantity = async (itemId: string, quantity: number) => {
    return await apiFetch<CartResponse>(`${apiBase}/cart/${itemId}`, {
      method: 'PATCH',
      body: { quantity }
    })
  }

  const removeFromCart = async (itemId: string) => {
    return await apiFetch<CartResponse>(`${apiBase}/cart/${itemId}`, {
      method: 'DELETE'
    })
  }

  const clearCart = async () => {
    return await apiFetch(`${apiBase}/cart`, {
      method: 'DELETE'
    })
  }

  return {
    fetchCart,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart
  }
}
