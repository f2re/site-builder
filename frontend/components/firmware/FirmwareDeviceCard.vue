<script setup lang="ts">
import type { DeviceRead, Complectation, VersionInfo } from '~/stores/firmwareStore'

interface Props {
  device: DeviceRead
  publicToken?: string
  isAuth?: boolean
}

interface DownloadPayload {
  device: DeviceRead
  version: string
  selectedIds: string[]
}

interface TogglePayload {
  serial: string
  complectationId: string
}

const props = withDefaults(defineProps<Props>(), {
  publicToken: '',
  isAuth: false,
})

const emit = defineEmits<{
  (e: 'download', payload: DownloadPayload): void
  (e: 'toggle-complectation', payload: TogglePayload): void
}>()

const { fetchVersionsByToken, fetchVersionInfo } = useFirmware()
const toast = useToast()

const selectedVersion = ref<string>('')
const versionInfo = ref<VersionInfo | null>(null)
const selectedComplectationIds = ref<Set<string>>(new Set())
const versions = ref<string[]>([])
const isDownloading = ref(false)
const isLoadingVersionInfo = ref(false)
const isLoadingVersions = ref(false)

// Computed
const simpleComplectations = computed<Complectation[]>(
  () => props.device.complectations.filter((c) => c.simple)
)

const deviceTypeIcon = computed(() =>
  props.device.device_type === 'OBD' ? 'ph:cpu-bold' : 'ph:broadcast-bold'
)

// Init: pre-select base complectations (simple=true)
onMounted(async () => {
  // Pre-select all simple complectations
  props.device.complectations
    .filter((c) => c.simple)
    .forEach((c) => selectedComplectationIds.value.add(c.id))

  await loadVersions()
})

async function loadVersions() {
  if (isLoadingVersions.value) return
  isLoadingVersions.value = true
  try {
    const token = props.publicToken || ''
    versions.value = await fetchVersionsByToken(token, props.device.device_type)
    // Auto-select the first version if available
    if (versions.value.length > 0 && !selectedVersion.value) {
      selectedVersion.value = versions.value[0]
      await loadVersionInfo()
    }
  } catch {
    // Silently fail — user will see empty select
  } finally {
    isLoadingVersions.value = false
  }
}

async function loadVersionInfo() {
  if (!selectedVersion.value) {
    versionInfo.value = null
    return
  }
  isLoadingVersionInfo.value = true
  try {
    versionInfo.value = await fetchVersionInfo(
      selectedVersion.value,
      props.device.device_type
    )
  } catch {
    versionInfo.value = null
  } finally {
    isLoadingVersionInfo.value = false
  }
}

function toggleComplect(comp: Complectation) {
  if (comp.label === 'base') return

  if (selectedComplectationIds.value.has(comp.id)) {
    selectedComplectationIds.value.delete(comp.id)
  } else {
    selectedComplectationIds.value.add(comp.id)
  }
  // Force reactivity on Set mutation
  selectedComplectationIds.value = new Set(selectedComplectationIds.value)

  // If auth user without public token — sync with API
  if (props.isAuth && !props.publicToken) {
    emit('toggle-complectation', {
      serial: props.device.serial,
      complectationId: comp.id,
    })
  }
}

async function downloadFirmware() {
  if (!selectedVersion.value) {
    toast.warning('Выберите версию прошивки')
    return
  }
  isDownloading.value = true
  try {
    const ids = Array.from(selectedComplectationIds.value)
    emit('download', {
      device: props.device,
      version: selectedVersion.value,
      selectedIds: ids,
    })
  } finally {
    isDownloading.value = false
  }
}
</script>

<template>
  <div class="device-card" data-testid="device-card">
    <!-- Header -->
    <div class="device-header">
      <div class="device-icon" :aria-hidden="true">
        <Icon :name="deviceTypeIcon" size="24" />
      </div>
      <div class="device-info">
        <code class="device-serial" data-testid="device-serial">{{ device.serial }}</code>
        <span class="device-type-badge">{{ device.device_type }}</span>
      </div>
    </div>

    <p v-if="device.comment" class="device-comment">{{ device.comment }}</p>

    <!-- Version select -->
    <div class="version-section">
      <label class="field-label" :for="`version-${device.id}`">Версия прошивки:</label>
      <div class="select-wrapper">
        <select
          :id="`version-${device.id}`"
          v-model="selectedVersion"
          class="version-select"
          data-testid="version-select"
          :disabled="isLoadingVersions || versions.length === 0"
          @change="loadVersionInfo"
        >
          <option value="">
            {{ isLoadingVersions ? 'Загрузка...' : 'Выберите версию...' }}
          </option>
          <option v-for="v in versions" :key="v" :value="v">Версия {{ v }}</option>
        </select>
      </div>
    </div>

    <!-- Changelog -->
    <div v-if="selectedVersion" class="changelog" data-testid="version-changelog">
      <div v-if="isLoadingVersionInfo" class="changelog-skeleton">
        <USkeleton height="80px" />
      </div>
      <div v-else-if="versionInfo" class="changelog-content">
        <h4 class="changelog-title">Изменения в версии {{ selectedVersion }}:</h4>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div
          class="changelog-text"
          v-html="versionInfo.changes.replace(/\n/g, '<br>')"
        />
        <div
          v-if="Object.keys(versionInfo.links || {}).length"
          class="version-links"
        >
          <a
            v-for="(url, name) in versionInfo.links"
            :key="name"
            :href="url"
            class="version-link"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Icon name="ph:link-bold" size="14" aria-hidden="true" />
            {{ name }}
          </a>
        </div>
      </div>
    </div>

    <!-- Complectations -->
    <div v-if="simpleComplectations.length > 0" class="complectations-section">
      <label class="field-label">Комплектация прошивки:</label>
      <div class="complectation-buttons" role="group" aria-label="Выбор комплектации">
        <button
          v-for="comp in simpleComplectations"
          :key="comp.id"
          type="button"
          :disabled="comp.label === 'base'"
          :class="[
            'complectation-btn',
            { 'is-active': selectedComplectationIds.has(comp.id) },
            { 'is-base': comp.label === 'base' },
          ]"
          data-testid="complectation-btn"
          :aria-label="comp.caption"
          :aria-pressed="selectedComplectationIds.has(comp.id)"
          @click="toggleComplect(comp)"
        >
          {{ comp.caption }}
        </button>
      </div>
    </div>

    <!-- Download button -->
    <button
      type="button"
      class="download-btn"
      :disabled="!selectedVersion || isDownloading"
      data-testid="download-btn"
      :aria-busy="isDownloading"
      @click="downloadFirmware"
    >
      <Icon name="ph:download-bold" size="16" aria-hidden="true" />
      {{ isDownloading ? 'Компиляция...' : 'Скачать прошивку' }}
    </button>
  </div>
</template>

<style scoped>
.device-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.device-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

/* Header */
.device-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.device-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-accent-glow);
  color: var(--color-accent);
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.device-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.device-serial {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-neon);
  word-break: break-all;
}

.device-type-badge {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-accent);
  background: var(--color-accent-glow);
  border-radius: var(--radius-sm);
  padding: 2px 8px;
  align-self: flex-start;
}

.device-comment {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin: 0;
}

/* Version section */
.version-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
}

.select-wrapper {
  position: relative;
}

.version-select {
  width: 100%;
  padding: 10px 14px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  cursor: pointer;
  appearance: none;
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.version-select:focus {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.version-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Changelog */
.changelog {
  background: var(--color-surface-2);
  border-radius: var(--radius-md);
  padding: 16px;
  border-left: 3px solid var(--color-accent);
}

.changelog-skeleton {
  min-height: 80px;
}

.changelog-title {
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 8px;
}

.changelog-text {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  line-height: 1.6;
}

.version-links {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.version-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-xs);
  color: var(--color-accent);
  text-decoration: none;
  padding: 4px 10px;
  background: var(--color-accent-glow);
  border-radius: var(--radius-full);
  transition: background-color var(--transition-fast);
}

.version-link:hover {
  background: var(--color-accent);
  color: var(--color-on-accent);
}

/* Complectations */
.complectations-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.complectation-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.complectation-btn {
  padding: 8px 16px;
  font-size: var(--text-sm);
  font-weight: 600;
  font-family: var(--font-sans);
  border: 2px solid var(--color-border);
  background: var(--color-surface-2);
  color: var(--color-text-2);
  border-radius: var(--radius-md);
  cursor: pointer;
  min-height: 44px;
  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    color var(--transition-fast);
  outline: none;
}

.complectation-btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.complectation-btn:hover:not(:disabled) {
  border-color: var(--color-accent);
}

.complectation-btn.is-active {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
  color: var(--color-accent);
}

.complectation-btn.is-base {
  opacity: 0.7;
  cursor: default;
}

.complectation-btn:disabled {
  opacity: 0.7;
  cursor: default;
}

/* Download button */
.download-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px 28px;
  font-size: var(--text-base);
  font-weight: 700;
  font-family: var(--font-sans);
  background: var(--color-accent);
  color: var(--color-on-accent);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  min-height: 56px;
  transition:
    background-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
  outline: none;
  margin-top: auto;
}

.download-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  box-shadow: var(--shadow-glow-accent);
  transform: translateY(-1px);
}

.download-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.download-btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.download-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
