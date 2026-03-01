import { useAuthStore } from '~/stores/authStore'
import { useUserStore } from '~/stores/userStore'
import { useToast } from '~/composables/useToast'

export default defineNuxtRouteMiddleware(async (to, from) => {
  const authStore = useAuthStore()
  const userStore = useUserStore()
  
  // Если пользователь не авторизован, отправляем на страницу логина
  if (!authStore.isAuthenticated) {
    return navigateTo({
      path: '/auth/login',
      query: {
        redirect: to.fullPath,
      },
    })
  }

  // Если это админский роут, проверяем роль
  if (to.path.startsWith('/admin')) {
    // Если профиль ещё не загружен, пробуем его загрузить
    if (!userStore.user) {
      await userStore.fetchProfile()
    }

    if (!userStore.isAdmin) {
      // На клиенте показываем уведомление
      if (process.client) {
        const toast = useToast()
        toast.error('Доступ запрещен', 'У вас нет прав администратора.')
      } else {
        // Если это происходит на сервере (первичная загрузка /admin не-админом),
        // то после редиректа на '/' уведомление не покажется обычным способом.
        // Однако по заданию мы должны использовать useToast.
      }
      return navigateTo('/', { replace: true })
    }
  }
})
