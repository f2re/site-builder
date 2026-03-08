// store: deliveryStore | frontend-agent | task: feature_cdek_checkout_001 + p10_frontend_delivery_selector

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CdekCity, CdekPickupPoint, DeliveryCalcResult } from '~/composables/useCdek'

export type DeliveryType = 'pickup' | 'courier'
export type DeliveryProvider = 'cdek' | 'pochta' | 'ozon' | 'wildberries'

export interface CourierAddress {
  street: string
  building: string
  apartment: string
  comment: string
}

export interface DeliveryOption {
  provider: DeliveryProvider
  provider_label: string
  service_type: 'pickup' | 'courier'
  service_name: string
  cost_rub: number
  days_min: number
  days_max: number
  tariff_code: string
  logo_url: string
}

export const useDeliveryStore = defineStore('delivery', () => {
  // --- State ---
  const deliveryType = ref<DeliveryType>('pickup')
  const selectedCity = ref<CdekCity | null>(null)
  const selectedPickupPoint = ref<CdekPickupPoint | null>(null)
  const courierAddress = ref<CourierAddress>({
    street: '',
    building: '',
    apartment: '',
    comment: '',
  })
  const calcResult = ref<DeliveryCalcResult | null>(null)
  const isCalculating = ref(false)

  // --- New: Multi-provider state ---
  const selectedProvider = ref<DeliveryProvider | null>(null)
  const availableOptions = ref<DeliveryOption[]>([])
  const isLoadingRates = ref(false)

  // --- Computed ---
  const deliveryCost = computed(() => calcResult.value?.cost_rub ?? 0)
  const deliveryDays = computed(() => {
    if (!calcResult.value) return null
    const { days_min, days_max } = calcResult.value
    return days_min === days_max ? `${days_min}` : `${days_min}–${days_max}`
  })

  const isDeliveryReady = computed(() => {
    if (!selectedCity.value) return false
    if (deliveryType.value === 'pickup') {
      return !!selectedPickupPoint.value
    }
    return courierAddress.value.street.trim().length > 0 && courierAddress.value.building.trim().length > 0
  })

  // --- Actions ---
  function setDeliveryType(type: DeliveryType) {
    deliveryType.value = type
    // Reset downstream selections when switching type
    selectedPickupPoint.value = null
    calcResult.value = null
    persist()
  }

  function setCity(city: CdekCity | null) {
    selectedCity.value = city
    selectedPickupPoint.value = null
    calcResult.value = null
    persist()
  }

  function setProvider(provider: DeliveryProvider | null) {
    selectedProvider.value = provider
    selectedPickupPoint.value = null
    calcResult.value = null
    persist()
  }

  function setAvailableOptions(options: DeliveryOption[]) {
    availableOptions.value = options
    persist()
  }

  function setIsLoadingRates(val: boolean) {
    isLoadingRates.value = val
  }

  function setPickupPoint(pvz: CdekPickupPoint | null) {
    selectedPickupPoint.value = pvz
    persist()
  }

  function setCourierAddress(addr: Partial<CourierAddress>) {
    courierAddress.value = { ...courierAddress.value, ...addr }
    persist()
  }

  function setCalcResult(result: DeliveryCalcResult | null) {
    calcResult.value = result
    persist()
  }

  function reset() {
    deliveryType.value = 'pickup'
    selectedCity.value = null
    selectedPickupPoint.value = null
    courierAddress.value = { street: '', building: '', apartment: '', comment: '' }
    calcResult.value = null
    isCalculating.value = false
    selectedProvider.value = null
    availableOptions.value = []
    isLoadingRates.value = false
    if (import.meta.client) {
      localStorage.removeItem('delivery')
    }
  }

  function persist() {
    if (import.meta.client) {
      localStorage.setItem('delivery', JSON.stringify({
        deliveryType: deliveryType.value,
        selectedCity: selectedCity.value,
        selectedPickupPoint: selectedPickupPoint.value,
        courierAddress: courierAddress.value,
        calcResult: calcResult.value,
        selectedProvider: selectedProvider.value,
        availableOptions: availableOptions.value,
      }))
    }
  }

  function init() {
    if (import.meta.client) {
      const saved = localStorage.getItem('delivery')
      if (saved) {
        try {
          const data = JSON.parse(saved)
          if (data.deliveryType) deliveryType.value = data.deliveryType
          if (data.selectedCity) selectedCity.value = data.selectedCity
          if (data.selectedPickupPoint) selectedPickupPoint.value = data.selectedPickupPoint
          if (data.courierAddress) courierAddress.value = data.courierAddress
          if (data.calcResult) calcResult.value = data.calcResult
          if (data.selectedProvider) selectedProvider.value = data.selectedProvider
          if (data.availableOptions) availableOptions.value = data.availableOptions
        } catch {
          // ignore parse errors
        }
      }
    }
  }

  return {
    deliveryType,
    selectedCity,
    selectedPickupPoint,
    courierAddress,
    calcResult,
    isCalculating,
    selectedProvider,
    availableOptions,
    isLoadingRates,
    deliveryCost,
    deliveryDays,
    isDeliveryReady,
    setDeliveryType,
    setCity,
    setProvider,
    setAvailableOptions,
    setIsLoadingRates,
    setPickupPoint,
    setCourierAddress,
    setCalcResult,
    reset,
    init,
  }
})
