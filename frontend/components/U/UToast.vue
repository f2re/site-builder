<script setup lang="ts">
/**
 * UToast — глобальный компонент стека toast-уведомлений.
 *
 * Подключается ОДИН РАЗ в app.vue. Управляется через useToast().
 *
 * Поддерживает типы: success, error, warning, info.
 * Стек: до 3 одновременных уведомлений. Новые добавляются сверху.
 * Анимация: slide-in справа (desktop) / снизу (mobile).
 * Автоматическое исчезновение: success 3s, info 4s, warning 5s, error 6s.
 *
 * @example в компонентах:
 * const toast = useToast()
 * toast.success('Сохранено')
 * toast.error('Ошибка', 'Попробуйте снова', { label: 'Повторить', handler: () => {} })
 */

import { useToast } from '~/composables/useToast'

const { toasts, remove } = useToast()

/** Максимальное количество видимых уведомлений */
const MAX_VISIBLE = 3

const visibleToasts = computed(() => toasts.value.slice(-MAX_VISIBLE))

/** Иконка по типу */
const iconMap: Record<string, string> = {
  success: 'ph:check-circle-bold',
  error: 'ph:x-circle-bold',
  warning: 'ph:warning-bold',
  info: 'ph:info-bold',
}

/** Цвет иконки по типу */
const colorMap: Record<string, string> = {
  success: 'var(--color-success)',
  error: 'var(--color-error)',
  warning: 'var(--color-warning)',
  info: 'var(--color-info)',
}

/** Цвет полоски прогресса */
const progressColorMap: Record<string, string> = {
  success: 'var(--color-success)',
  error: 'var(--color-error)',
  warning: 'var(--color-warning)',
  info: 'var(--color-info)',
}

/** Длительность анимации прогресс-бара (совпадает с duration toast) */
const durationMap: Record<string, number> = {
  success: 3000,
  error: 6000,
  warning: 5000,
  info: 4000,
}
</script>

<template>
  <Teleport to="body">
    <div
      class="toast-container"
      role="status"
      aria-live="polite"
      aria-atomic="false"
      data-testid="toast-container"
    >
      <TransitionGroup name="toast" tag="div" class="toast-list">
        <div
          v-for="toast in visibleToasts"
          :key="toast.id"
          class="toast-item"
          :class="`toast-item--${toast.type}`"
          data-testid="toast-item"
          role="alert"
        >
          <!-- Icon -->
          <div class="toast-icon" :style="{ color: colorMap[toast.type] }">
            <Icon :name="iconMap[toast.type]" size="20" />
          </div>

          <!-- Content -->
          <div class="toast-content">
            <div class="toast-title">{{ toast.title }}</div>
            <div v-if="toast.message" class="toast-message">{{ toast.message }}</div>
            <button
              v-if="toast.action"
              class="toast-action"
              @click="toast.action!.handler(); remove(toast.id)"
            >
              {{ toast.action.label }}
            </button>
          </div>

          <!-- Close button -->
          <button
            class="toast-close"
            aria-label="Закрыть уведомление"
            data-testid="toast-close-btn"
            @click="remove(toast.id)"
          >
            <Icon name="ph:x-bold" size="14" />
          </button>

          <!-- Progress bar -->
          <div
            class="toast-progress"
            :style="{
              '--toast-duration': `${toast.duration ?? durationMap[toast.type]}ms`,
              background: progressColorMap[toast.type],
            }"
          />
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 1.25rem;
  right: 1.25rem;
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  pointer-events: none;
  width: 360px;
  max-width: calc(100vw - 2.5rem);
}

.toast-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.toast-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem 1rem 1.125rem;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  pointer-events: all;
  overflow: hidden;
}

/* Левая цветная полоса по типу */
.toast-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  border-radius: var(--radius-sm) 0 0 var(--radius-sm);
}

.toast-item--success::before { background: var(--color-success); }
.toast-item--error::before   { background: var(--color-error); }
.toast-item--warning::before { background: var(--color-warning); }
.toast-item--info::before    { background: var(--color-info); }

.toast-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
}

.toast-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.toast-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
  line-height: 1.4;
}

.toast-message {
  font-size: var(--text-xs);
  color: var(--color-text-2);
  line-height: 1.4;
}

.toast-action {
  margin-top: 0.25rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-accent);
  padding: 0;
  text-decoration: underline;
  text-underline-offset: 2px;
  transition: color var(--transition-fast);
}

.toast-action:hover {
  color: var(--color-accent-hover);
}

.toast-close {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-top: 1px;
}

.toast-close:hover {
  background: var(--color-surface-3);
  color: var(--color-text);
}

/* Progress bar at the bottom */
.toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  width: 100%;
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  transform-origin: left;
  animation: toast-progress var(--toast-duration, 4000ms) linear forwards;
}

@keyframes toast-progress {
  from { transform: scaleX(1); }
  to   { transform: scaleX(0); }
}

/* TransitionGroup animations — slide from right */
.toast-enter-active {
  transition:
    opacity var(--transition-normal),
    transform var(--transition-normal);
}

.toast-leave-active {
  transition:
    opacity var(--transition-fast),
    transform var(--transition-fast);
  position: absolute;
  width: 100%;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform var(--transition-normal);
}

/* Mobile: slide from bottom, full width */
@media (max-width: 640px) {
  .toast-container {
    top: auto;
    bottom: 5rem; /* above bottom navigation */
    right: 0;
    left: 0;
    width: 100%;
    max-width: 100%;
    padding: 0 1rem;
  }

  .toast-enter-from,
  .toast-leave-to {
    opacity: 0;
    transform: translateY(100%);
  }
}
</style>
