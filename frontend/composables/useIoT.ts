import { ref } from 'vue'
import { useRuntimeConfig } from '#app'
import { useAuth } from './useAuth'

export interface ComplectationItem {
  id: string
  caption: string
  label: string
  code: string
  simple: boolean
}

export interface IoTDevice {
  id: string
  device_uid: string
  name: string | null
  model: string | null
  is_active: boolean
  last_seen_at: string | null
  complectations?: ComplectationItem[]
}

export interface DeviceRegisterRequest {
  device_uid: string
  name: string | null
  model: string | null
}

export interface TelemetryEvent {
  event: 'telemetry' | 'connected' | 'error'
  data?: any
  message?: string
  device_id?: string
  timestamp?: string
}

export const useIoT = () => {
  const config = useRuntimeConfig()
  const { accessToken } = useAuth()
  
  const devices = ref<IoTDevice[]>([])
  const pending = ref(false)
  const error = ref<any>(null)

  const fetchDevices = async () => {
    pending.value = true
    error.value = null
    try {
      const response = await $fetch<IoTDevice[]>(`${config.public.apiBase}/users/me/devices`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`
        }
      })
      devices.value = response
      return response
    } catch (err: any) {
      error.value = err
      throw err
    } finally {
      pending.value = false
    }
  }

  const registerDevice = async (data: DeviceRegisterRequest) => {
    pending.value = true
    error.value = null
    try {
      const response = await $fetch<IoTDevice>(`${config.public.apiBase}/users/me/devices`, {
        method: 'POST',
        body: data,
        headers: {
          Authorization: `Bearer ${accessToken.value}`
        }
      })
      devices.value.push(response)
      return response
    } catch (err: any) {
      error.value = err
      throw err
    } finally {
      pending.value = false
    }
  }

  const getDevice = async (id: string) => {
    pending.value = true
    error.value = null
    try {
      const response = await $fetch<IoTDevice>(`${config.public.apiBase}/users/me/devices/${id}`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`
        }
      })
      return response
    } catch (err: any) {
      error.value = err
      throw err
    } finally {
      pending.value = false
    }
  }

  const connectDevice = (id: string, onMessage: (event: TelemetryEvent) => void) => {
    const wsUrl = config.public.apiBase.replace(/^http/, 'ws')
    const socket = new WebSocket(`${wsUrl}/users/me/devices/${id}/connect?token=${accessToken.value}`)
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data) as TelemetryEvent
      onMessage(data)
    }

    return socket
  }

  const formatDeviceModel = (model: string | null) => {
    if (!model) return 'Неизвестная модель'
    const models: Record<string, string> = {
      'wifi_obd2': 'Wifi OBD2',
      'wifi_obd2_advanced': 'Wifi OBD2 Advanced'
    }
    return models[model] || model
  }

  const fetchAllComplectations = async (): Promise<ComplectationItem[]> => {
    try {
      const response = await $fetch<ComplectationItem[]>(`${config.public.apiBase}/users/complectations`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`
        }
      })
      return response
    } catch (err: unknown) {
      return []
    }
  }

  return {
    devices,
    pending,
    error,
    fetchDevices,
    registerDevice,
    getDevice,
    connectDevice,
    formatDeviceModel,
    fetchAllComplectations
  }
}
