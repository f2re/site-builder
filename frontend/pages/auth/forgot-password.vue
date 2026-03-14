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

const schema = zod.object({
  email: zod.string().min(1, 'Email обязателен').email('Некорректный email')
})

const { handleSubmit, errors, defineField, isSubmitting } = useForm({
  validationSchema: toTypedSchema(schema),
  initialValues: {
    email: ''
  }
})

const [email, emailProps] = defineField('email')

const onSubmit = handleSubmit(async (values) => {
  const result = await authStore.forgotPassword(values.email)
  
  if (result.success) {
    toast.success('Инструкции отправлены', 'Если email зарегистрирован, вы получите письмо для сброса пароля')
    // We don't necessarily want to redirect immediately, 
    // but maybe to a "check your email" state or back to login
    setTimeout(() => router.push('/auth/login'), 5000)
  } else {
    toast.error('Ошибка', result.error || 'Не удалось отправить запрос на сброс пароля')
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
            <h1 class="auth-title">Восстановление пароля</h1>
            <p class="auth-subtitle">Введите ваш Email, чтобы получить инструкции по сбросу пароля</p>
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
          </div>

          <div class="form-actions">
            <UButton
              type="submit"
              variant="primary"
              size="lg"
              :loading="isSubmitting"
              class="w-full btn-race"
            >
              Отправить инструкции
              <template #iconRight>
                <Icon name="ph:paper-plane-tilt-bold" size="20" />
              </template>
            </UButton>
          </div>
        </form>

        <template #footer>
          <div class="auth-footer">
            <NuxtLink to="/auth/login" class="back-link">
              <Icon name="ph:caret-left-bold" size="14" />
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
  line-height: 1.5;
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
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-sm);
  transition: all var(--transition-fast);
}

.back-link:hover {
  color: var(--color-accent);
  gap: 8px;
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
