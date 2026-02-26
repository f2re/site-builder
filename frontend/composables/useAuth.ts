import { useCookie } from '#app'

export const useAuth = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase
  
  const accessToken = useCookie<string | null>('access_token', {
    maxAge: 60 * 30, // 30 minutes
    path: '/'
  })
  
  const refreshToken = useCookie<string | null>('refresh_token', {
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: '/'
  })

  const login = async (email: string, password: string) => {
    const { data, error } = await useFetch<any>(`${apiBase}/auth/login`, {
      method: 'POST',
      body: { email, password }
    })
    
    if (data.value) {
      accessToken.value = data.value.access_token
      refreshToken.value = data.value.refresh_token
    }
    
    return { data, error }
  }

  const logout = () => {
    accessToken.value = null
    refreshToken.value = null
  }

  const useApi = (url: string, options: any = {}) => {
    return useFetch(url, {
      ...options,
      headers: {
        ...options.headers,
        ...(accessToken.value ? { Authorization: `Bearer ${accessToken.value}` } : {})
      }
    })
  }

  return {
    accessToken,
    refreshToken,
    login,
    logout,
    useApi
  }
}
