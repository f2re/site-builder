<script setup lang="ts">
const props = defineProps<{
  status: string
}>()

const statusConfig: Record<string, { label: string; color: string }> = {
  pending: { label: 'Ожидает', color: 'var(--color-muted)' },
  awaiting_payment: { label: 'Ожидает оплаты', color: 'var(--color-warning)' },
  paid: { label: 'Оплачен', color: 'var(--color-success)' },
  shipped: { label: 'Отправлен', color: 'var(--color-info)' },
  delivered: { label: 'Доставлен', color: 'var(--color-success)' },
  cancelled: { label: 'Отменён', color: 'var(--color-error)' },
  failed: { label: 'Ошибка', color: 'var(--color-error)' }
}

const config = computed(() => statusConfig[props.status] || statusConfig.pending)
</script>

<template>
  <span class="status-badge" :style="{ '--badge-color': config.color }" data-testid="order-status-badge">
    {{ config.label }}
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--badge-color);
  background: color-mix(in srgb, var(--badge-color) 15%, transparent);
  border: 1px solid var(--badge-color);
}
</style>
