export interface ContactMessage {
  id: string
  name: string
  email: string
  phone: string | null
  subject: string
  message: string
  status: 'NEW' | 'READ' | 'REPLIED'
  ip_address: string | null
  created_at: string
  read_at: string | null
}

export interface ContactListResponse {
  items: ContactMessage[]
  total: number
  next_cursor: string | null
}

export interface ContactSettings {
  contact_email: string | null
  contact_page_text: string | null
}

export const useAdminContact = () => {
  const apiFetch = useApiFetch()

  const getMessages = (params: { status?: string; cursor?: string; limit?: number }) =>
    useApi<ContactListResponse>('/admin/contact', { query: params })

  const getMessage = (id: string) =>
    useApi<ContactMessage>(`/admin/contact/${id}`)

  const replyMessage = (id: string) =>
    apiFetch<ContactMessage>(`/admin/contact/${id}/reply`, {
      method: 'PUT',
      body: { status: 'REPLIED' },
    })

  const deleteMessage = (id: string) =>
    apiFetch(`/admin/contact/${id}`, { method: 'DELETE' })

  const getSettings = () =>
    useApi<ContactSettings>('/admin/settings/contact')

  const updateSettings = (data: Partial<ContactSettings>) =>
    apiFetch<ContactSettings>('/admin/settings/contact', {
      method: 'PUT',
      body: data,
    })

  return {
    getMessages,
    getMessage,
    replyMessage,
    deleteMessage,
    getSettings,
    updateSettings,
  }
}
