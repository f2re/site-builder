<script setup lang="ts">
import { useUser } from '~/composables/useUser'
import { useForm } from 'vee-validate'
import * as zod from 'zod'
import { toTypedSchema } from '@vee-validate/zod'

definePageMeta({
  middleware: 'auth'
})

const { user, pending, error, fetchProfile, updateProfile } = useUser()
const toast = useToast()

const schema = zod.object({
  full_name: zod.string().min(2, 'Минимум 2 символа').max(100, 'Максимум 100 символов').nullable()
})

const { handleSubmit, resetForm, errors, defineField } = useForm({
  validationSchema: toTypedSchema(schema),
  initialValues: {
    full_name: ''
  }
})

const [full_name, full_nameProps] = defineField('full_name')

onMounted(async () => {
  try {
    const data = await fetchProfile()
    resetForm({
      values: {
        full_name: data.full_name || ''
      }
    })
  } catch (err) {
    console.error(err)
  }
})

const onSubmit = handleSubmit(async (values) => {
  try {
    await updateProfile(values)
    toast.success('Профиль обновлен', 'Ваши данные успешно сохранены')
  } catch (err) {
    toast.error('Ошибка обновления', 'Не удалось сохранить изменения')
  }
})
</script>

<template>
  <div class="profile-page">
    <div class="container">
      <h1 class="page-title">Личный кабинет</h1>
      <ProfileNav />

      <div class="profile-grid">
        <UCard class="profile-card">
          <template #header>
            <h2 class="card-title">Основные данные</h2>
          </template>

          <div v-if="pending && !user" class="skeletons">
            <USkeleton height="40px" width="100%" />
            <USkeleton height="40px" width="100%" />
            <USkeleton height="40px" width="100%" />
          </div>

          <form v-else @submit.prevent="onSubmit" class="profile-form">
            <div class="form-group">
              <label>Email</label>
              <UInput
                :model-value="user?.email"
                disabled
                icon="ph:envelope-simple-bold"
              />
              <p class="field-hint">Email нельзя изменить</p>
            </div>

            <div class="form-group">
              <label>Полное имя</label>
              <UInput
                v-model="full_name"
                v-bind="full_nameProps"
                placeholder="Введите ваше имя"
                :error="errors.full_name"
                icon="ph:user-bold"
              />
            </div>

            <div class="form-actions">
              <UButton
                type="submit"
                :loading="pending"
                variant="primary"
                icon="ph:check-bold"
              >
                Сохранить изменения
              </UButton>
            </div>
          </form>
        </UCard>

        <UCard class="account-info">
          <template #header>
            <h2 class="card-title">Статус аккаунта</h2>
          </template>
          <div class="info-list">
            <div class="info-item">
              <span class="label">Роль:</span>
              <UBadge :variant="user?.role === 'admin' ? 'danger' : 'secondary'">
                {{ user?.role }}
              </UBadge>
            </div>
            <div class="info-item">
              <span class="label">Статус:</span>
              <UBadge :variant="user?.is_active ? 'success' : 'danger'">
                {{ user?.is_active ? 'Активен' : 'Заблокирован' }}
              </UBadge>
            </div>
            <div class="info-item">
              <span class="label">ID:</span>
              <code class="user-id">{{ user?.id }}</code>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  padding: 40px 0;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 24px;
  letter-spacing: -0.02em;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 24px;
  align-items: start;
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 700;
  margin: 0;
}

.profile-form {
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

.field-hint {
  font-size: var(--text-xs);
  color: var(--color-muted);
  margin-top: 4px;
}

.form-actions {
  margin-top: 12px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-item .label {
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.user-id {
  font-family: var(--font-mono);
  font-size: 10px;
  background: var(--color-surface-2);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  color: var(--color-muted);
}

@media (max-width: 1024px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>
