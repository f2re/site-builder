import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface StoreCartItem {
  id: number
  name: string
  price: number
  quantity: number
  image?: string
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<StoreCartItem[]>([])
  const selectedPvzCode = ref<string>('')
  const selectedCityCode = ref<string>('')

  const totalCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )

  const totalPrice = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  const addItem = (product: any) => {
    const existing = items.value.find(i => i.id === product.id)
    if (existing) {
      existing.quantity++
    } else {
      items.value.push({ ...product, quantity: 1 })
    }
    persist()
  }

  const removeItem = (id: number) => {
    items.value = items.value.filter(i => i.id !== id)
    persist()
  }

  const updateQuantity = (id: number, quantity: number) => {
    const item = items.value.find(i => i.id === id)
    if (item) {
      if (quantity <= 0) {
        removeItem(id)
      } else {
        item.quantity = quantity
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
