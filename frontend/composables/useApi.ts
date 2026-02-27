import { useAuthStore } from '~/stores/authStore'
import type { UseFetchOptions } from 'nuxt/app'

export function useApi<T>(
  url: string | (() => string), 
  options: UseFetchOptions<T> = {}
) {
  const authStore = useAuthStore()
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const apiFetch = $fetch.create({
    baseURL: apiBase,
    onRequest({ options }) {
      if (authStore.accessToken) {
        options.headers = new Headers(options.headers)
        options.headers.set('Authorization', `Bearer ${authStore.accessToken}`)
      }
    },
    async onResponseError({ response, options, request }) {
      // @ts-ignore
      if (response.status === 401 && !options._retry) {
        // @ts-ignore
        options._retry = true
        
        const newToken = await authStore.refreshToken()
        
        if (newToken) {
          options.headers = new Headers(options.headers)
          options.headers.set('Authorization', `Bearer ${newToken}`)
          
          // Retry the request
          return $fetch(request, options)
        }
      }
    }
  })

  return useFetch(url, {
    ...options,
    $fetch: apiFetch
  })
}
