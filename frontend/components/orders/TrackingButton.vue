<script setup lang="ts">
const props = defineProps<{
  trackingUrl?: string
  provider: string
}>()

const providerLabels: Record<string, string> = {
  cdek: 'СДЭК',
  pochta: 'Почте РФ',
  ozon: 'Ozon',
  wb: 'Wildberries'
}

const label = computed(() => `Отследить на ${providerLabels[props.provider] || 'сайте доставки'}`)
</script>

<template>
  <a
    v-if="trackingUrl"
    :href="trackingUrl"
    target="_blank"
    rel="noopener noreferrer"
    class="tracking-btn"
    data-testid="tracking-btn"
  >
    <Icon name="ph:package-bold" size="16" />
    {{ label }}
    <Icon name="ph:arrow-square-out-bold" size="14" />
  </a>
</template>

<style scoped>
.tracking-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-accent);
  font-size: var(--text-sm);
  font-weight: 600;
  text-decoration: none;
  transition: border-color var(--transition-fast), background var(--transition-fast);
  min-height: 44px;
}

.tracking-btn:hover {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
}
</style>
