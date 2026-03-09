import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ProductOptionGroup, ProductOptionValue } from '~/composables/useProducts'
import { useProducts } from '~/composables/useProducts'

export interface CreateGroupData {
  name: string
  is_required: boolean
  sort_order: number
}

export interface UpdateGroupData {
  name?: string
  is_required?: boolean
  sort_order?: number
}

export interface CreateValueData {
  name: string
  price_modifier: number
  is_default: boolean
  sort_order: number
  sku_suffix?: string | null
}

export interface UpdateValueData {
  name?: string
  price_modifier?: number
  is_default?: boolean
  sort_order?: number
  sku_suffix?: string | null
}

export const useProductOptionsStore = defineStore('productOptions', () => {
  // State: groups keyed by productId
  const groups = ref<Record<string, ProductOptionGroup[]>>({})
  const loading = ref<Record<string, boolean>>({})

  const {
    adminCreateOptionGroup,
    adminUpdateOptionGroup,
    adminDeleteOptionGroup,
    adminCreateOptionValue,
    adminUpdateOptionValue,
    adminDeleteOptionValue,
  } = useProducts()

  // Initialize groups from already-loaded product data (no extra API call)
  const setGroups = (productId: string, productGroups: ProductOptionGroup[]): void => {
    groups.value[productId] = [...productGroups]
  }

  // Create a new option group
  const createGroup = async (productId: string, data: CreateGroupData): Promise<ProductOptionGroup> => {
    loading.value[productId] = true
    try {
      const newGroup = await adminCreateOptionGroup(productId, data) as ProductOptionGroup
      if (!groups.value[productId]) {
        groups.value[productId] = []
      }
      groups.value[productId].push(newGroup)
      return newGroup
    } finally {
      loading.value[productId] = false
    }
  }

  // Update an option group
  const updateGroup = async (
    productId: string,
    groupId: string,
    data: UpdateGroupData
  ): Promise<ProductOptionGroup> => {
    loading.value[productId] = true
    try {
      const updated = await adminUpdateOptionGroup(groupId, data) as ProductOptionGroup
      const idx = (groups.value[productId] || []).findIndex((g) => g.id === groupId)
      if (idx !== -1) {
        groups.value[productId][idx] = updated
      }
      return updated
    } finally {
      loading.value[productId] = false
    }
  }

  // Delete an option group
  const deleteGroup = async (productId: string, groupId: string): Promise<void> => {
    loading.value[productId] = true
    try {
      await adminDeleteOptionGroup(groupId)
      if (groups.value[productId]) {
        groups.value[productId] = groups.value[productId].filter((g) => g.id !== groupId)
      }
    } finally {
      loading.value[productId] = false
    }
  }

  // Create a new option value within a group
  const createValue = async (
    productId: string,
    groupId: string,
    data: CreateValueData
  ): Promise<ProductOptionValue> => {
    loading.value[productId] = true
    try {
      const newValue = await adminCreateOptionValue(groupId, data) as ProductOptionValue
      const group = (groups.value[productId] || []).find((g) => g.id === groupId)
      if (group) {
        group.values.push(newValue)
      }
      return newValue
    } finally {
      loading.value[productId] = false
    }
  }

  // Update an option value
  const updateValue = async (
    productId: string,
    groupId: string,
    valueId: string,
    data: UpdateValueData
  ): Promise<ProductOptionValue> => {
    loading.value[productId] = true
    try {
      const updated = await adminUpdateOptionValue(valueId, data) as ProductOptionValue
      const group = (groups.value[productId] || []).find((g) => g.id === groupId)
      if (group) {
        const idx = group.values.findIndex((v) => v.id === valueId)
        if (idx !== -1) {
          group.values[idx] = updated
        }
      }
      return updated
    } finally {
      loading.value[productId] = false
    }
  }

  // Delete an option value
  const deleteValue = async (productId: string, groupId: string, valueId: string): Promise<void> => {
    loading.value[productId] = true
    try {
      await adminDeleteOptionValue(valueId)
      const group = (groups.value[productId] || []).find((g) => g.id === groupId)
      if (group) {
        group.values = group.values.filter((v) => v.id !== valueId)
      }
    } finally {
      loading.value[productId] = false
    }
  }

  const getGroups = (productId: string): ProductOptionGroup[] => {
    return groups.value[productId] || []
  }

  const isLoading = (productId: string): boolean => {
    return !!loading.value[productId]
  }

  return {
    groups,
    loading,
    setGroups,
    createGroup,
    updateGroup,
    deleteGroup,
    createValue,
    updateValue,
    deleteValue,
    getGroups,
    isLoading,
  }
})
