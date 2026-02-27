<script setup lang="ts">
import { useOrders } from '~/composables/useOrders'
import type { PVZ } from '~/composables/useOrders'

const props = defineProps<{
  cityCode: string
}>()

const emit = defineEmits<{
  (e: 'select', pvz: PVZ): void
}>()

const { getPVZs } = useOrders()
const { data: pvzsData, pending } = await getPVZs(props.cityCode)

const selectedCode = ref('')

const handleSelect = (pvz: PVZ) => {
  selectedCode.value = pvz.code
  emit('select', pvz)
}
</script>

<template>
  <div class="delivery-picker">
    <div v-if="pending" class="delivery-picker__loading">
      <div class="skeleton h-10 w-full mb-4"></div>
      <div class="skeleton h-24 w-full"></div>
    </div>

    <div v-else-if="pvzsData?.items.length" class="pvz-list">
      <div
        v-for="pvz in pvzsData.items"
        :key="pvz.code"
        class="pvz-item"
        :class="{ 'is-selected': selectedCode === pvz.code }"
        @click="handleSelect(pvz)"
      >
        <div class="pvz-item__header">
          <span class="pvz-item__name">{{ pvz.name }}</span>
          <Icon v-if="selectedCode === pvz.code" name="ph:check-circle-fill" size="20" color="var(--color-success)" />
        </div>
        <div class="pvz-item__address">{{ pvz.address }}</div>
        <div class="pvz-item__hours">Часы работы: {{ pvz.work_hours }}</div>
      </div>
    </div>

    <div v-else class="pvz-empty">
      В данном городе пункты выдачи не найдены.
    </div>
  </div>
</template>

<style scoped>
.pvz-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

.pvz-item {
  padding: 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--color-surface);
}

.pvz-item:hover {
  border-color: var(--color-accent);
  background: var(--color-surface-2);
}

.pvz-item.is-selected {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
  box-shadow: var(--shadow-glow-accent);
}

.pvz-item__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4px;
}

.pvz-item__name {
  font-weight: 700;
  font-size: var(--text-base);
  color: var(--color-text);
}

.pvz-item__address {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin-bottom: 8px;
}

.pvz-item__hours {
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.pvz-empty {
  padding: 24px;
  text-align: center;
  color: var(--color-muted);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
}

/* Custom Scrollbar */
.pvz-list::-webkit-scrollbar { width: 4px; }
.pvz-list::-webkit-scrollbar-track { background: var(--color-bg-subtle); }
.pvz-list::-webkit-scrollbar-thumb { background: var(--color-border-strong); border-radius: 4px; }
</style>
