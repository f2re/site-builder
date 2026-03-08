<script setup lang="ts">
import type { DeliveryAddress } from '~/composables/useAddresses'

const props = defineProps<{
  address: DeliveryAddress
}>()

const emit = defineEmits<{
  edit: []
  delete: []
  setDefault: []
}>()

const providerLabels: Record<string, string> = {
  cdek: 'СДЭК',
  pochta: 'Почта РФ',
  ozon: 'Ozon',
  wb: 'Wildberries'
}
</script>

<template>
  <div class="address-card" :class="{ 'address-card--default': address.is_default }" data-testid="address-card">
    <div class="address-card__header">
      <h3 class="address-card__name" data-testid="address-name">{{ address.name }}</h3>
      <span v-if="address.is_default" class="address-badge" data-testid="default-badge">По умолчанию</span>
    </div>

    <div class="address-card__body">
      <p class="address-card__recipient">{{ address.recipient_name }}</p>
      <p class="address-card__phone">{{ address.recipient_phone }}</p>
      <p class="address-card__address">{{ address.full_address }}, {{ address.city }}</p>
      <p class="address-card__provider">{{ providerLabels[address.provider] }}</p>
    </div>

    <div class="address-card__actions">
      <button v-if="!address.is_default" class="btn-text" data-testid="set-default-btn" @click="emit('setDefault')">
        Сделать основным
      </button>
      <button class="btn-text" data-testid="edit-address-btn" @click="emit('edit')">
        <Icon name="ph:pencil-bold" size="14" />
        Изменить
      </button>
      <button class="btn-text btn-text--danger" data-testid="delete-address-btn" @click="emit('delete')">
        <Icon name="ph:trash-bold" size="14" />
        Удалить
      </button>
    </div>
  </div>
</template>

<style scoped>
.address-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  transition: border-color var(--transition-fast);
}

.address-card--default {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
}

.address-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 8px;
}

.address-card__name {
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.address-badge {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-accent);
  background: var(--color-accent-glow);
  padding: 4px 10px;
  border-radius: var(--radius-full);
}

.address-card__body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 16px;
}

.address-card__recipient,
.address-card__phone,
.address-card__address,
.address-card__provider {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin: 0;
}

.address-card__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-text {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: var(--color-accent);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  padding: 4px 0;
  transition: opacity var(--transition-fast);
}

.btn-text:hover {
  opacity: 0.8;
}

.btn-text--danger {
  color: var(--color-error);
}
</style>
