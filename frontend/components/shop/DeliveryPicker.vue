<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useOrders } from '~/composables/useOrders'

const props = defineProps<{
  cityCode: string
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'select', pvz: any): void
}>()

const { getPVZs } = useOrders()
const pvzs = ref<any[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

const fetchPVZs = async (cityCode: string) => {
  if (!cityCode) return
  isLoading.value = true
  error.value = null
  try {
    const { data, error: fetchError } = await getPVZs(cityCode)
    if (fetchError.value) {
      error.value = 'Не удалось загрузить пункты выдачи'
      return
    }
    if (data.value) {
      pvzs.value = data.value.items
    }
  } catch (err) {
    error.value = 'Ошибка загрузки пунктов'
  } finally {
    isLoading.value = false
  }
}

watch(() => props.cityCode, (newVal) => {
  if (newVal) {
    fetchPVZs(newVal)
  } else {
    pvzs.value = []
  }
})

onMounted(() => {
  if (props.cityCode) {
    fetchPVZs(props.cityCode)
  }
})

const handleSelect = (code: string) => {
  const pvz = pvzs.value.find(p => p.code === code)
  emit('update:modelValue', code)
  emit('select', pvz)
}
</script>

<template>
  <div class="delivery-picker">
    <div v-if="isLoading" class="picker-loading">
      <div class="shimmer-box" style="height: 56px; border-radius: 8px;"></div>
    </div>
    
    <div v-else-if="error" class="picker-error">
      {{ error }}
    </div>
    
    <div v-else-if="cityCode && pvzs.length > 0" class="picker-list">
      <label class="picker-label">Выберите пункт выдачи СДЭК</label>
      <div class="pvz-scroll-container">
        <div 
          v-for="pvz in pvzs" 
          :key="pvz.code"
          class="pvz-card"
          :class="{ 'pvz-card--active': modelValue === pvz.code }"
          @click="handleSelect(pvz.code)"
        >
          <div class="pvz-header">
            <span class="pvz-name">{{ pvz.name }}</span>
            <div class="pvz-check" v-if="modelValue === pvz.code">
              <Icon name="ph:check-circle-fill" size="20" />
            </div>
          </div>
          <div class="pvz-address">{{ pvz.address }}</div>
          <div class="pvz-hours" v-if="pvz.work_hours">
            <Icon name="ph:clock" size="14" />
            <span>{{ pvz.work_hours }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="cityCode" class="picker-empty">
      В этом городе нет пунктов выдачи СДЭК
    </div>
    
    <div v-else class="picker-hint">
      Сначала выберите город доставки
    </div>
  </div>
</template>

<style scoped>
.delivery-picker {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.picker-label {
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 4px;
}

.pvz-scroll-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

/* Custom scrollbar */
.pvz-scroll-container::-webkit-scrollbar { width: 4px; }
.pvz-scroll-container::-webkit-scrollbar-track { background: var(--color-surface-2); }
.pvz-scroll-container::-webkit-scrollbar-thumb { background: var(--color-border-strong); border-radius: 4px; }

.pvz-card {
  padding: 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.pvz-card:hover {
  border-color: var(--color-accent);
  background: var(--color-bg-subtle);
}

.pvz-card--active {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
  box-shadow: var(--shadow-glow-accent);
}

.pvz-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4px;
}

.pvz-name {
  font-weight: 700;
  font-size: var(--text-sm);
  color: var(--color-text);
}

.pvz-check {
  color: var(--color-accent);
}

.pvz-address {
  font-size: var(--text-xs);
  color: var(--color-text-2);
  margin-bottom: 8px;
}

.pvz-hours {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--color-muted);
}

.picker-loading, .picker-error, .picker-empty, .picker-hint {
  padding: 24px;
  text-align: center;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-muted);
  font-size: var(--text-sm);
}

.shimmer-box {
  background: var(--color-skeleton);
  background-image: linear-gradient(
    90deg,
    var(--color-skeleton) 0%,
    var(--color-skeleton-shine) 50%,
    var(--color-skeleton) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
</style>
