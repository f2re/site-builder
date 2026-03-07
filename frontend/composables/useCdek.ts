// composable: useCdek | frontend-agent | task: feature_cdek_checkout_001

export interface CdekCity {
  code: number
  city: string
  fias_guid?: string | null
  region?: string | null
  country?: string | null
}

export interface CdekPickupPoint {
  code: string
  name: string
  address: string
  latitude: number
  longitude: number
  work_time: string
  phone: string
  note?: string | null
}

export interface DeliveryCalcParams {
  from_city_code?: number
  to_city_code: number
  weight_grams?: number
  tariff_code?: number
}

export interface DeliveryCalcResult {
  cost_rub: number
  days_min: number
  days_max: number
  tariff_code: string
}

// Fallback mock cities used when backend is unavailable
const MOCK_CITIES: CdekCity[] = [
  { code: 44, city: 'Москва', region: 'Московская обл.', country: 'Россия' },
  { code: 137, city: 'Санкт-Петербург', region: 'Санкт-Петербург', country: 'Россия' },
  { code: 270, city: 'Новосибирск', region: 'Новосибирская обл.', country: 'Россия' },
  { code: 63, city: 'Екатеринбург', region: 'Свердловская обл.', country: 'Россия' },
  { code: 373, city: 'Казань', region: 'Татарстан', country: 'Россия' },
  { code: 278, city: 'Нижний Новгород', region: 'Нижегородская обл.', country: 'Россия' },
  { code: 56, city: 'Краснодар', region: 'Краснодарский край', country: 'Россия' },
  { code: 7, city: 'Самара', region: 'Самарская обл.', country: 'Россия' },
  { code: 6, city: 'Уфа', region: 'Башкортостан', country: 'Россия' },
  { code: 255, city: 'Ростов-на-Дону', region: 'Ростовская обл.', country: 'Россия' },
]

export const useCdek = () => {
  const apiFetch = useApiFetch()

  /**
   * Search cities via CDEK API with debounce handled by caller.
   * Falls back to mock cities on error.
   */
  const searchCities = async (query: string): Promise<CdekCity[]> => {
    if (query.length < 2) return []
    try {
      const result = await apiFetch<CdekCity[]>('/delivery/cities', {
        params: { query, country_codes: ['RU'] }
      })
      return result ?? []
    } catch {
      // Backend unavailable — filter mock list
      const q = query.toLowerCase()
      return MOCK_CITIES.filter(c => c.city.toLowerCase().startsWith(q))
    }
  }

  /**
   * Get pickup points (PVZ) for a given city code.
   */
  const getPickupPoints = async (cityCode: number): Promise<CdekPickupPoint[]> => {
    try {
      const result = await apiFetch<CdekPickupPoint[]>('/delivery/pickup-points', {
        params: { city_code: cityCode }
      })
      return result ?? []
    } catch {
      return []
    }
  }

  /**
   * Calculate delivery cost and days.
   */
  const calculateDelivery = async (params: DeliveryCalcParams): Promise<DeliveryCalcResult | null> => {
    try {
      const result = await apiFetch<DeliveryCalcResult>('/delivery/calculate', {
        params: {
          from_city_code: params.from_city_code ?? 44,
          to_city_code: params.to_city_code,
          weight_grams: params.weight_grams ?? 500,
          tariff_code: params.tariff_code ?? 136,
        }
      })
      return result ?? null
    } catch {
      return null
    }
  }

  return { searchCities, getPickupPoints, calculateDelivery }
}
