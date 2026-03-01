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
  name: zod.string().min(2, 'Имя должно быть не менее 2 символов'),
  email: zod.string().min(1, 'Email обязателен').email('Некорректный email'),
  password: zod.string().min(6, 'Пароль должен быть не менее 6 символов'),
  confirmPassword: zod.string().min(6, 'Подтверждение пароля обязательно')
}).refine((data) => data.password === data.confirmPassword, {
  message: "Пароли не совпадают",
  path: ["confirmPassword"],
})

const { handleSubmit, errors, defineField, isSubmitting } = useForm({
  validationSchema: toTypedSchema(schema),
  initialValues: {
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  }
})

const [name, nameProps] = defineField('name')
const [email, emailProps] = defineField('email')
const [password, passwordProps] = defineField('password')
const [confirmPassword, confirmPasswordProps] = defineField('confirmPassword')

const onSubmit = handleSubmit(async (values) => {
  const result = await authStore.register(values.name, values.email, values.password)
  
  if (result.success) {
    toast.success('Регистрация успешна', 'Теперь вы можете войти в свой аккаунт')
    router.push('/auth/login')
  } else {
    toast.error('Ошибка регистрации', result.error || 'Произошла непредвиденная ошибка')
  }
})
</script>

<template>
  <div class="auth-page">
    <div class="auth-container">
      <UCard class="auth-card">
        <template #header>
          <div class="auth-header">
            <h1 class="auth-title">Создание аккаунта</h1>
            <p class="auth-subtitle">Зарегистрируйтесь, чтобы получить доступ ко всем функциям</p>
          </div>
        </template>

        <form @submit.prevent="onSubmit" class="auth-form">
          <div class="form-group">
            <label for="name">Имя</label>
            <UInput
              id="name"
              v-model="name"
              v-bind="nameProps"
              placeholder="Ваше имя"
              :error="errors.name"
              icon="ph:user-bold"
            />
          </div>

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
            <label for="password">Пароль</label>
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

          <div class="form-group">
            <label for="confirmPassword">Подтверждение пароля</label>
            <UInput
              id="confirmPassword"
              v-model="confirmPassword"
              v-bind="confirmPasswordProps"
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
              class="w-full"
            >
              Зарегистрироваться
            </UButton>
          </div>
        </form>

        <template #footer>
          <div class="auth-footer">
            <p>Уже есть аккаунт? <NuxtLink to="/auth/login" class="login-link">Войти</NuxtLink></p>
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

.login-link {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 700;
}

.login-link:hover {
  text-decoration: underline;
}
</style>
