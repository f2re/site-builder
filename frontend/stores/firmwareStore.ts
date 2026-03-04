import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface FirmwareDevice {
  id: string
  serial: string
  type: 'OBD' | 'AFR'
  created_at: string
  complectations: Complectation[]
}

export interface Version {
  id: string
  version: string
  changelog: string | null
}

export interface Complectation {
  id: string
  caption: string
  label: string
  code: number
  simple: boolean
}

export const useFirmwareStore = defineStore('firmware', () => {
  const token = ref<string | null>(null)
  const devices = ref<FirmwareDevice[]>([])
  const versions = ref<Record<string, Version[]>>({})
  const complectations = ref<Record<string, Complectation[]>>({})

  // Admin state
  const globalDevices = ref<FirmwareDevice[]>([])
  const allComplectations = ref<Complectation[]>([])

  function setToken(t: string) {
    token.value = t
  }

  function setDevices(d: FirmwareDevice[]) {
    devices.value = d
  }

  function setVersions(type: string, v: Version[]) {
    versions.value[type] = v
  }

  function setComplectations(deviceId: string, c: Complectation[]) {
    complectations.value[deviceId] = c
  }

  function setGlobalDevices(d: FirmwareDevice[]) {
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
