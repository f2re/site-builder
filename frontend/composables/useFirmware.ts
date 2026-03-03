import { useFirmwareStore } from '~/stores/firmwareStore'
import type { Device, Version, Complectation } from '~/stores/firmwareStore'

export const useFirmware = () => {
  const store = useFirmwareStore()
  const apiFetch = useApiFetch()

  const fetchToken = async () => {
    const data = await apiFetch<any>('/firmware/my-token')
    if (data) store.setToken(data.token)
    return data
  }

  const fetchMyDevices = async () => {
    const data = await apiFetch<Device[]>('/firmware/my-devices')
    if (data) store.setDevices(data)
    return data
  }

  const addDevice = async (serial: string) => {
    const data = await apiFetch<Device>('/firmware/add-device', {
      method: 'POST',
      body: { serial }
    })
    if (data) await fetchMyDevices()
    return data
  }

  const fetchVersions = async (type: string) => {
    const data = await apiFetch<any>(`/firmware/versions/${type}`)
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
    const response = await apiFetch<Blob>('/firmware/download', {
      method: 'POST',
      body: { 
        serial, 
        device_type: deviceType,
        version, 
        selected_complectation_ids: selectedIds 
      },
      responseType: 'blob'
    })

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
    const data = await apiFetch<Device[]>('/admin/firmware/devices')
    if (data) store.setGlobalDevices(data)
    return data
  }

  const fetchAllComplectations = async () => {
    const data = await apiFetch<Complectation[]>('/admin/firmware/complectations')
    if (data) store.setAllComplectations(data)
    return data
  }

  const importExcel = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return await apiFetch<any>('/admin/firmware/import', {
      method: 'POST',
      body: formData
    })
  }

  const mergeUsers = async (sourceEmail: string, targetEmail: string) => {
    return await apiFetch<any>('/admin/firmware/merge-users', {
      method: 'POST',
      body: { source_email: sourceEmail, target_email: targetEmail }
    })
  }

  const createComplectation = async (data: Omit<Complectation, 'id'>) => {
    return await apiFetch<Complectation>('/admin/firmware/complectations', {
      method: 'POST',
      body: data
    })
  }

  const updateComplectation = async (id: string, data: Partial<Complectation>) => {
    return await apiFetch<Complectation>(`/admin/firmware/complectations/${id}`, {
      method: 'PUT',
      body: data
    })
  }

  const deleteComplectation = async (id: string) => {
    return await apiFetch<any>(`/admin/firmware/complectations/${id}`, {
      method: 'DELETE'
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
