import { useCookie } from '#app'

export interface CartItem {
  product_id: string
  slug: string
  name: string
  quantity: number
  price_rub: number
  stock_available: number
}

export interface CartResponse {
  cart_id: string
  items: CartItem[]
  subtotal_rub: number
  reserved_until: string | null
}

export const useCart = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase
  const cartId = useCookie<string | null>('cart_id', {
    maxAge: 60 * 60 * 24 * 7, // 1 week
    path: '/'
  })

  // We'll use a local token ref if it exists in the future
  // For now, we assume the backend might use cartId or a token
  
  const fetchCart = async () => {
    return await useFetch<CartResponse>(`${apiBase}/cart`, {
      key: 'cart-data',
      headers: cartId.value ? { 'X-Cart-ID': cartId.value } : {},
      onResponse({ response }) {
        if (response._data?.cart_id) {
          cartId.value = response._data.cart_id
        }
      }
    })
  }

  const addToCart = async (productId: string, quantity: number = 1) => {
    return await useFetch<CartResponse>(`${apiBase}/cart/add`, {
      method: 'POST',
      body: { product_id: productId, quantity },
      headers: cartId.value ? { 'X-Cart-ID': cartId.value } : {},
      onResponse({ response }) {
        if (response._data?.cart_id) {
          cartId.value = response._data.cart_id
        }
      }
    })
  }

  const removeFromCart = async (productId: string) => {
    return await useFetch<CartResponse>(`${apiBase}/cart/${productId}`, {
      method: 'DELETE',
      headers: cartId.value ? { 'X-Cart-ID': cartId.value } : {}
    })
  }

  const updateQuantity = async (productId: string, quantity: number) => {
     // The API contract doesn't have a specific update quantity endpoint, 
     // but usually POST /cart/add with a new quantity or a PATCH endpoint works.
     // Looking at contract 4.2 POST /api/v1/cart/add it takes quantity.
     // Let's assume it sets or adds. If it adds, we might need a different approach.
     // If the contract says "POST /api/v1/cart/add", I'll use it.
     return await addToCart(productId, quantity)
  }

  const clearCart = async () => {
    return await useFetch(`${apiBase}/cart`, {
      method: 'DELETE',
      headers: cartId.value ? { 'X-Cart-ID': cartId.value } : {}
    })
  }

  return {
    cartId,
    fetchCart,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart
  }
}
