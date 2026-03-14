<script setup lang="ts">
import { useIoT } from '~/composables/useIoT'
import { useForm } from 'vee-validate'
import * as zod from 'zod'
import { toTypedSchema } from '@vee-validate/zod'

definePageMeta({
  middleware: 'auth'
})

useHead({
  meta: [
    { name: 'robots', content: 'noindex' }
  ]
})

const { devices, pending, fetchDevices, registerDevice, formatDeviceModel } = useIoT()
const toast = useToast()

const schema = zod.object({
  device_uid: zod.string().min(5, 'UID должен быть не короче 5 символов').max(50, 'UID слишком длинный'),
  name: zod.string().min(2, 'Имя устройства не короче 2 символов').max(50, 'Имя слишком длинное').nullable().optional(),
  model: zod.enum(['wifi_obd2', 'wifi_obd2_advanced'], {
    errorMap: () => ({ message: 'Выберите модель из списка' })
  })
})

const { handleSubmit, resetForm, errors, defineField } = useForm({
  validationSchema: toTypedSchema(schema),
  initialValues: {
    model: 'wifi_obd2'
  }
})

const [device_uid, device_uidProps] = defineField('device_uid')
const [name, nameProps] = defineField('name')
const [model, modelProps] = defineField('model')

const availableModels = [
  { label: 'Wifi OBD2', value: 'wifi_obd2' },
  { label: 'Wifi OBD2 Advanced', value: 'wifi_obd2_advanced' }
]

const showAddForm = ref(false)

onMounted(async () => {
  try {
    await fetchDevices()
  } catch (err) {
    console.error(err)
  }
})

const onSubmit = handleSubmit(async (values) => {
  try {
    await registerDevice(values)
    toast.success('Устройство добавлено', 'Новое устройство успешно зарегистрировано')
    showAddForm.value = false
    resetForm()
  } catch (err: any) {
    const detail = err?.data?.detail || 'Не удалось добавить устройство'
    toast.error('Ошибка регистрации', detail)
  }
})
</script>

<template>
  <div class="devices-page">
    <div class="container">
      <h1 class="page-title">Мои устройства</h1>
      <ProfileNav />

      <div class="devices-header">
        <h2 class="section-title">Список подключенных устройств</h2>
        <UButton
          v-if="!showAddForm"
          variant="secondary"
          icon="ph:plus-bold"
          @click="showAddForm = true"
        >
          Добавить новое
        </UButton>
      </div>

      <Transition name="fade-slide">
        <UCard v-if="showAddForm" class="add-device-card">
          <template #header>
            <div class="card-header">
              <h3 class="card-title">Регистрация устройства</h3>
              <UButton
                variant="ghost"
                icon="ph:x-bold"
                size="sm"
                @click="showAddForm = false"
              />
            </div>
          </template>

          <form @submit.prevent="onSubmit" class="device-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Device UID (S/N)</label>
                <UInput
                  v-model="device_uid"
                  v-bind="device_uidProps"
                  placeholder="UID вашего устройства"
                  :error="errors.device_uid"
                  icon="ph:barcode-bold"
                />
              </div>

              <div class="form-group">
                <label>Название</label>
                <UInput
                  v-model="name"
                  v-bind="nameProps"
                  placeholder="Например: Моя машина"
                  :error="errors.name"
                  icon="ph:identification-card-bold"
                />
              </div>

              <div class="form-group">
                <label>Модель</label>
                <USelect
                  v-model="model"
                  v-bind="modelProps"
                  :options="availableModels"
                  :error="errors.model"
                  icon="ph:package-bold"
                />
              </div>
            </div>

            <div class="form-actions">
              <UButton
                type="submit"
                :loading="pending"
                variant="primary"
                icon="ph:check-bold"
              >
                Зарегистрировать
              </UButton>
            </div>
          </form>
        </UCard>
      </Transition>

      <div class="devices-list">
        <div v-if="pending && devices.length === 0" class="skeletons">
          <USkeleton v-for="i in 3" :key="i" height="120px" width="100%" radius="var(--radius-lg)" />
        </div>

        <div v-else-if="devices.length === 0" class="empty-state">
          <div class="empty-icon">
            <Icon name="ph:cpu-bold" size="48" />
          </div>
          <h3>Нет подключенных устройств</h3>
          <p>Зарегистрируйте ваше первое IoT-устройство, чтобы отслеживать телеметрию в реальном времени.</p>
          <UButton variant="primary" icon="ph:plus-bold" @click="showAddForm = true">
            Добавить устройство
          </UButton>
        </div>

        <div v-else class="devices-grid">
          <NuxtLink
            v-for="device in devices"
            :key="device.id"
            :to="`/profile/devices/${device.id}`"
            class="device-card-link"
          >
            <UCard class="device-card">
              <div class="device-info">
                <div class="device-icon" :class="{ online: device.is_active }">
                  <Icon name="ph:broadcast-bold" size="24" />
                </div>
                <div class="device-details">
                  <h4 class="device-name">{{ device.name || 'Безымянное устройство' }}</h4>
                  <p class="device-model">{{ formatDeviceModel(device.model) }}</p>
                  <code class="device-uid">{{ device.device_uid }}</code>
                </div>
              </div>
              
              <div class="device-status">
                <UBadge :variant="device.is_active ? 'success' : 'secondary'">
                  {{ device.is_active ? 'Online' : 'Offline' }}
                </UBadge>
                <span class="last-seen" v-if="device.last_seen_at">
                  {{ new Date(device.last_seen_at).toLocaleString() }}
                </span>
              </div>

              <div class="card-action">
                <Icon name="ph:arrow-right-bold" size="20" />
              </div>
            </UCard>
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.devices-page {
  padding: 40px 0;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 24px;
}

.devices-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-size: var(--text-lg);
  font-weight: 700;
  margin: 0;
}

.add-device-card {
  margin-bottom: 32px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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

.devices-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeletons {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: var(--color-surface);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-xl);
}

.empty-icon {
  width: 80px;
  height: 80px;
  background: var(--color-bg-subtle);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  color: var(--color-muted);
}

.empty-state h3 {
  font-size: var(--text-xl);
  font-weight: 700;
  margin-bottom: 12px;
}

.empty-state p {
  color: var(--color-text-2);
  margin-bottom: 24px;
  max-width: 400px;
  margin-inline: auto;
}

.devices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

.device-card-link {
  text-decoration: none;
  display: block;
}

.device-card {
  position: relative;
  transition: all var(--transition-normal);
  padding: 24px;
}

.device-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
  transform: translateY(-2px);
}

.device-info {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.device-icon {
  width: 56px;
  height: 56px;
  background: var(--color-surface-2);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-muted);
  transition: all var(--transition-normal);
}

.device-icon.online {
  color: var(--color-neon);
  box-shadow: var(--shadow-glow-neon);
  background: rgba(0, 245, 212, 0.05);
}

.device-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.device-name {
  font-size: var(--text-base);
  font-weight: 700;
  margin: 0;
  color: var(--color-text);
}

.device-model {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin: 0;
}

.device-uid {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--color-muted);
  margin-top: 4px;
}

.device-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.last-seen {
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.card-action {
  position: absolute;
  right: 20px;
  bottom: 20px;
  color: var(--color-muted);
  transition: all var(--transition-fast);
}

.device-card:hover .card-action {
  color: var(--color-accent);
  transform: translateX(4px);
}

@media (max-width: 768px) {
  .devices-grid {
    grid-template-columns: 1fr;
  }
}
</style>
