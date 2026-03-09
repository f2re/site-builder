import { ref, computed, watch } from 'vue'
import type { Ref, ComputedRef } from 'vue'
import type { Product, ProductOptionGroup, ProductPriceCalculationResponse } from '~/composables/useProducts'
import { useProducts } from '~/composables/useProducts'

export interface UseProductOptionsReturn {
  selectedOptions: Ref<Record<string, string>>
  allRequiredSelected: ComputedRef<boolean>
  calculatedPrice: Ref<ProductPriceCalculationResponse | null>
  isCalculating: Ref<boolean>
  selectedValueIds: ComputedRef<string[]>
  fetchPrice: () => Promise<void>
}

export function useProductOptions(product: Ref<Product | null | undefined>): UseProductOptionsReturn {
  const { calculatePrice } = useProducts()

  const selectedOptions = ref<Record<string, string>>({})
  const calculatedPrice = ref<ProductPriceCalculationResponse | null>(null)
  const isCalculating = ref(false)

  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  // Auto-select defaults when product changes
  watch(
    product,
    (newVal) => {
      if (!newVal?.option_groups?.length) return

      const defaults: Record<string, string> = {}
      newVal.option_groups.forEach((group: ProductOptionGroup) => {
        // Only handle single-select (radio) groups
        if (group.type !== 'checkbox') {
          const defaultVal = group.values.find((v) => v.is_default) || group.values[0]
          if (defaultVal) {
            defaults[group.id] = defaultVal.id
          }
        }
      })
      selectedOptions.value = defaults
    },
    { immediate: true }
  )

  const allRequiredSelected: ComputedRef<boolean> = computed(() => {
    if (!product.value?.option_groups) return true
    return product.value.option_groups
      .filter((g: ProductOptionGroup) => g.is_required && g.type !== 'checkbox')
      .every((g: ProductOptionGroup) => !!selectedOptions.value[g.id])
  })

  const selectedValueIds: ComputedRef<string[]> = computed(() => {
    return Object.values(selectedOptions.value).filter(Boolean)
  })

  const fetchPrice = async (): Promise<void> => {
    if (!product.value?.id) return
    if (selectedValueIds.value.length === 0) {
      calculatedPrice.value = null
      return
    }

    isCalculating.value = true
    try {
      const result = await calculatePrice(product.value.id, selectedValueIds.value)
      calculatedPrice.value = result
    } catch {
      calculatedPrice.value = null
    } finally {
      isCalculating.value = false
    }
  }

  // Debounced watch on selectedOptions changes
  watch(
    selectedOptions,
    () => {
      if (debounceTimer) clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        fetchPrice()
      }, 300)
    },
    { deep: true }
  )

  return {
    selectedOptions,
    allRequiredSelected,
    calculatedPrice,
    isCalculating,
    selectedValueIds,
    fetchPrice,
  }
}
