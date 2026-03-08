<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useDeliveryStore } from '~/stores/deliveryStore'
import { useDeliveryAggregator } from '~/composables/useDeliveryAggregator'
import type { DeliveryOption, DeliveryProvider } from '~/stores/deliveryStore'

interface Props {
  cityCode: number | null
  totalWeightGrams?: number
}

const props = withDefaults(defineProps<Props>(), {
  totalWeightGrams: 500
})

const emit = defineEmits<{
  (e: 'provider-selected', provider: string): void
  (e: 'option-selected', option: DeliveryOption): void
}>()

const deliveryStore = useDeliveryStore()
const { calculateAll } = useDeliveryAggregator()

const groupedProviders = computed(() => {
  const groups = new Map<DeliveryProvider, DeliveryOption[]>()
  deliveryStore.availableOptions.forEach(opt => {
    if (!groups.has(opt.provider)) {
      groups.set(opt.provider, [])
    }
    groups.get(opt.provider)!.push(opt)
  })
  return groups
})

const providerCards = computed(() => {
  const cards: Array<{
    provider: DeliveryProvider
    label: string
    minCost: number
    minDays: number
    maxDays: number
  }> = []

  groupedProviders.value.forEach((options, provider) => {
    const minCostOption = options.reduce((min, opt) => opt.cost_rub < min.cost_rub ? opt : min)
    cards.push({
      provider,
      label: minCostOption.provider_label,
      minCost: minCostOption.cost_rub,
      minDays: Math.min(...options.map(o => o.days_min)),
      maxDays: Math.max(...options.map(o => o.days_max))
    })
  })

  return cards
})

const selectedProviderOptions = computed(() => {
  if (!deliveryStore.selectedProvider) return []
  return groupedProviders.value.get(deliveryStore.selectedProvider) ?? []
})

const hasPickup = computed(() => selectedProviderOptions.value.some(o => o.service_type === 'pickup'))
const hasCourier = computed(() => selectedProviderOptions.value.some(o => o.service_type === 'courier'))

watch(() => props.cityCode, async (newCode) => {
  if (!newCode) {
    deliveryStore.setAvailableOptions([])
    return
  }
  deliveryStore.setIsLoadingRates(true)
  const options = await calculateAll({
    to_city_code: newCode,
    weight_grams: props.totalWeightGrams
  })
  deliveryStore.setAvailableOptions(options)
  deliveryStore.setIsLoadingRates(false)
}, { immediate: true })

function selectProvider(provider: DeliveryProvider) {
  deliveryStore.setProvider(provider)
  emit('provider-selected', provider)
}

function selectServiceType(type: 'pickup' | 'courier') {
  deliveryStore.setDeliveryType(type)
  const option = selectedProviderOptions.value.find(o => o.service_type === type)
  if (option) {
    emit('option-selected', option)
  }
}
</script>

<template>
  <div class="provider-selector" data-testid="delivery-provider-selector">
    <div class="provider-grid">
      <DeliveryProviderCard
        v-for="card in providerCards"
        :key="card.provider"
        :provider="card.provider"
        :label="card.label"
        :cost_rub="card.minCost"
        :days_min="card.minDays"
        :days_max="card.maxDays"
        :is-selected="deliveryStore.selectedProvider === card.provider"
        :is-loading="deliveryStore.isLoadingRates"
        @click="selectProvider(card.provider)"
      />
    </div>

    <Transition name="fade-slide">
      <div v-if="deliveryStore.selectedProvider && (hasPickup || hasCourier)" class="service-type-toggle">
        <div class="type-toggle" data-testid="delivery-type-toggle">
          <button
            v-if="hasPickup"
            class="type-btn"
            :class="{ 'type-btn--active': deliveryStore.deliveryType === 'pickup' }"
            data-testid="delivery-type-pickup"
            @click="selectServiceType('pickup')"
          >
            <Icon name="ph:package-bold" size="18" />
            Пункт выдачи
          </button>
          <button
            v-if="hasCourier"
            class="type-btn"
            :class="{ 'type-btn--active': deliveryStore.deliveryType === 'courier' }"
            data-testid="delivery-type-courier"
            @click="selectServiceType('courier')"
          >
            <Icon name="ph:truck-bold" size="18" />
            Курьер
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.provider-selector {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.service-type-toggle {
  margin-top: 4px;
}

.type-toggle {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.type-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  color: var(--color-text-2);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: border-color var(--transition-fast), color var(--transition-fast), background var(--transition-fast);
  min-height: 44px;
}

.type-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.type-btn--active {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
  color: var(--color-accent);
}
</style>
