import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// API schema: DeviceRead (matches backend DeviceRead schema)
export interface DeviceRead {
  id: string
  serial: string
  device_type: 'OBD' | 'AFR'
  comment: string | null
  created_at: string
  complectations: Complectation[]
}

// Legacy alias — keep for backward compatibility with existing components
export type FirmwareDevice = DeviceRead

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

export interface VersionInfo {
  changes: string
  links: Record<string, string>
}

// Admin-specific: DeviceRead + owner info
export interface AdminDevice {
  id: string
  serial: string
  device_type: 'OBD' | 'AFR'
  comment: string | null
  created_at: string
  complectations: Complectation[]
  owner_id: string | null
  owner_email: string | null
  owner_name: string | null
}

export interface DuplicateAccount {
  user_id: string
  email: string
  name: string
  device_count: number
}

export interface DuplicateGroup {
  accounts: DuplicateAccount[]
}

export const useFirmwareStore = defineStore('firmware', () => {
  const authStore = useAuthStore()

  const token = ref<string | null>(null)
  const devices = ref<DeviceRead[]>([])
  const versions = ref<Record<string, Version[]>>({})
  const complectations = ref<Record<string, Complectation[]>>({})

  // Public token mode (from URL or form input)
  const publicToken = ref<string>('')

  // Public mode: token is set and user is NOT logged in
  const isPublicMode = computed(
    () => !!publicToken.value && !authStore.isAuthenticated
  )

  // Admin state
  const globalDevices = ref<AdminDevice[]>([])
  const allComplectations = ref<Complectation[]>([])
  const adminDevicesTotal = ref(0)
  const duplicates = ref<DuplicateGroup[]>([])

  function setToken(t: string) {
    token.value = t
  }

  function setDevices(d: DeviceRead[]) {
    devices.value = d
  }

  function setPublicToken(t: string) {
    publicToken.value = t
  }

  function setVersions(type: string, v: Version[]) {
    versions.value[type] = v
  }

  function setComplectations(deviceId: string, c: Complectation[]) {
    complectations.value[deviceId] = c
  }

  function setGlobalDevices(d: AdminDevice[]) {
    globalDevices.value = d
  }

  function setAdminDevicesTotal(n: number) {
    adminDevicesTotal.value = n
  }

  function setDuplicates(d: DuplicateGroup[]) {
    duplicates.value = d
  }

  function setAllComplectations(c: Complectation[]) {
    allComplectations.value = c
  }

  return {
    token,
    devices,
    versions,
    complectations,
    publicToken,
    isPublicMode,
    globalDevices,
    allComplectations,
    adminDevicesTotal,
    duplicates,
    setToken,
    setDevices,
    setPublicToken,
    setVersions,
    setComplectations,
    setGlobalDevices,
    setAdminDevicesTotal,
    setDuplicates,
    setAllComplectations,
  }
})
