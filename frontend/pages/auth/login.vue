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
  min-height: calc(100vh - 72px - 200px); /* Adjust based on header/footer */
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
}

.auth-subtitle {
  color: var(--color-text-2);
  font-size: var(--text-sm);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
