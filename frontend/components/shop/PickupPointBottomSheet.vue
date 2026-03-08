<script setup lang="ts">
import { ref, computed } from 'vue'
import type { PickupPointResult } from '~/composables/useDeliveryAggregator'

interface Props {
  isOpen: boolean
  points: PickupPointResult[]
  selectedCode: string | null
  provider: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'select', point: PickupPointResult): void
  (e: 'apply'): void
}>()

const searchQuery = ref('')

const filteredPoints = computed(() => {
  if (!searchQuery.value) return props.points
  const q = searchQuery.value.toLowerCase()
  return props.points.filter(p =>
    p.address.toLowerCase().includes(q) ||
    p.name.toLowerCase().includes(q)
  )
})

function handleBackdropClick() {
  emit('close')
}

function handleSelect(point: PickupPointResult) {
  emit('select', point)
}

function handleApply() {
  emit('apply')
}
</script>

<template>
  <Teleport to="body">
    <Transition name="bottom-sheet">
      <div
        v-if="isOpen"
        class="bottom-sheet-wrapper"
        data-testid="pvz-bottom-sheet"
        @click.self="handleBackdropClick"
      >
        <div class="bottom-sheet">
          <div class="bottom-sheet__handle" />
          <div class="bottom-sheet__header">
            <h3 class="bottom-sheet__title">Выберите пункт выдачи</h3>
            <button
              class="bottom-sheet__close"
              data-testid="pvz-bottom-sheet-close"
              aria-label="Закрыть"
              @click="emit('close')"
            >
              <Icon name="ph:x-bold" size="20" />
            </button>
          </div>

          <div class="bottom-sheet__search">
            <Icon name="ph:magnifying-glass-bold" size="18" class="search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="Поиск по адресу..."
              data-testid="pvz-search-input"
            />
          </div>

          <div class="bottom-sheet__list">
            <div
              v-for="point in filteredPoints"
              :key="point.code"
              class="pvz-item"
              :class="{ 'pvz-item--selected': selectedCode === point.code }"
              data-testid="pvz-item"
              @click="handleSelect(point)"
            >
              <div class="pvz-item__info">
                <div class="pvz-item__name">{{ point.name }}</div>
                <div class="pvz-item__address">{{ point.address }}</div>
                <div class="pvz-item__hours">
                  <Icon name="ph:clock-bold" size="12" />
                  {{ point.work_time }}
                </div>
              </div>
              <Icon
                v-if="selectedCode === point.code"
                name="ph:check-circle-fill"
                size="24"
                class="pvz-item__check"
              />
            </div>
          </div>

          <button
            class="bottom-sheet__apply"
            data-testid="pvz-apply-btn"
            :disabled="!selectedCode"
            @click="handleApply"
          >
            Применить
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
@media (min-width: 768px) {
  .bottom-sheet-wrapper {
    display: none;
  }
}

.bottom-sheet-wrapper {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  background: var(--color-overlay);
  display: flex;
  align-items: flex-end;
}

.bottom-sheet {
  width: 100%;
  max-height: 85vh;
  background: var(--color-surface);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-modal);
}

.bottom-sheet__handle {
  width: 40px;
  height: 4px;
  background: var(--color-border-strong);
  border-radius: var(--radius-full);
  margin: 12px auto 8px;
}

.bottom-sheet__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
}

.bottom-sheet__title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
}

.bottom-sheet__close {
  background: none;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast);
  min-width: 32px;
  min-height: 32px;
  justify-content: center;
}

.bottom-sheet__close:hover {
  color: var(--color-text);
}

.bottom-sheet__search {
  position: relative;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
}

.search-icon {
  position: absolute;
  left: 32px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 10px 14px 10px 40px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  color: var(--color-text);
  font-size: 16px;
  outline: none;
  transition: border-color var(--transition-fast);
}

.search-input:focus {
  border-color: var(--color-accent);
}

.bottom-sheet__list {
  flex: 1;
  overflow-y: auto;
  padding: 12px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pvz-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface-2);
  cursor: pointer;
  transition: border-color var(--transition-fast), background var(--transition-fast);
}

.pvz-item:active {
  transform: scale(0.98);
}

.pvz-item--selected {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
}

.pvz-item__info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pvz-item__name {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
}

.pvz-item__address {
  font-size: var(--text-xs);
  color: var(--color-text-2);
}

.pvz-item__hours {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.pvz-item__check {
  color: var(--color-accent);
  flex-shrink: 0;
}

.bottom-sheet__apply {
  margin: 16px 20px;
  padding: 14px;
  background: var(--color-accent);
  color: var(--color-on-accent);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: 700;
  cursor: pointer;
  transition: background var(--transition-fast);
  min-height: 52px;
}

.bottom-sheet__apply:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bottom-sheet__apply:not(:disabled):active {
  transform: scale(0.98);
}

.bottom-sheet-enter-active,
.bottom-sheet-leave-active {
  transition: opacity var(--transition-normal);
}

.bottom-sheet-enter-active .bottom-sheet,
.bottom-sheet-leave-active .bottom-sheet {
  transition: transform var(--transition-normal);
}

.bottom-sheet-enter-from,
.bottom-sheet-leave-to {
  opacity: 0;
}

.bottom-sheet-enter-from .bottom-sheet,
.bottom-sheet-leave-to .bottom-sheet {
  transform: translateY(100%);
}
</style>
