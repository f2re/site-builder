<script setup lang="ts">
import { useAuthStore } from '~/stores/authStore'
import { useForm } from 'vee-validate'
import * as zod from 'zod'
import { toTypedSchema } from '@vee-validate/zod'
import { useToast } from '~/composables/useToast'

definePageMeta({
  layout: 'auth'
})

const authStore = useAuthStore()
const toast = useToast()
const router = useRouter()
const route = useRoute()

const token = computed(() => (route.query.token as string) || '')

const schema = zod.object({
  password: zod.string().min(8, 'Пароль должен быть не менее 8 символов'),
  confirmPassword: zod.string().min(8, 'Подтвердите пароль')
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Пароли не совпадают',
  path: ['confirmPassword']
})

const { handleSubmit, errors, defineField, isSubmitting } = useForm({
  validationSchema: toTypedSchema(schema),
  initialValues: {
    password: '',
    confirmPassword: ''
  }
})

const [password, passwordProps] = defineField('password')
const [confirmPassword, confirmPasswordProps] = defineField('confirmPassword')

const onSubmit = handleSubmit(async (values) => {
  if (!token.value) {
    toast.error('Ошибка', 'Токен сброса пароля отсутствует или недействителен')
    return
  }

  const result = await authStore.resetPassword(token.value, values.password)
  
  if (result.success) {
    toast.success('Пароль изменен', 'Теперь вы можете войти с новым паролем')
    router.push('/auth/login')
  } else {
    toast.error('Ошибка', result.error || 'Не удалось сбросить пароль')
  }
})

onMounted(() => {
  if (!route.query.token) {
    toast.warning('Внимание', 'Токен сброса пароля не найден в URL')
  }
})
</script>

<template>
  <div class="auth-page">
    <!-- Background Decoration -->
    <div class="auth-bg-decor">
      <div class="auth-bg-blob auth-bg-blob--1"></div>
      <div class="auth-bg-blob auth-bg-blob--2"></div>
    </div>

    <div class="auth-container">
      <div class="auth-logo-section">
        <NuxtLink to="/" class="auth-logo">
          <span class="logo-text">Wifi<span class="logo-accent">OBD</span></span>
        </NuxtLink>
      </div>

      <UCard class="auth-card">
        <template #header>
          <div class="auth-header">
            <h1 class="auth-title">Новый пароль</h1>
            <p class="auth-subtitle">Установите надежный пароль для вашего аккаунта</p>
          </div>
        </template>

        <form @submit.prevent="onSubmit" class="auth-form">
          <div class="form-grid">
            <UInput
              id="password"
              v-model="password"
              v-bind="passwordProps"
              label="Новый пароль"
              type="password"
              placeholder="••••••••"
              :error="errors.password"
              icon="ph:lock-simple-bold"
            />

            <UInput
              id="confirmPassword"
              v-model="confirmPassword"
              v-bind="confirmPasswordProps"
              label="Подтвердите пароль"
              type="password"
              placeholder="••••••••"
              :error="errors.confirmPassword"
              icon="ph:lock-simple-bold"
            />
          </div>

          <div class="form-actions">
            <UButton
              type="submit"
              variant="primary"
              size="lg"
              :loading="isSubmitting"
              :disabled="!token"
              class="w-full btn-race"
            >
              Сбросить пароль
              <template #iconRight>
                <Icon name="ph:check-bold" size="20" />
              </template>
            </UButton>
          </div>
        </form>

        <template #footer>
          <div class="auth-footer">
            <NuxtLink to="/auth/login" class="back-link">
              Вернуться ко входу
            </NuxtLink>
          </div>
        </template>
      </UCard>
      
      <div class="auth-page-footer">
        <p>© {{ new Date().getFullYear() }} WifiOBD. Все права защищены.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background-color: var(--color-bg);
  position: relative;
  overflow: hidden;
}

/* Background Blobs */
.auth-bg-decor {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.auth-bg-blob {
  position: absolute;
  filter: blur(80px);
  opacity: 0.15;
  border-radius: var(--radius-full);
}

.auth-bg-blob--1 {
  width: 400px;
  height: 400px;
  background: var(--color-accent);
  top: -100px;
  right: -100px;
}

.auth-bg-blob--2 {
  width: 300px;
  height: 300px;
  background: var(--color-neon);
  bottom: -50px;
  left: -50px;
}

.auth-container {
  width: 100%;
  max-width: 460px;
  position: relative;
  z-index: 1;
}

.auth-logo-section {
  text-align: center;
  margin-bottom: 32px;
}

.auth-logo {
  text-decoration: none;
  display: inline-flex;
}

.logo-text {
  font-size: var(--text-3xl);
  font-weight: 900;
  color: var(--color-text);
  letter-spacing: -0.04em;
  font-style: italic;
  text-transform: uppercase;
}

.logo-accent {
  color: var(--color-accent);
}

.auth-card {
  box-shadow: var(--shadow-modal);
  background-color: var(--color-surface);
}

.auth-header {
  text-align: center;
}

.auth-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
  color: var(--color-text);
}

.auth-subtitle {
  color: var(--color-text-2);
  font-size: var(--text-sm);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.w-full { width: 100%; }

.btn-race {
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-style: italic;
}

.auth-footer {
  display: flex;
  justify-content: center;
}

.back-link {
  color: var(--color-text-2);
  text-decoration: none;
  font-weight: 600;
  font-size: var(--text-sm);
  transition: color var(--transition-fast);
}

.back-link:hover {
  color: var(--color-accent);
}

.auth-page-footer {
  margin-top: 32px;
  text-align: center;
  font-size: var(--text-xs);
  color: var(--color-muted);
}

/* Mobile-First Adjustments */
@media (max-width: 480px) {
  .auth-page {
    padding: 20px 16px;
  }
  
  .auth-logo-section {
    margin-bottom: 24px;
  }
  
  .auth-title {
    font-size: var(--text-xl);
  }
}
</style>
