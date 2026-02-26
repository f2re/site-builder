import { ref } from 'vue'
import { useRuntimeConfig } from '#app'
import { useAuth } from './useAuth'

export interface Device {
  id: string
  device_uid: string
  name: string | null
  model: string | null
  is_active: boolean
  last_seen_at: string | null
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
  const { token } = useAuth()
  
  const devices = ref<Device[]>([])
  const pending = ref(false)
  const error = ref<any>(null)

  const fetchDevices = async () => {
    pending.value = true
    error.value = null
    try {
      const response = await $fetch<Device[]>(`${config.public.apiBase}/users/me/devices`, {
        headers: {
          Authorization: `Bearer ${token.value}`
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
      const response = await $fetch<Device>(`${config.public.apiBase}/users/me/devices`, {
        method: 'POST',
        body: data,
        headers: {
          Authorization: `Bearer ${token.value}`
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
      const response = await $fetch<Device>(`${config.public.apiBase}/users/me/devices/${id}`, {
        headers: {
          Authorization: `Bearer ${token.value}`
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
    const socket = new WebSocket(`${wsUrl}/users/me/devices/${id}/connect?token=${token.value}`)
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data) as TelemetryEvent
      onMessage(data)
    }

    return socket
  }

  return {
    devices,
    pending,
    error,
    fetchDevices,
    registerDevice,
    getDevice,
    connectDevice
  }
}
