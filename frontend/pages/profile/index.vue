<script setup lang="ts">
import { useUser } from '~/composables/useUser'
import { useForm, useField } from 'vee-validate'
import * as zod from 'zod'
import { toTypedSchema } from '@vee-validate/zod'
import { useToast } from '~/composables/useToast'
import { onMounted, computed } from 'vue'

definePageMeta({
  middleware: 'auth'
})

useHead({
  meta: [
    { name: 'robots', content: 'noindex' }
  ]
})

const { user, pending, fetchProfile, updateProfile } = useUser()
const toast = useToast()

const schema = zod.object({
  full_name: zod.string().max(100, 'Максимум 100 символов').optional().nullable().or(zod.literal('')),
  phone: zod.string().regex(/^\+?[0-9\s-]{10,20}$/, 'Некорректный номер телефона').optional().nullable().or(zod.literal('')),
  address: zod.string().max(255, 'Максимум 255 символов').optional().nullable().or(zod.literal(''))
})

const { handleSubmit, resetForm, errors } = useForm({
  validationSchema: toTypedSchema(schema),
  initialValues: {
    full_name: '',
    phone: '',
    address: ''
  }
})

const { value: full_name } = useField<string>('full_name')
const { value: phone } = useField<string>('phone')
const { value: address } = useField<string>('address')

const isAdmin = computed(() => user.value?.role === 'admin')

onMounted(async () => {
  try {
    const data = await fetchProfile()
    if (data) {
      resetForm({
        values: {
          full_name: data.full_name || '',
          phone: data.phone || '',
          address: data.address || ''
        }
      })
    }
  } catch (err) {
    console.error('Failed to load profile:', err)
  }
})

const onSubmit = handleSubmit(async (formValues) => {
  try {
    const result = await updateProfile({
      full_name: formValues.full_name || null,
      phone: formValues.phone || null,
      address: formValues.address || null
    })
    
    // Sync form state with new values
    resetForm({
      values: {
        full_name: result.full_name || '',
        phone: result.phone || '',
        address: result.address || ''
      }
    })
    
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
            <h2 class="card-title">Личные данные</h2>
          </template>

          <div v-if="pending && !user" class="skeletons">
            <USkeleton height="40px" width="100%" class="mb-4" />
            <USkeleton height="40px" width="100%" class="mb-4" />
            <USkeleton height="40px" width="100%" class="mb-4" />
            <USkeleton height="40px" width="100%" />
          </div>

          <form v-else @submit.prevent="onSubmit" class="profile-form">
            <div class="form-group">
              <label>Email</label>
              <UInput
                :model-value="user?.email || ''"
                disabled
                icon="ph:envelope-simple-bold"
              />
              <p class="field-hint">Email нельзя изменить</p>
            </div>

            <div class="form-group">
              <label>ФИО</label>
              <UInput
                v-model="full_name"
                placeholder="Иван Иванов"
                :error="errors.full_name"
                icon="ph:user-bold"
              />
            </div>

            <div class="form-group">
              <label>Телефон</label>
              <UInput
                v-model="phone"
                placeholder="+7 (999) 000-00-00"
                :error="errors.phone"
                icon="ph:phone-bold"
              />
            </div>

            <div class="form-group">
              <label>Адрес доставки</label>
              <UInput
                v-model="address"
                placeholder="г. Москва, ул. Ленина, д. 1"
                :error="errors.address"
                icon="ph:map-pin-bold"
              />
            </div>

            <div class="form-actions">
              <UButton
                type="submit"
                :loading="pending"
                variant="primary"
                class="btn-save"
              >
                <template #icon>
                  <Icon name="ph:check-bold" size="20" />
                </template>
                Сохранить изменения
              </UButton>
            </div>
          </form>
        </UCard>

        <!-- Admin Only Section -->
        <UCard v-if="isAdmin" class="account-info">
          <template #header>
            <h2 class="card-title">Техническая информация (Admin)</h2>
          </template>
          <div class="info-list">
            <div class="info-item">
              <span class="label">Роль:</span>
              <UBadge variant="accent">
                {{ user?.role }}
              </UBadge>
            </div>
            <div class="info-item">
              <span class="label">Статус:</span>
              <UBadge :variant="user?.is_active ? 'success' : 'error'">
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

.btn-save {
  width: auto;
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

.mb-4 {
  margin-bottom: 1rem;
}

@media (max-width: 1024px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .btn-save {
    width: 100%;
  }
}
</style>
