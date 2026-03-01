import { useFirmwareStore } from '~/stores/firmwareStore'
import type { Device, Version, Complectation } from '~/stores/firmwareStore'

export const useFirmware = () => {
  const store = useFirmwareStore()
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  const fetchToken = async () => {
    const data = await $fetch<any>(`${config.public.apiBase}/api/v1/firmware/my-token`, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    if (data) store.setToken(data.token)
    return data
  }

  const fetchMyDevices = async () => {
    const data = await $fetch<Device[]>(`${config.public.apiBase}/api/v1/firmware/my-devices`, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    if (data) store.setDevices(data)
    return data
  }

  const addDevice = async (serial: string) => {
    const data = await $fetch<Device>(`${config.public.apiBase}/api/v1/firmware/add-device`, {
      method: 'POST',
      body: { serial },
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    if (data) await fetchMyDevices()
    return data
  }

  const fetchVersions = async (type: string) => {
    const data = await $fetch<any>(`${config.public.apiBase}/api/v1/firmware/versions/${type}`, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    // data.versions is an array of strings
    if (data?.versions) {
      const versionObjs: Version[] = data.versions.map((v: string) => ({
        id: v,
        version: v,
        changelog: null
      }))
      store.setVersions(type, versionObjs)
    }
    return data
  }

  const downloadFirmware = async (serial: string, deviceType: string, version: string, selectedIds: string[]) => {
    // This returns a blob/file stream
    const response = await $fetch<Blob>(`${config.public.apiBase}/api/v1/firmware/download`, {
      method: 'POST',
      body: { 
        serial, 
        device_type: deviceType,
        version, 
        selected_complectation_ids: selectedIds 
      },
      headers: { Authorization: `Bearer ${authStore.accessToken}` },
      responseType: 'blob'
    })

    // Create a temporary link to trigger download
    const url = window.URL.createObjectURL(response)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `firmware_${serial}_${version}.bin`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    return response
  }

  // Admin methods
  const fetchGlobalDevices = async () => {
    const data = await $fetch<Device[]>(`${config.public.apiBase}/api/v1/admin/firmware/devices`, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    if (data) store.setGlobalDevices(data)
    return data
  }

  const fetchAllComplectations = async () => {
    const data = await $fetch<Complectation[]>(`${config.public.apiBase}/api/v1/admin/firmware/complectations`, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    if (data) store.setAllComplectations(data)
    return data
  }

  const importExcel = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return await $fetch<any>(`${config.public.apiBase}/api/v1/admin/firmware/import`, {
      method: 'POST',
      body: formData,
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
  }

  const mergeUsers = async (sourceEmail: string, targetEmail: string) => {
    return await $fetch<any>(`${config.public.apiBase}/api/v1/admin/firmware/merge-users`, {
      method: 'POST',
      body: { source_email: sourceEmail, target_email: targetEmail },
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
  }

  const createComplectation = async (data: Omit<Complectation, 'id'>) => {
    return await $fetch<Complectation>(`${config.public.apiBase}/api/v1/admin/firmware/complectations`, {
      method: 'POST',
      body: data,
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
  }

  const updateComplectation = async (id: string, data: Partial<Complectation>) => {
    return await $fetch<Complectation>(`${config.public.apiBase}/api/v1/admin/firmware/complectations/${id}`, {
      method: 'PUT',
      body: data,
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
  }

  const deleteComplectation = async (id: string) => {
    return await $fetch<any>(`${config.public.apiBase}/api/v1/admin/firmware/complectations/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
  }

  return {
    fetchToken,
    fetchMyDevices,
    addDevice,
    fetchVersions,
    downloadFirmware,
    fetchGlobalDevices,
    fetchAllComplectations,
    importExcel,
    mergeUsers,
    createComplectation,
    updateComplectation,
    deleteComplectation
  }
}
