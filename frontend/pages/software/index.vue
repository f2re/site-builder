<script setup lang="ts">
import DeviceCard from '~/components/shop/DeviceCard.vue'

definePageMeta({
  middleware: 'auth'
})

const { fetchMyDevices, addDevice, fetchToken } = useFirmware()
const { devices, token } = storeToRefs(useFirmwareStore())
const toast = useToast()

const serialToAdd = ref('')
const isAddingDevice = ref(false)
const isFetchingToken = ref(false)
const isInitialLoading = ref(true)

const onAddDevice = async () => {
  if (!serialToAdd.value) return
  
  isAddingDevice.value = true
  try {
    await addDevice(serialToAdd.value)
    serialToAdd.value = ''
    toast.success({ title: 'Устройство добавлено', message: 'Новое устройство успешно привязано к вашей учетной записи' })
  } catch (err) {
    toast.error({ title: 'Ошибка при добавлении', message: 'Не удалось добавить устройство. Проверьте серийный номер.' })
  } finally {
    isAddingDevice.value = false
  }
}

const onGetToken = async () => {
  isFetchingToken.value = true
  try {
    await fetchToken()
    toast.success({ title: 'Токен обновлен', message: 'Токен для программы успешно получен' })
  } catch (err) {
    toast.error({ title: 'Ошибка получения токена', message: 'Не удалось получить токен.' })
  } finally {
    isFetchingToken.value = false
  }
}

const copyToken = () => {
  if (!token.value) return
  navigator.clipboard.writeText(token.value)
  toast.success({ title: 'Скопировано', message: 'Токен скопирован в буфер обмена' })
}

onMounted(async () => {
  try {
    await fetchMyDevices()
  } finally {
    isInitialLoading.value = false
  }
})

useSeo({
  title: 'Программное обеспечение',
  description: 'Управление устройствами и загрузка прошивок'
})
</script>

<template>
  <main class="software-page">
    <div class="container">
      <header class="page-header">
        <h1 class="page-title">Мои устройства</h1>
        <p class="page-description">Управляйте вашими OBD-адаптерами и скачивайте последние версии прошивок.</p>
      </header>

      <div class="dashboard-grid">
        <!-- Sidebar: Token & Add Device -->
        <aside class="dashboard-sidebar">
          <UCard class="token-card">
            <template #header>
              <h3 class="card-title">Программный доступ</h3>
            </template>
            <p class="token-help">Используйте этот токен в настольном приложении для автоматической авторизации.</p>
            
            <div v-if="token" class="token-display">
              <code>{{ token }}</code>
              <UButton variant="ghost" size="sm" @click="copyToken">
                <Icon name="ph:copy-bold" />
              </UButton>
            </div>
            
            <UButton 
              block 
              :variant="token ? 'secondary' : 'primary'"
              :loading="isFetchingToken"
              @click="onGetToken"
            >
              {{ token ? 'Обновить токен' : 'Получить токен' }}
            </UButton>
          </UCard>

          <UCard class="add-device-card">
            <template #header>
              <h3 class="card-title">Добавить устройство</h3>
            </template>
            <form @submit.prevent="onAddDevice" class="add-device-form">
              <UInput
                v-model="serialToAdd"
                label="Серийный номер"
                placeholder="Например: OBD123456"
                :disabled="isAddingDevice"
              />
              <UButton 
                type="submit" 
                block 
                :loading="isAddingDevice"
                :disabled="!serialToAdd"
              >
                <template #icon>
                  <Icon name="ph:plus-bold" />
                </template>
                Привязать
              </UButton>
            </form>
          </UCard>
        </aside>

        <!-- Main Content: Device List -->
        <section class="device-list-section">
          <div v-if="isInitialLoading" class="device-grid">
            <USkeleton v-for="i in 2" :key="i" height="240px" />
          </div>

          <div v-else-if="devices.length > 0" class="device-grid">
            <TransitionGroup name="list">
              <div v-for="device in devices" :key="device.id">
                <DeviceCard :device="device" />
              </div>
            </TransitionGroup>
          </div>

          <div v-else class="empty-state">
            <div class="empty-icon">
              <Icon name="ph:cpu-light" size="64" />
            </div>
            <h3>Нет привязанных устройств</h3>
            <p>Добавьте серийный номер вашего устройства в форме слева, чтобы получить доступ к прошивкам.</p>
          </div>
        </section>
      </div>
    </div>
  </main>
</template>

<style scoped>
.software-page {
  padding: 40px 0;
  min-height: calc(100vh - 200px);
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  margin-bottom: 40px;
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: 800;
  margin-bottom: 8px;
  background: linear-gradient(135deg, var(--color-text) 0%, var(--color-muted) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-description {
  color: var(--color-text-2);
  font-size: var(--text-lg);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 32px;
  align-items: start;
}

.dashboard-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: sticky;
  top: 100px;
}

.card-title {
  margin: 0;
  font-size: var(--text-base);
  font-weight: 700;
}

.token-help {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin-bottom: 16px;
}

.token-display {
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.token-display code {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-neon);
  word-break: break-all;
}

.add-device-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.device-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 40px;
  background: var(--color-surface);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-lg);
  text-align: center;
}

.empty-icon {
  color: var(--color-muted);
  margin-bottom: 24px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: var(--text-xl);
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--color-text-2);
  max-width: 400px;
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-sidebar {
    position: static;
    order: 2;
  }
  
  .device-list-section {
    order: 1;
  }
}

@media (max-width: 640px) {
  .page-title {
    font-size: var(--text-2xl);
  }
}
</style>
