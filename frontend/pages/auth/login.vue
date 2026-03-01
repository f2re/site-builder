<script setup lang="ts">
import { useAuthStore } from '~/stores/authStore'
import { useForm } from 'vee-validate'
import * as zod from 'zod'
import { toTypedSchema } from '@vee-validate/zod'
import { useToast } from '~/composables/useToast'

definePageMeta({
  layout: 'default'
})

const authStore = useAuthStore()
const toast = useToast()
const router = useRouter()
const config = useRuntimeConfig()

const schema = zod.object({
  email: zod.string().min(1, 'Email обязателен').email('Некорректный email'),
  password: zod.string().min(6, 'Пароль должен быть не менее 6 символов')
})

const { handleSubmit, errors, defineField, isSubmitting } = useForm({
  validationSchema: toTypedSchema(schema),
  initialValues: {
    email: '',
    password: ''
  }
})

const [email, emailProps] = defineField('email')
const [password, passwordProps] = defineField('password')

const onSubmit = handleSubmit(async (values) => {
  const result = await authStore.login(values.email, values.password)
  
  if (result.success) {
    toast.success('Успешный вход', 'Добро пожаловать обратно!')
    router.push('/profile')
  } else {
    toast.error('Ошибка входа', result.error || 'Неверный email или пароль')
  }
})

const loginWithProvider = (provider: string) => {
  const redirectUri = `${window.location.origin}/auth/callback?provider=${provider}`
  window.location.href = `${config.public.apiBase}/auth/${provider}/login?redirect_uri=${encodeURIComponent(redirectUri)}`
}

// Telegram Login Widget handler
onMounted(() => {
  // @ts-ignore
  window.onTelegramAuth = async (user: any) => {
    const result = await authStore.handleTelegramAuth(user)
    if (result.success) {
      toast.success('Успешный вход', 'Добро пожаловать через Telegram!')
      router.push('/profile')
    } else {
      toast.error('Ошибка Telegram входа', result.error)
    }
  }
})
</script>

<template>
  <div class="auth-page">
    <div class="auth-container">
      <UCard class="auth-card">
        <template #header>
          <div class="auth-header">
            <h1 class="auth-title">Вход в аккаунт</h1>
            <p class="auth-subtitle">Введите ваши данные для доступа к профилю</p>
          </div>
        </template>

        <form @submit.prevent="onSubmit" class="auth-form">
          <div class="form-group">
            <label for="email">Email</label>
            <UInput
              id="email"
              v-model="email"
              v-bind="emailProps"
              type="email"
              placeholder="example@mail.com"
              :error="errors.email"
              icon="ph:envelope-simple-bold"
            />
          </div>

          <div class="form-group">
            <div class="label-row">
              <label for="password">Пароль</label>
              <NuxtLink to="/auth/forgot-password" class="forgot-link">Забыли пароль?</NuxtLink>
            </div>
            <UInput
              id="password"
              v-model="password"
              v-bind="passwordProps"
              type="password"
              placeholder="••••••••"
              :error="errors.password"
              icon="ph:lock-simple-bold"
            />
          </div>

          <div class="form-actions">
            <UButton
              type="submit"
              variant="primary"
              size="lg"
              :loading="isSubmitting"
              class="w-full"
            >
              Войти
            </UButton>
          </div>
        </form>

        <div class="oauth-divider">
          <span>или через соцсети</span>
        </div>

        <div class="oauth-buttons">
          <button @click="loginWithProvider('google')" class="oauth-btn google">
            <Icon name="logos:google-icon" size="20" />
            <span>Google</span>
          </button>
          <button @click="loginWithProvider('yandex')" class="oauth-btn yandex">
            <Icon name="simple-icons:yandex" size="20" color="#ff0000" />
            <span>Яндекс</span>
          </button>
        </div>

        <div class="telegram-widget-container">
          <div class="tg-label">Быстрый вход:</div>
          <div id="telegram-login-container">
            <!-- This is where the Telegram widget will be, but for "Race-Style" we might prefer a custom button if we could. 
                 However, the Telegram widget is most secure. Let's use a custom button that triggers the Telegram login if possible, 
                 or just use the widget with a race-style wrapper. 
            -->
            <script 
              async 
              src="https://telegram.org/js/telegram-widget.js?22" 
              data-telegram-login="WifiOBD_Bot" 
              data-size="large" 
              data-onauth="onTelegramAuth(user)" 
              data-request-access="write"
            ></script>
          </div>
        </div>

        <template #footer>
          <div class="auth-footer">
            <p>Нет аккаунта? <NuxtLink to="/auth/register" class="register-link">Зарегистрироваться</NuxtLink></p>
          </div>
        </template>
      </UCard>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: calc(100vh - 72px - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.auth-container {
  width: 100%;
  max-width: 440px;
}

.auth-header {
  text-align: center;
}

.auth-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
  text-transform: uppercase;
  font-style: italic;
  color: var(--color-text);
}

.auth-subtitle {
  color: var(--color-text-2);
  font-size: var(--text-sm);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forgot-link {
  font-size: var(--text-xs);
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 600;
}

.forgot-link:hover {
  text-decoration: underline;
}

.form-actions {
  margin-top: 8px;
}

.w-full {
  width: 100%;
}

.oauth-divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
  color: var(--color-muted);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.oauth-divider::before,
.oauth-divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--color-border);
}

.oauth-divider span {
  padding: 0 12px;
}

.oauth-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.oauth-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border: 1px solid var(--color-border);
  background: var(--color-surface-2);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.oauth-btn:hover {
  border-color: var(--color-accent);
  background: var(--color-surface-3);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.oauth-btn:active {
  transform: translateY(0);
}

.telegram-widget-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 16px;
  background: var(--color-bg-subtle);
  border-radius: var(--radius-lg);
  border: 1px dashed var(--color-border-strong);
}

.tg-label {
  font-size: var(--text-xs);
  font-weight: 700;
  color: var(--color-text-2);
  text-transform: uppercase;
}

.auth-footer {
  text-align: center;
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.register-link {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 700;
}

.register-link:hover {
  text-decoration: underline;
}
</style>
