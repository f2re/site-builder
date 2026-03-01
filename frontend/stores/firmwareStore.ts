import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Device {
  id: string
  serial: string
  type: 'OBD' | 'AFR'
  added_at: string
}

export interface Version {
  id: string
  version: string
  changelog: string | null
  file_path: string
}

export interface Complectation {
  id: string
  name: string
  description: string | null
  price: number
  is_active: boolean
}

export const useFirmwareStore = defineStore('firmware', () => {
  const token = ref<string | null>(null)
  const devices = ref<Device[]>([])
  const versions = ref<Record<string, Version[]>>({})
  const complectations = ref<Record<string, Complectation[]>>({})

  // Admin state
  const globalDevices = ref<Device[]>([])
  const allComplectations = ref<Complectation[]>([])

  function setToken(t: string) {
    token.value = t
  }

  function setDevices(d: Device[]) {
    devices.value = d
  }

  function setVersions(type: string, v: Version[]) {
    versions.value[type] = v
  }

  function setComplectations(deviceId: string, c: Complectation[]) {
    complectations.value[deviceId] = c
  }

  function setGlobalDevices(d: Device[]) {
    globalDevices.value = d
  }

  function setAllComplectations(c: Complectation[]) {
    allComplectations.value = c
  }

  return {
    token,
    devices,
    versions,
    complectations,
    globalDevices,
    allComplectations,
    setToken,
    setDevices,
    setVersions,
    setComplectations,
    setGlobalDevices,
    setAllComplectations
  }
})
