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
  const botName = config.public.telegramBotName
  const isDefault = botName === 'WifiOBD_Bot'
  console.log('[DEBUG] Login Page - Telegram Bot Name from RuntimeConfig:', botName, isDefault ? '(using default)' : '(overridden)')
  
  if (isDefault) {
    console.warn('[DEBUG] Warning: Telegram Bot Name is using default "WifiOBD_Bot". If this is not intended, set NUXT_PUBLIC_TELEGRAM_BOT_NAME in .env')
  }
  
  // Define callback on window
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

  // Dynamically load Telegram widget
  const script = document.createElement('script')
  script.src = 'https://telegram.org/js/telegram-widget.js?22'
  script.async = true
  script.setAttribute('data-telegram-login', botName)
  script.setAttribute('data-size', 'large')
  script.setAttribute('data-onauth', 'onTelegramAuth(user)')
  script.setAttribute('data-request-access', 'write')
  
  const container = document.getElementById('telegram-login-container')
  if (container) {
    container.innerHTML = '' // Clear placeholder if any script already exists
    container.appendChild(script)
  }
})

onUnmounted(() => {
  // @ts-ignore
  delete window.onTelegramAuth
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
            <h1 class="auth-title">Вход в аккаунт</h1>
            <p class="auth-subtitle">Вернитесь к управлению вашим автопарком</p>
          </div>
        </template>

        <form @submit.prevent="onSubmit" class="auth-form">
          <div class="form-grid">
            <UInput
              id="email"
              v-model="email"
              v-bind="emailProps"
              label="Email"
              type="email"
              placeholder="example@mail.com"
              :error="errors.email"
              icon="ph:envelope-simple-bold"
            />

            <div class="password-field">
              <UInput
                id="password"
                v-model="password"
                v-bind="passwordProps"
                label="Пароль"
                type="password"
                placeholder="••••••••"
                :error="errors.password"
                icon="ph:lock-simple-bold"
              />
              <NuxtLink to="/auth/forgot-password" class="forgot-link">
                Забыли пароль?
              </NuxtLink>
            </div>
          </div>

          <div class="form-actions">
            <UButton
              type="submit"
              variant="primary"
              size="lg"
              :loading="isSubmitting"
              class="w-full btn-race"
            >
              Войти в систему
              <template #iconRight>
                <Icon name="ph:arrow-right-bold" size="20" />
              </template>
            </UButton>
          </div>
        </form>

        <div class="oauth-divider">
          <span>или через соцсети</span>
        </div>

        <div class="oauth-grid">
          <button @click="loginWithProvider('google')" class="oauth-btn oauth-btn--google" aria-label="Войти через Google">
            <Icon name="logos:google-icon" size="20" />
            <span>Google</span>
          </button>
          <button @click="loginWithProvider('yandex')" class="oauth-btn oauth-btn--yandex" aria-label="Войти через Яндекс">
            <Icon name="simple-icons:yandex" size="20" style="color: #fc3f1d" />
            <span>Яндекс</span>
          </button>
        </div>

        <div class="telegram-section">
          <div id="telegram-login-container" class="tg-wrapper">
            <div class="tg-placeholder">
               <Icon name="logos:telegram" size="24" class="tg-icon" />
               <span>Вход через Telegram...</span>
            </div>
          </div>
        </div>

        <template #footer>
          <div class="auth-footer">
            <span>Ещё нет аккаунта?</span>
            <NuxtLink to="/auth/register" class="register-link">
              Присоединяйтесь к нам
              <Icon name="ph:caret-right-bold" size="14" />
            </NuxtLink>
          </div>
        </template>
      </UCard>
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

.password-field {
  position: relative;
  display: flex;
  flex-direction: column;
}

.forgot-link {
  align-self: flex-end;
  font-size: var(--text-xs);
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 600;
  margin-top: 6px;
  transition: color var(--transition-fast);
}

.forgot-link:hover {
  color: var(--color-accent-hover);
}

.w-full { width: 100%; }

.btn-race {
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 800;
}

.oauth-divider {
  display: flex;
  align-items: center;
  margin: 32px 0 24px;
  color: var(--color-muted);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-weight: 700;
}

.oauth-divider::before,
.oauth-divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--color-border);
}

.oauth-divider span {
  padding: 0 16px;
}

.oauth-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.oauth-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px;
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

.oauth-btn--yandex {
  color: #000;
  background: #fff;
}
[data-theme="dark"] .oauth-btn--yandex {
  background: #f0f0f5;
}

.telegram-section {
  display: flex;
  justify-content: center;
  padding: 24px;
  background: var(--color-surface-2);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  position: relative;
  overflow: hidden;
  margin-top: 12px;
}

.telegram-section::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: #24A1DE;
}

.tg-wrapper {
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.tg-placeholder {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--color-text-2);
  font-size: var(--text-sm);
  font-weight: 500;
  animation: pulse 2s infinite ease-in-out;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.tg-icon {
  color: #24A1DE;
}

.auth-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-size: var(--text-sm);
}

.auth-footer span {
  color: var(--color-text-2);
}

.register-link {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all var(--transition-fast);
}

.register-link:hover {
  color: var(--color-accent-hover);
  gap: 6px;
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
