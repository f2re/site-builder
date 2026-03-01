<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'

interface PVZ {
  code: string
  address: string
  name: string
  lat: number
  lon: number
  work_hours: string
}

const props = defineProps<{
  modelValue: string
  pvzs: PVZ[]
  isLoading?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const viewType = ref<'list' | 'map'>('list')
const searchQuery = ref('')
const mapInstance = ref<any>(null)
const mapContainer = ref<HTMLElement | null>(null)

const filteredPvzs = computed(() => {
  if (!searchQuery.value) return props.pvzs
  const query = searchQuery.value.toLowerCase()
  return props.pvzs.filter(p => 
    p.address.toLowerCase().includes(query) || 
    p.name.toLowerCase().includes(query)
  )
})

const selectPvz = (code: string) => {
  emit('update:modelValue', code)
}

const toggleView = (type: 'list' | 'map') => {
  viewType.value = type
  if (type === 'map') {
    nextTick(() => {
      initMap()
    })
  }
}

// Load Yandex Maps script
const loadYMaps = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if ((window as any).ymaps) {
      (window as any).ymaps.ready(resolve)
      return
    }

    const script = document.createElement('script')
    script.src = 'https://api-maps.yandex.ru/2.1/?lang=ru_RU'
    script.async = true
    script.onload = () => {
      (window as any).ymaps.ready(resolve)
    }
    script.onerror = reject
    document.head.appendChild(script)
  })
}

const initMap = async () => {
  if (!mapContainer.value) return
  
  try {
    await loadYMaps()
    const ymaps = (window as any).ymaps

    if (mapInstance.value) {
      mapInstance.value.destroy()
    }

    // Calculate center
    let center = [55.753215, 37.622504] // Moscow
    if (props.pvzs.length > 0) {
      center = [props.pvzs[0].lat, props.pvzs[0].lon]
    }

    mapInstance.value = new ymaps.Map(mapContainer.value, {
      center,
      zoom: 12,
      controls: ['zoomControl', 'fullscreenControl']
    })

    const objectManager = new ymaps.ObjectManager({
      clusterize: true,
      gridSize: 32,
      clusterDisableClickZoom: false
    })

    const features = props.pvzs.map(p => ({
      type: 'Feature',
      id: p.code,
      geometry: {
        type: 'Point',
        coordinates: [p.lat, p.lon]
      },
      properties: {
        balloonContentHeader: `<strong>${p.name}</strong>`,
        balloonContentBody: `
          <div class="map-balloon">
            <p>${p.address}</p>
            <p><small>${p.work_hours}</small></p>
            <button 
              class="select-btn-map" 
              onclick="window.dispatchEvent(new CustomEvent('select-pvz', {detail: '${p.code}'}))"
              style="
                background: #e63946; 
                color: white; 
                border: none; 
                padding: 8px 16px; 
                border-radius: 4px; 
                margin-top: 8px; 
                cursor: pointer;
                font-family: inherit;
                font-weight: 600;
                width: 100%;
              "
            >
              Выбрать
            </button>
          </div>
        `,
        hintContent: p.address
      }
    }))

    objectManager.add(features)
    mapInstance.value.geoObjects.add(objectManager)

    // Fit to bounds if there are many points
    if (features.length > 1) {
      mapInstance.value.setBounds(objectManager.getBounds(), {
        checkZoomRange: true,
        zoomMargin: 20
      })
    }
  } catch (err) {
    console.error('Failed to init Yandex Maps', err)
  }
}

// Global listener for map balloon buttons
onMounted(() => {
  window.addEventListener('select-pvz', (e: any) => {
    selectPvz(e.detail)
  })
})

watch(() => props.pvzs, () => {
  if (viewType.value === 'map') {
    initMap()
  }
}, { deep: true })

</script>

<template>
  <div class="cdek-picker">
    <div class="picker-header">
      <div class="view-toggle">
        <button 
          class="toggle-btn" 
          :class="{ active: viewType === 'list' }"
          @click="toggleView('list')"
        >
          <Icon name="ph:list-bold" />
          Список
        </button>
        <button 
          class="toggle-btn" 
          :class="{ active: viewType === 'map' }"
          @click="toggleView('map')"
        >
          <Icon name="ph:map-pin-bold" />
          Карта
        </button>
      </div>

      <div class="search-wrapper" v-if="viewType === 'list'">
        <UInput
          v-model="searchQuery"
          placeholder="Поиск по адресу..."
          icon="ph:magnifying-glass-bold"
        />
      </div>
    </div>

    <div class="picker-content">
      <Transition name="fade-slide" mode="out-in">
        <div v-if="viewType === 'list'" key="list" class="pvz-list custom-scrollbar">
          <div v-if="isLoading" class="pvz-loading">
            <USkeleton v-for="i in 3" :key="i" height="120px" class="pvz-skeleton" />
          </div>
          <template v-else-if="filteredPvzs.length > 0">
            <div 
              v-for="pvz in filteredPvzs" 
              :key="pvz.code"
              class="pvz-card"
              :class="{ selected: modelValue === pvz.code }"
              @click="selectPvz(pvz.code)"
            >
              <div class="pvz-card-header">
                <span class="pvz-name">{{ pvz.name }}</span>
                <Icon 
                  v-if="modelValue === pvz.code" 
                  name="ph:check-circle-fill" 
                  class="selected-icon" 
                />
              </div>
              <p class="pvz-address">{{ pvz.address }}</p>
              <div class="pvz-meta">
                <div class="meta-item">
                  <Icon name="ph:clock-bold" />
                  <span>{{ pvz.work_hours }}</span>
                </div>
              </div>
              <div class="pvz-actions">
                <UButton 
                  :variant="modelValue === pvz.code ? 'primary' : 'secondary'"
                  size="sm"
                  class="select-btn"
                >
                  {{ modelValue === pvz.code ? 'Выбрано' : 'Выбрать' }}
                </UButton>
              </div>
            </div>
          </template>
          <div v-else class="pvz-empty">
            <Icon name="ph:map-pin-slash-bold" size="48" />
            <p>Пункты не найдены</p>
          </div>
        </div>

        <div v-else key="map" class="pvz-map-container">
          <div ref="mapContainer" class="map-view"></div>
          <div v-if="isLoading" class="map-overlay-loading">
            <USpinner />
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.cdek-picker {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  height: 500px;
  position: relative;
}

.picker-header {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (min-width: 640px) {
  .picker-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.view-toggle {
  display: flex;
  background: var(--color-surface-2);
  padding: 4px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  width: fit-content;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--color-text-2);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  border-radius: calc(var(--radius-md) - 2px);
  transition: all var(--transition-fast);
}

.toggle-btn.active {
  background: var(--color-surface);
  color: var(--color-accent);
  box-shadow: var(--shadow-sm);
}

.search-wrapper {
  flex: 1;
  max-width: 300px;
}

.picker-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.pvz-list {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pvz-card {
  padding: 16px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.pvz-card:hover {
  border-color: var(--color-accent);
  transform: translateY(-2px);
}

.pvz-card.selected {
  border-color: var(--color-accent);
  background: var(--color-surface-3);
  box-shadow: var(--shadow-glow-accent);
}

.pvz-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.pvz-name {
  font-weight: 700;
  color: var(--color-text);
  font-size: var(--text-base);
}

.selected-icon {
  color: var(--color-accent);
  font-size: 1.25rem;
}

.pvz-address {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin-bottom: 12px;
  line-height: 1.4;
}

.pvz-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.pvz-actions {
  display: flex;
  justify-content: flex-end;
}

.pvz-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: var(--color-muted);
  gap: 12px;
}

.pvz-map-container {
  height: 100%;
  width: 100%;
}

.map-view {
  height: 100%;
  width: 100%;
}

.map-overlay-loading {
  position: absolute;
  inset: 0;
  background: var(--color-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.pvz-loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pvz-skeleton {
  border-radius: var(--radius-md);
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--color-border-strong);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--color-accent);
}

/* Map Balloon Styling (passed as raw HTML) */
:deep(.map-balloon) {
  font-family: var(--font-sans);
  color: #111118; /* Yandex balloons often have their own bg, using dark text for contrast */
}

/* Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all var(--transition-normal);
}
.fade-slide-enter-from { opacity: 0; transform: translateY(10px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
