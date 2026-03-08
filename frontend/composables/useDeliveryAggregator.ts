// composable: useDeliveryAggregator | frontend-agent | task: p10_frontend_delivery_selector

import type { DeliveryOption } from '~/stores/deliveryStore'

export interface AggregatedRateRequest {
  from_city_code?: number
  to_city_code: number
  weight_grams?: number
  length_cm?: number
  width_cm?: number
  height_cm?: number
}

export interface PickupPointResult {
  code: string
  provider: string
  name: string
  address: string
  latitude: number
  longitude: number
  work_time: string
  phone?: string
  note?: string
}

const MOCK_OPTIONS: DeliveryOption[] = [
  { provider: 'cdek', provider_label: 'СДЭК', service_type: 'pickup', service_name: 'СДЭК ПВЗ', cost_rub: 299, days_min: 3, days_max: 5, tariff_code: '136', logo_url: '/img/delivery/cdek.svg' },
  { provider: 'cdek', provider_label: 'СДЭК', service_type: 'courier', service_name: 'СДЭК Курьер', cost_rub: 399, days_min: 2, days_max: 4, tariff_code: '137', logo_url: '/img/delivery/cdek.svg' },
  { provider: 'pochta', provider_label: 'Почта России', service_type: 'courier', service_name: 'Почта 1-й класс', cost_rub: 249, days_min: 4, days_max: 10, tariff_code: '23030', logo_url: '/img/delivery/pochta.svg' },
  { provider: 'ozon', provider_label: 'Ozon', service_type: 'pickup', service_name: 'Ozon Логистика', cost_rub: 199, days_min: 5, days_max: 9, tariff_code: 'ozon_std', logo_url: '/img/delivery/ozon.svg' },
  { provider: 'wildberries', provider_label: 'Wildberries', service_type: 'pickup', service_name: 'WB Доставка', cost_rub: 129, days_min: 6, days_max: 12, tariff_code: 'wb_std', logo_url: '/img/delivery/wildberries.svg' },
]

export const useDeliveryAggregator = () => {
  const apiFetch = useApiFetch()

  const calculateAll = async (params: AggregatedRateRequest): Promise<DeliveryOption[]> => {
    try {
      const result = await apiFetch<DeliveryOption[]>('/delivery/calculate-all', {
        method: 'POST',
        body: params,
      })
      return result ?? MOCK_OPTIONS
    } catch {
      return MOCK_OPTIONS
    }
  }

  const getPickupPointsAll = async (
    cityCode: number,
    provider?: string
  ): Promise<PickupPointResult[]> => {
    try {
      const result = await apiFetch<PickupPointResult[]>('/delivery/pickup-points-all', {
        params: { city_code: cityCode, provider }
      })
      return result ?? []
    } catch {
      return []
    }
  }

  return { calculateAll, getPickupPointsAll }
}
