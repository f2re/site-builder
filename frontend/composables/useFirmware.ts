import { useFirmwareStore } from '~/stores/firmwareStore'
import type { DeviceRead, AdminDevice, DuplicateGroup, Complectation, VersionInfo } from '~/stores/firmwareStore'

// Keep legacy export for any code that imports Device from here
export type { DeviceRead, AdminDevice, DuplicateGroup, Complectation }

export const useFirmware = () => {
  const store = useFirmwareStore()
  const apiFetch = useApiFetch()

  // ─── Auth-required endpoints ─────────────────────────────────────────────

  const fetchToken = async () => {
    const data = await apiFetch<{ token: string }>('/firmware/my-token')
    if (data) store.setToken(data.token)
    return data
  }

  const fetchMyDevices = async () => {
    const data = await apiFetch<DeviceRead[]>('/firmware/my-devices')
    if (data) store.setDevices(data)
    return data
  }

  const addDevice = async (serial: string) => {
    const data = await apiFetch<DeviceRead>('/firmware/add-device', {
      method: 'POST',
      body: { serial },
    })
    if (data) await fetchMyDevices()
    return data
  }

  const downloadFirmware = async (
    serial: string,
    deviceType: string,
    version: string,
    selectedIds: string[]
  ) => {
    const response = await apiFetch<Blob>('/firmware/download', {
      method: 'POST',
      body: {
        serial,
        device_type: deviceType,
        version,
        selected_complectation_ids: selectedIds,
      },
      responseType: 'blob',
    })

    triggerBlobDownload(response, `firmware_${serial}_${version}.bin`)
    return response
  }

  const toggleComplectation = async (serial: string, complectationId: string) => {
    return await apiFetch<{ ok: boolean }>(
      `/firmware/devices/${serial}/complectations/${complectationId}/toggle`,
      { method: 'POST' }
    )
  }

  // ─── Public (by-token) endpoints ─────────────────────────────────────────

  const fetchDevicesByToken = async (token: string): Promise<DeviceRead[]> => {
    const data = await apiFetch<DeviceRead[]>(
      `/firmware/by-token/${token}/devices`
    )
    if (data) store.setDevices(data)
    return data ?? []
  }

  const fetchVersionsByToken = async (
    token: string,
    deviceType: string
  ): Promise<string[]> => {
    const data = await apiFetch<{ versions: string[] }>(
      `/firmware/by-token/${token}/versions/${deviceType}`
    )
    return data?.versions ?? []
  }

  const fetchVersionInfo = async (
    version: string,
    deviceType: string
  ): Promise<VersionInfo | null> => {
    const data = await apiFetch<VersionInfo>('/firmware/version-info', {
      params: { version, device_type: deviceType },
    })
    return data ?? null
  }

  const downloadByToken = async (
    token: string,
    serial: string,
    deviceType: string,
    version: string,
    selectedIds: string[]
  ) => {
    const response = await apiFetch<Blob>(
      `/firmware/by-token/${token}/download`,
      {
        method: 'POST',
        body: {
          serial,
          device_type: deviceType,
          version,
          selected_complectation_ids: selectedIds,
        },
        responseType: 'blob',
      }
    )

    triggerBlobDownload(response, `firmware_${serial}_${version}.bin`)
    return response
  }

  // ─── Helpers ─────────────────────────────────────────────────────────────

  /** Triggers a browser file download from a Blob */
  function triggerBlobDownload(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  // ─── Admin endpoints ──────────────────────────────────────────────────────

  const fetchGlobalDevices = async () => {
    const data = await apiFetch<DeviceRead[]>('/admin/firmware/devices')
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
    return await apiFetch<unknown>('/admin/firmware/import', {
      method: 'POST',
      body: formData,
    })
  }

  const mergeUsers = async (sourceEmail: string, targetEmail: string) => {
    return await apiFetch<unknown>('/admin/firmware/merge-users', {
      method: 'POST',
      body: { source_email: sourceEmail, target_email: targetEmail },
    })
  }

  const createComplectation = async (data: Omit<Complectation, 'id'>) => {
    return await apiFetch<Complectation>('/admin/firmware/complectations', {
      method: 'POST',
      body: data,
    })
  }

  const updateComplectation = async (id: string, data: Partial<Complectation>) => {
    return await apiFetch<Complectation>(`/admin/firmware/complectations/${id}`, {
      method: 'PUT',
      body: data,
    })
  }

  const deleteComplectation = async (id: string) => {
    return await apiFetch<unknown>(`/admin/firmware/complectations/${id}`, {
      method: 'DELETE',
    })
  }

  return {
    // Auth
    fetchToken,
    fetchMyDevices,
    addDevice,
    downloadFirmware,
    toggleComplectation,
    // Public
    fetchDevicesByToken,
    fetchVersionsByToken,
    fetchVersionInfo,
    downloadByToken,
    // Admin
    fetchGlobalDevices,
    fetchAllComplectations,
    importExcel,
    mergeUsers,
    createComplectation,
    updateComplectation,
    deleteComplectation,
  }
}
