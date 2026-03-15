export interface ContactFormData {
  name: string
  email: string
  phone?: string
  subject: string
  message: string
  turnstile_token: string
}

export interface ContactSettings {
  contact_email: string | null
  contact_page_text: string | null
}

export interface ContactMessageRead {
  id: string
  name: string
  email: string
  subject: string
  created_at: string
}

export const useContact = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  /**
   * Submit contact form.
   * POST /api/v1/contact
   * Rate limit: 5/minute per IP
   * Errors: 422 (Turnstile failed), 429 (rate limit)
   */
  const submitContactForm = async (data: ContactFormData): Promise<ContactMessageRead> => {
    return $fetch<ContactMessageRead>(`${apiBase}/contact`, {
      method: 'POST',
      body: data,
    })
  }

  /**
   * Fetch public contact page settings.
   * GET /api/v1/contact/settings — PUBLIC, no auth required
   * Falls back gracefully if endpoint is not available.
   */
  const getContactSettings = async (): Promise<ContactSettings> => {
    try {
      return await $fetch<ContactSettings>(`${apiBase}/contact/settings`)
    } catch {
      // Endpoint may not be implemented yet — silently fall back
      return { contact_email: null, contact_page_text: null }
    }
  }

  return {
    submitContactForm,
    getContactSettings,
  }
}
