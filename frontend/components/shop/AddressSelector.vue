<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAddresses } from '~/composables/useAddresses'
import type { DeliveryAddress } from '~/composables/useAddresses'

const emit = defineEmits<{
  select: [address: DeliveryAddress | null]
}>()

const { data } = await useAddresses().getAddresses()
const addresses = computed(() => data.value?.items || [])

const selectedId = ref<string | null>(null)
const showNewAddress = ref(false)

const selectAddress = (addr: DeliveryAddress) => {
  selectedId.value = addr.id
  showNewAddress.value = false
  emit('select', addr)
}

const selectNewAddress = () => {
  selectedId.value = null
  showNewAddress.value = true
  emit('select', null)
}

const defaultAddress = computed(() => addresses.value.find(a => a.is_default))

if (defaultAddress.value && !selectedId.value) {
  selectAddress(defaultAddress.value)
}
</script>

<template>
  <div class="address-selector" data-testid="address-selector">
    <label class="selector-label">Адрес доставки</label>

    <div v-if="addresses.length > 0" class="addresses-list">
      <button
        v-for="addr in addresses"
        :key="addr.id"
        class="address-option"
        :class="{ 'address-option--selected': selectedId === addr.id }"
        data-testid="address-option"
        @click="selectAddress(addr)"
      >
        <div class="address-option__content">
          <div class="address-option__name">{{ addr.name }}</div>
          <div class="address-option__address">{{ addr.full_address }}, {{ addr.city }}</div>
        </div>
        <Icon v-if="selectedId === addr.id" name="ph:check-circle-fill" size="20" class="check-icon" />
      </button>

      <button
        class="address-option address-option--new"
        :class="{ 'address-option--selected': showNewAddress }"
        data-testid="new-address-option"
        @click="selectNewAddress"
      >
        <Icon name="ph:plus-circle-bold" size="20" />
        <span>Новый адрес</span>
      </button>
    </div>

    <div v-else class="no-addresses">
      <p>У вас нет сохранённых адресов</p>
    </div>
  </div>
</template>

<style scoped>
.address-selector {
  margin-bottom: 24px;
}

.selector-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
  margin-bottom: 12px;
}

.addresses-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.address-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border-color var(--transition-fast), background var(--transition-fast);
  text-align: left;
  min-height: 44px;
}

.address-option:hover {
  border-color: var(--color-accent);
}

.address-option--selected {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
}

.address-option__content {
  flex: 1;
  min-width: 0;
}

.address-option__name {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 2px;
}

.address-option__address {
  font-size: var(--text-xs);
  color: var(--color-text-2);
}

.address-option--new {
  justify-content: center;
  color: var(--color-accent);
  font-weight: 600;
}

.check-icon {
  color: var(--color-accent);
  flex-shrink: 0;
}

.no-addresses {
  padding: 20px;
  text-align: center;
  color: var(--color-muted);
  font-size: var(--text-sm);
}
</style>
