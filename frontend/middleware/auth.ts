import { useAuthStore } from '~/stores/authStore'

export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()
  
  // Если пользователь не авторизован, отправляем на страницу логина
  if (!authStore.isAuthenticated) {
    return navigateTo('/auth/login', {
      query: {
        redirect: to.fullPath,
      },
    })
  }

  // Если это админский роут, проверяем роль
  if (to.path.startsWith('/admin') && !authStore.isAdmin) {
    return navigateTo('/', { replace: true })
  }
})
