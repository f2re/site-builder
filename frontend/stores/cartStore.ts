import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface StoreCartItem {
  id: string  // now composite id (variant_id + options)
  variantId: string
  name: string
  price: number
  quantity: number
  image?: string
  maxStock?: number
  selectedOptions?: Array<{
    group_id: string
    group_name: string
    value_id: string
    value_name: string
    price_modifier: number
  }>
  selectedOptionValueIds?: string[]
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<StoreCartItem[]>([])
  const selectedPvzCode = ref<string>('')
  const selectedCityCode = ref<string>('')

  const totalCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )

  const totalPrice = computed(() =>
    items.value.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0)
  )

  const addItem = (product: Omit<StoreCartItem, 'quantity'>): boolean => {
    // Ensure price is a number
    const price = typeof product.price === 'string' ? parseFloat(product.price) : product.price
    const productWithNumPrice = { ...product, price }

    const existing = items.value.find(i => i.id === product.id)
    if (existing) {
      if (existing.quantity >= (existing.maxStock ?? Infinity)) {
        return false
      }
      existing.quantity++
    } else {
      items.value.push({ ...productWithNumPrice, quantity: 1 })
    }
    persist()
    return true
  }

  const removeItem = (id: string) => {
    items.value = items.value.filter(i => i.id !== id)
    persist()
  }

  const updateQuantity = (id: string, quantity: number) => {
    const item = items.value.find(i => i.id === id)
    if (item) {
      if (quantity <= 0) {
        removeItem(id)
      } else {
        item.quantity = Math.min(quantity, item.maxStock ?? quantity)
        persist()
      }
    }
  }

  const setPvzCode = (code: string) => {
    selectedPvzCode.value = code
    persist()
  }

  const setCityCode = (code: string) => {
    selectedCityCode.value = code
    persist()
  }

  const clearCart = () => {
    items.value = []
    selectedPvzCode.value = ''
    persist()
  }

  const persist = () => {
    if (process.client) {
      localStorage.setItem('cart', JSON.stringify({
        items: items.value,
        selectedPvzCode: selectedPvzCode.value,
        selectedCityCode: selectedCityCode.value
      }))
    }
  }

  const init = () => {
    if (process.client) {
      const saved = localStorage.getItem('cart')
      if (saved) {
        try {
          const data = JSON.parse(saved)
          if (Array.isArray(data)) {
            // Backward compatibility
            items.value = data
          } else {
            items.value = data.items || []
            selectedPvzCode.value = data.selectedPvzCode || ''
            selectedCityCode.value = data.selectedCityCode || ''
          }
        } catch {
          items.value = []
        }
      }
    }
  }

  return {
    items,
    selectedPvzCode,
    selectedCityCode,
    totalCount,
    totalPrice,
    addItem,
    removeItem,
    updateQuantity,
    setPvzCode,
    setCityCode,
    clearCart,
    init,
  }
})
