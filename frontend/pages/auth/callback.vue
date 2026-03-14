<script setup lang="ts">
import { useAuthStore } from '~/stores/authStore'
import { useToast } from '~/composables/useToast'

definePageMeta({
  layout: 'auth'
})

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const processing = ref(true)

onMounted(async () => {
  const { code, provider } = route.query
  
  if (!code || !provider) {
    toast.error('Ошибка входа', 'Неверные параметры callback')
    router.push('/auth/login')
    return
  }

  const redirectUri = `${window.location.origin}/auth/callback?provider=${provider}`
  
  const result = await authStore.handleOAuthCallback(
    provider as string, 
    code as string, 
    redirectUri
  )

  if (result.success) {
    toast.success('Вход выполнен', 'Добро пожаловать!')
    router.push('/profile')
  } else {
    toast.error('Ошибка входа', result.error || 'Не удалось авторизоваться через провайдера')
    router.push('/auth/login')
  }
  
  processing.value = false
})
</script>

<template>
  <div class="callback-page">
    <div class="loading-container">
      <div class="loader">
        <div class="loader-wheel"></div>
        <div class="loader-text">Авторизация...</div>
      </div>
      <p class="speed-label">СИНХРОНИЗАЦИЯ АККАУНТА</p>
    </div>
  </div>
</template>

<style scoped>
.callback-page {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.loader {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loader-wheel {
  width: 64px;
  height: 64px;
  border: 4px solid var(--color-surface-2);
  border-top: 4px solid var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.loader-text {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.01em;
}

.speed-label {
  font-size: var(--text-xs);
  font-weight: 800;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.2em;
  padding: 4px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
