<script setup lang="ts">
import type { Device } from '~/stores/firmwareStore'

interface Props {
  device: Device
}

const props = defineProps<Props>()

const { fetchVersions, downloadFirmware } = useFirmware()
const { versions } = storeToRefs(useFirmwareStore())
const toast = useToast()

const selectedVersionId = ref<string>('')
const isPending = ref(false)
const isDownloading = ref(false)

const deviceVersions = computed(() => versions.value[props.device.type] || [])

const versionOptions = computed(() => 
  deviceVersions.value.map(v => ({
    label: v.version,
    value: v.id
  }))
)

onMounted(async () => {
  if (deviceVersions.value.length === 0) {
    isPending.value = true
    try {
      await fetchVersions(props.device.type)
    } finally {
      isPending.value = false
    }
  }
})

const handleDownload = async () => {
  if (!selectedVersionId.value) {
    toast.error({ title: 'Выберите версию', message: 'Необходимо выбрать версию прошивки для загрузки' })
    return
  }

  isDownloading.value = true
  try {
    const response = await downloadFirmware(props.device.id, selectedVersionId.value, [])
    if (response?.url) {
      window.open(response.url, '_blank')
      toast.success({ title: 'Загрузка началась', message: 'Файл прошивки успешно подготовлен' })
    } else {
      throw new Error('No download URL returned')
    }
  } catch (err) {
    toast.error({ 
      title: 'Ошибка загрузки', 
      message: 'Не удалось получить ссылку на прошику. Попробуйте позже.',
      action: { label: 'Повторить', handler: handleDownload }
    })
  } finally {
    isDownloading.value = false
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<template>
  <UCard class="device-card">
    <template #header>
      <div class="device-header">
        <div class="device-info">
          <UBadge :variant="device.type === 'OBD' ? 'accent' : 'neon'" size="sm" class="device-type">
            {{ device.type }}
          </UBadge>
          <h3 class="device-serial">{{ device.serial }}</h3>
        </div>
        <div class="device-date">
          Добавлен: {{ formatDate(device.added_at) }}
        </div>
      </div>
    </template>

    <div class="device-body">
      <div class="device-icon">
        <Icon :name="device.type === 'OBD' ? 'ph:cpu-bold' : 'ph:gauge-bold'" size="48" />
      </div>
      
      <div class="device-actions">
        <USelect
          v-model="selectedVersionId"
          :options="versionOptions"
          label="Версия прошивки"
          placeholder="Выберите версию..."
          :disabled="isPending || isDownloading"
        />
        
        <UButton
          class="download-btn"
          :loading="isDownloading"
          :disabled="!selectedVersionId"
          @click="handleDownload"
        >
          <template #icon>
            <Icon name="ph:download-simple-bold" size="20" />
          </template>
          Скачать прошивку
        </UButton>
      </div>
    </div>
  </UCard>
</template>

<style scoped>
.device-card {
  height: 100%;
}

.device-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.device-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.device-serial {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 700;
  letter-spacing: 0.02em;
  font-family: var(--font-mono);
}

.device-date {
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.device-body {
  display: flex;
  align-items: center;
  gap: 24px;
}

.device-icon {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-subtle);
  border-radius: var(--radius-lg);
  color: var(--color-accent);
}

.device-actions {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.download-btn {
  width: 100%;
}

@media (max-width: 640px) {
  .device-body {
    flex-direction: column;
    text-align: center;
  }
  
  .device-icon {
    width: 64px;
    height: 64px;
  }
  
  .device-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
