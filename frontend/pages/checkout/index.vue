<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useCartStore } from '~/stores/cartStore'
import { useOrders } from '~/composables/useOrders'
import { useAuth } from '~/composables/useAuth'

const cartStore = useCartStore()
const { createOrder, calculateDelivery, getPVZs } = useOrders()
const { accessToken } = useAuth()
const config = useRuntimeConfig()
const router = useRouter()

// Redirect if cart is empty
onMounted(() => {
  if (cartStore.items.length === 0) {
    router.push('/cart')
  }
})

// Cities stub
const cities = [
  { label: 'Москва', value: '44' },
  { label: 'Санкт-Петербург', value: '137' },
  { label: 'Новосибирск', value: '270' },
  { label: 'Екатеринбург', value: '250' },
  { label: 'Казань', value: '431' },
  { label: 'Нижний Новгород', value: '136' },
  { label: 'Челябинск', value: '410' },
  { label: 'Самара', value: '416' },
  { label: 'Омск', value: '407' },
  { label: 'Ростов-на-Дону', value: '131' },
]

// Form state
const form = ref({
  name: '',
  email: '',
  phone: '',
  cityCode: '',
  deliveryType: 'cdek_pvz' as 'cdek_pvz' | 'cdek_door',
  pvzCode: '',
  address: '',
})

// Validation
const errors = ref<Record<string, string>>({})

// Delivery calculation state
const deliveryCost = ref<number | null>(null)
const deliveryDays = ref<{ min: number; max: number } | null>(null)
const isCalculating = ref(false)
const pvzs = ref<any[]>([])
const isLoadingPVZs = ref(false)

// Fetch PVZs when city changes
watch(() => form.value.cityCode, async (newCity) => {
  if (newCity && form.value.deliveryType === 'cdek_pvz') {
    isLoadingPVZs.value = true
    try {
      const { data } = await getPVZs(newCity)
      if (data.value) {
        pvzs.value = data.value.items
        form.value.pvzCode = '' // Reset PVZ
      }
    } finally {
      isLoadingPVZs.value = false
    }
  }
  recalculateDelivery()
})

watch(() => form.value.deliveryType, () => {
  recalculateDelivery()
})

const recalculateDelivery = async () => {
  if (!form.value.cityCode) return

  isCalculating.value = true
  try {
    const { data } = await calculateDelivery({
      city_code: form.value.cityCode,
      weight_kg: 0.5,
      dimensions: { l: 20, w: 15, h: 10 }
    })
    
    if (data.value) {
      deliveryCost.value = data.value.cost_rub
      deliveryDays.value = { min: data.value.days_min, max: data.value.days_max }
    }
  } catch (err) {
    console.error('Failed to calculate delivery', err)
  } finally {
    isCalculating.value = false
  }
}

const totalWithDelivery = computed(() => {
  return cartStore.totalPrice + (deliveryCost.value || 0)
})

const isPending = ref(false)

const handlePlaceOrder = async () => {
  // Simple validation
  errors.value = {}
  if (!form.value.cityCode) errors.value.cityCode = 'Выберите город'
  if (form.value.deliveryType === 'cdek_pvz' && !form.value.pvzCode) errors.value.pvzCode = 'Выберите пункт выдачи'
  if (form.value.deliveryType === 'cdek_door' && !form.value.address) errors.value.address = 'Введите адрес доставки'
  
  if (Object.keys(errors.value).length > 0) return

  isPending.value = true
  try {
    const { data, error } = await createOrder({
      delivery_type: form.value.deliveryType,
      pvz_code: form.value.deliveryType === 'cdek_pvz' ? form.value.pvzCode : undefined,
      address: form.value.deliveryType === 'cdek_door' ? form.value.address : undefined,
      payment_method: 'yoomoney'
    })

    if (error.value) {
      alert('Ошибка при создании заказа: ' + (error.value.data?.detail || 'Неизвестная ошибка'))
      return
    }

    if (data.value?.payment_url) {
      // Clear cart before redirecting
      cartStore.clearCart()
      window.location.href = data.value.payment_url
    }
  } catch (err) {
    console.error('Order creation failed', err)
  } finally {
    isPending.value = false
  }
}
</script>

<template>
  <div class="checkout-page">
    <div class="container">
      <h1 class="page-title">Оформление заказа</h1>

      <div class="checkout-grid">
        <!-- Form -->
        <div class="checkout-form">
          <UCard class="form-card">
            <div class="card-header">
              <h2 class="card-title">Доставка</h2>
            </div>
            
            <div class="form-section">
              <USelect
                v-model="form.cityCode"
                label="Город"
                :options="cities"
                :error="errors.cityCode"
                placeholder="Выберите ваш город"
              />

              <div class="delivery-type-toggle">
                <button
                  class="type-btn"
                  :class="{ 'type-btn--active': form.deliveryType === 'cdek_pvz' }"
                  @click="form.deliveryType = 'cdek_pvz'"
                >
                  <span class="type-icon">📦</span>
                  <span>Пункт выдачи</span>
                </button>
                <button
                  class="type-btn"
                  :class="{ 'type-btn--active': form.deliveryType === 'cdek_door' }"
                  @click="form.deliveryType = 'cdek_door'"
                >
                  <span class="type-icon">🏠</span>
                  <span>Курьером</span>
                </button>
              </div>

              <div v-if="form.deliveryType === 'cdek_pvz'" class="pvz-selection">
                <USelect
                  v-if="pvzs.length > 0"
                  v-model="form.pvzCode"
                  label="Пункт выдачи (СДЭК)"
                  :options="pvzs.map(p => ({ label: p.address, value: p.code }))"
                  :error="errors.pvzCode"
                  :disabled="isLoadingPVZs"
                  placeholder="Выберите удобный пункт"
                />
                <div v-else-if="isLoadingPVZs" class="pvz-loading">
                  Загрузка пунктов выдачи...
                </div>
                <div v-else-if="form.cityCode" class="pvz-empty">
                  Пункты выдачи не найдены для этого города
                </div>
              </div>

              <UInput
                v-else
                v-model="form.address"
                label="Адрес доставки"
                placeholder="Улица, дом, квартира"
                :error="errors.address"
              />
            </div>

            <div v-if="deliveryCost !== null" class="delivery-info">
              <div class="info-item">
                <span class="info-label">Стоимость доставки:</span>
                <span class="info-value">{{ deliveryCost }} ₽</span>
              </div>
              <div v-if="deliveryDays" class="info-item">
                <span class="info-label">Срок:</span>
                <span class="info-value">{{ deliveryDays.min }}–{{ deliveryDays.max }} дн.</span>
              </div>
            </div>
          </UCard>
        </div>

        <!-- Sidebar / Summary -->
        <div class="checkout-summary">
          <UCard class="summary-card">
            <h2 class="card-title">Ваш заказ</h2>
            
            <div class="summary-items">
              <div v-for="item in cartStore.items" :key="item.id" class="summary-item">
                <span class="item-name">{{ item.name }} × {{ item.quantity }}</span>
                <span class="item-price">{{ item.price * item.quantity }} ₽</span>
              </div>
            </div>

            <div class="summary-totals">
              <div class="total-row">
                <span>Товары</span>
                <span>{{ cartStore.totalPrice }} ₽</span>
              </div>
              <div class="total-row">
                <span>Доставка</span>
                <span v-if="isCalculating">...</span>
                <span v-else-if="deliveryCost !== null">{{ deliveryCost }} ₽</span>
                <span v-else>—</span>
              </div>
              <div class="total-row total-row--main">
                <span>Итого</span>
                <span>{{ totalWithDelivery }} ₽</span>
              </div>
            </div>

            <UButton
              variant="primary"
              size="lg"
              class="place-order-btn"
              :loading="isPending"
              @click="handlePlaceOrder"
            >
              Оплатить заказ
            </UButton>
            
            <p class="summary-hint">
              Вы будете перенаправлены на страницу оплаты ЮKassa
            </p>
          </UCard>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.checkout-page {
  padding: 40px 0;
  min-height: calc(100vh - 200px);
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 32px;
  letter-spacing: -1px;
}

.checkout-grid {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 32px;
}

.form-card {
  padding: 32px;
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 700;
  margin-bottom: 24px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.delivery-type-toggle {
  display: flex;
  background: var(--color-surface-2);
  padding: 4px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.type-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border: none;
  background: transparent;
  color: var(--color-text-2);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  border-radius: calc(var(--radius-md) - 2px);
  transition: all var(--transition-fast);
}

.type-btn--active {
  background: var(--color-surface);
  color: var(--color-accent);
  box-shadow: var(--shadow-sm);
}

.type-icon { font-size: 1.2rem; }

.delivery-info {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px dashed var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
}

.info-label { color: var(--color-text-2); font-size: var(--text-sm); }
.info-value { font-weight: 600; color: var(--color-text); }

.summary-card {
  padding: 32px;
  position: sticky;
  top: 100px;
}

.summary-items {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.summary-totals {
  border-top: 1px solid var(--color-border);
  padding-top: 16px;
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  color: var(--color-text-2);
}

.total-row--main {
  margin-top: 8px;
  color: var(--color-text);
  font-size: var(--text-lg);
  font-weight: 800;
}

.place-order-btn {
  width: 100%;
}

.summary-hint {
  font-size: var(--text-xs);
  color: var(--color-muted);
  text-align: center;
  margin-top: 16px;
}

@media (max-width: 900px) {
  .checkout-grid {
    grid-template-columns: 1fr;
  }
  .checkout-summary {
    order: -1;
  }
}
</style>
