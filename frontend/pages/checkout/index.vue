<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useCartStore } from '~/stores/cartStore'
import { useDeliveryStore } from '~/stores/deliveryStore'
import { useToast } from '~/composables/useToast'
import { useCdek } from '~/composables/useCdek'
import { formatPrice } from '~/composables/useFormatters'
import AppBreadcrumbs from '~/components/AppBreadcrumbs.vue'
import type { CdekCity, CdekPickupPoint } from '~/composables/useCdek'

const cartStore = useCartStore()
const deliveryStore = useDeliveryStore()
const toast = useToast()
const { searchCities, getPickupPoints, calculateDelivery } = useCdek()
const router = useRouter()

// --- SEO ---
useSeoMeta({
  title: 'Оформление заказа | WifiOBD',
  description: 'Оформите заказ с доставкой СДЭК по всей России.',
  ogTitle: 'Оформление заказа | WifiOBD',
})
useHead({ meta: [{ name: 'robots', content: 'noindex' }] })

const breadcrumbItems = [
  { name: 'Каталог', path: '/products' },
  { name: 'Корзина', path: '/cart' },
  { name: 'Оформление', path: '/checkout' },
]

// --- City search ---
const cityQuery = ref('')
const cityResults = ref<CdekCity[]>([])
const citySearchOpen = ref(false)
const citySearchPending = ref(false)

// --- Contact Info ---
const userStore = useUserStore()
const customer = ref({
  name: userStore.user?.full_name || '',
  email: userStore.user?.email || '',
  phone: userStore.user?.phone || '',
})
const phoneError = ref('')

// --- Saved addresses ---
const selectedAddress = ref<any>(null)
const handleAddressSelect = (addr: any) => {
  selectedAddress.value = addr
  if (addr) {
    cityQuery.value = addr.city
    deliveryStore.setCity({ code: 0, city: addr.city })
  }
}

const handlePhoneInput = (e: Event) => {
  const input = e.target as HTMLInputElement
  let value = input.value.replace(/\D/g, '')
  if (value.startsWith('7') || value.startsWith('8')) {
    value = value.substring(1)
  }
  
  let formatted = '+7 ('
  if (value.length > 0) formatted += value.substring(0, 3)
  if (value.length > 3) formatted += ') ' + value.substring(3, 6)
  if (value.length > 6) formatted += '-' + value.substring(6, 8)
  if (value.length > 8) formatted += '-' + value.substring(8, 10)
  
  customer.value.phone = value.length === 0 ? '' : formatted
  phoneError.value = ''
}

const validateForm = () => {
  let isValid = true
  if (customer.value.phone) {
    const digits = customer.value.phone.replace(/\D/g, '')
    if (digits.length < 11) {
      phoneError.value = 'Введите корректный номер телефона'
      isValid = false
    }
  } else {
    phoneError.value = 'Телефон обязателен'
    isValid = false
  }
  return isValid
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null

watch(cityQuery, (val) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  // If user typed something that doesn't match selected city, clear selection
  if (deliveryStore.selectedCity && val !== deliveryStore.selectedCity.city) {
    deliveryStore.setCity(null)
    pvzList.value = []
  }
  if (val.length < 2) {
    cityResults.value = []
    citySearchOpen.value = false
    return
  }
  debounceTimer = setTimeout(async () => {
    citySearchPending.value = true
    cityResults.value = await searchCities(val)
    citySearchOpen.value = cityResults.value.length > 0
    citySearchPending.value = false
  }, 300)
})

function selectCity(city: CdekCity) {
  deliveryStore.setCity(city)
  cityQuery.value = city.city
  citySearchOpen.value = false
  cityResults.value = []
  if (deliveryStore.deliveryType === 'pickup') {
    loadPickupPoints(city.code)
  } else {
    triggerRecalculate()
  }
}

function clearCity() {
  deliveryStore.setCity(null)
  cityQuery.value = ''
  cityResults.value = []
  citySearchOpen.value = false
  pvzList.value = []
}

// --- Pickup points ---
const pvzList = ref<CdekPickupPoint[]>([])
const pvzLoading = ref(false)

async function loadPickupPoints(cityCode: number) {
  pvzLoading.value = true
  pvzList.value = await getPickupPoints(cityCode)
  pvzLoading.value = false
  triggerRecalculate()
}

function selectPvz(pvz: CdekPickupPoint) {
  deliveryStore.setPickupPoint(pvz)
}

// --- Delivery type switch ---
function setDeliveryType(type: 'pickup' | 'courier') {
  deliveryStore.setDeliveryType(type)
  if (deliveryStore.selectedCity) {
    if (type === 'pickup') {
      loadPickupPoints(deliveryStore.selectedCity.code)
    } else {
      pvzList.value = []
      triggerRecalculate()
    }
  }
}

// --- Provider selection ---
function handleProviderSelected(provider: string) {
  if (deliveryStore.deliveryType === 'pickup' && deliveryStore.selectedCity) {
    loadPickupPoints(deliveryStore.selectedCity.code)
  }
}

// --- Calculate delivery ---
async function triggerRecalculate() {
  const city = deliveryStore.selectedCity
  if (!city) return
  deliveryStore.isCalculating = true
  const result = await calculateDelivery({ to_city_code: city.code })
  deliveryStore.setCalcResult(result)
  deliveryStore.isCalculating = false
}

// --- Order total ---
const orderTotal = computed(() => cartStore.totalPrice + deliveryStore.deliveryCost)

// --- Place order ---
const orderPending = ref(false)
const apiFetch = useApiFetch()

async function placeOrder() {
  if (!deliveryStore.isDeliveryReady || orderPending.value) return
  if (!validateForm()) {
    toast.error('Ошибка заполнения', 'Проверьте корректность введенных данных')
    return
  }
  orderPending.value = true
  try {
    const body: Record<string, unknown> = {
      payment_method: 'yoomoney',
      email: customer.value.email,
      full_name: customer.value.name,
      phone: customer.value.phone,
      provider: deliveryStore.selectedProvider || 'cdek',
    }
    if (deliveryStore.deliveryType === 'pickup') {
      body.delivery_type = 'cdek_pvz'
      body.pvz_code = deliveryStore.selectedPickupPoint?.code
    } else {
      body.delivery_type = 'cdek_door'
      const addr = deliveryStore.courierAddress
      const parts = [addr.street, addr.building, addr.apartment ? `кв. ${addr.apartment}` : ''].filter(Boolean)
      body.address = parts.join(', ')
    }
    const response = await apiFetch<{ order_id: string; payment_url: string }>('/orders/', {
      method: 'POST',
      body,
    })
    if (response?.payment_url) {
      cartStore.clearCart()
      deliveryStore.reset()
      await navigateTo(response.payment_url, { external: true })
    }
  } catch {
    toast.error('Ошибка оформления', 'Не удалось создать заказ. Попробуйте снова.')
  } finally {
    orderPending.value = false
  }
}

// --- Init on mount ---
onMounted(() => {
  cartStore.init()
  deliveryStore.init()
  if (cartStore.items.length === 0) {
    router.push('/cart')
    return
  }
  if (deliveryStore.selectedCity) {
    cityQuery.value = deliveryStore.selectedCity.city
    if (deliveryStore.deliveryType === 'pickup') {
      loadPickupPoints(deliveryStore.selectedCity.code)
    }
  }
})
</script>

<template>
  <div class="checkout-page">
    <div class="container">
      <AppBreadcrumbs :items="breadcrumbItems" />
      <h1 class="checkout-page__title">Оформление заказа</h1>

      <div v-if="cartStore.items.length === 0" class="checkout-empty">
        <Icon name="ph:shopping-cart-light" size="64" />
        <p>Ваша корзина пуста.</p>
        <NuxtLink to="/products" class="btn btn--primary">Перейти в каталог</NuxtLink>
      </div>

      <div v-else class="checkout-layout">
        <!-- LEFT: Info and Delivery -->
        <div class="checkout-main-col">
          <!-- Contact Info -->
          <section class="checkout-section mb-6">
            <h2 class="section-title">Контактные данные</h2>
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label" for="customer-name">Имя и фамилия</label>
                <input
                  id="customer-name"
                  v-model="customer.name"
                  type="text"
                  class="form-input form-input--no-icon"
                  placeholder="Иван Иванов"
                  data-testid="customer-name"
                />
              </div>
              <div class="form-group">
                <label class="form-label" for="customer-email">Email</label>
                <input
                  id="customer-email"
                  v-model="customer.email"
                  type="email"
                  class="form-input form-input--no-icon"
                  placeholder="example@mail.ru"
                  data-testid="customer-email"
                />
              </div>
              <div class="form-group">
                <label class="form-label" for="customer-phone">Телефон</label>
                <input
                  id="customer-phone"
                  :value="customer.phone"
                  type="tel"
                  class="form-input form-input--no-icon"
                  :class="{ 'form-input--error': phoneError }"
                  placeholder="+7 (___) ___-__-__"
                  data-testid="customer-phone"
                  @input="handlePhoneInput"
                />
                <span v-if="phoneError" class="form-error">{{ phoneError }}</span>
              </div>
            </div>
          </section>

          <!-- Saved Addresses -->
          <section v-if="userStore.isAuthenticated" class="checkout-section mb-6">
            <h2 class="section-title">Сохранённые адреса</h2>
            <AddressSelector @select="handleAddressSelect" />
          </section>

          <!-- Delivery section -->
          <section class="delivery-section" data-testid="delivery-form">
          <h2 class="section-title">Способ доставки</h2>

          <!-- Provider selector -->
          <DeliveryProviderSelector
            v-if="deliveryStore.selectedCity"
            :city-code="deliveryStore.selectedCity.code"
            :total-weight-grams="500"
            @provider-selected="handleProviderSelected"
          />

          <!-- Delivery type toggle (legacy CDEK) -->
          <div v-if="!deliveryStore.selectedProvider" class="type-toggle">
            <button
              class="type-btn"
              :class="{ 'type-btn--active': deliveryStore.deliveryType === 'pickup' }"
              data-testid="delivery-type-pickup"
              @click="setDeliveryType('pickup')"
            >
              <Icon name="ph:package-bold" size="18" />
              Пункт выдачи (ПВЗ)
            </button>
            <button
              class="type-btn"
              :class="{ 'type-btn--active': deliveryStore.deliveryType === 'courier' }"
              data-testid="delivery-type-courier"
              @click="setDeliveryType('courier')"
            >
              <Icon name="ph:truck-bold" size="18" />
              Курьер
            </button>
          </div>

          <!-- City search -->
          <div class="form-group">
            <label class="form-label" for="city-input">Город доставки</label>
            <div class="city-input-wrap">
              <Icon
                v-if="!citySearchPending"
                name="ph:magnifying-glass-bold"
                size="18"
                class="city-icon city-icon--left"
              />
              <Icon
                v-else
                name="ph:spinner-gap-bold"
                size="18"
                class="city-icon city-icon--left city-spin"
              />
              <input
                id="city-input"
                v-model="cityQuery"
                type="text"
                class="form-input"
                placeholder="Введите название города..."
                autocomplete="off"
                data-testid="city-input"
                @focus="citySearchOpen = cityResults.length > 0"
                @blur="setTimeout(() => { citySearchOpen = false }, 200)"
              />
              <button
                v-if="deliveryStore.selectedCity"
                class="city-clear-btn"
                aria-label="Сбросить город"
                @click="clearCity"
              >
                <Icon name="ph:x-bold" size="14" />
              </button>
            </div>

            <!-- City dropdown -->
            <ul
              v-if="citySearchOpen && cityResults.length > 0"
              class="city-dropdown"
              data-testid="city-search-results"
            >
              <li
                v-for="city in cityResults"
                :key="city.code"
                class="city-option"
                data-testid="city-option"
                @mousedown.prevent="selectCity(city)"
              >
                <span class="city-option__name">{{ city.city }}</span>
                <span v-if="city.region" class="city-option__region">{{ city.region }}</span>
              </li>
            </ul>
          </div>

          <!-- PVZ section (pickup mode) -->
          <template v-if="deliveryStore.deliveryType === 'pickup' && deliveryStore.selectedCity">
            <div v-if="pvzLoading" class="pvz-state">
              <Icon name="ph:spinner-gap-bold" size="24" class="city-spin" />
              <span>Загружаем пункты выдачи...</span>
            </div>

            <div v-else-if="pvzList.length === 0" class="pvz-state">
              <Icon name="ph:map-pin-slash-bold" size="24" />
              <span>Пункты выдачи не найдены в выбранном городе</span>
            </div>

            <div v-else class="pvz-list" data-testid="pvz-list">
              <div
                v-for="pvz in pvzList"
                :key="pvz.code"
                class="pvz-item"
                :class="{ 'pvz-item--selected': deliveryStore.selectedPickupPoint?.code === pvz.code }"
                data-testid="pvz-item"
              >
                <div class="pvz-item__info">
                  <div class="pvz-item__address">{{ pvz.address }}</div>
                  <div class="pvz-item__hours">
                    <Icon name="ph:clock-bold" size="12" />
                    {{ pvz.work_time }}
                  </div>
                  <div v-if="pvz.phone" class="pvz-item__phone">{{ pvz.phone }}</div>
                  <div v-if="pvz.note" class="pvz-item__note">{{ pvz.note }}</div>
                </div>
                <button
                  class="pvz-select-btn"
                  :class="deliveryStore.selectedPickupPoint?.code === pvz.code ? 'btn btn--primary btn--sm' : 'btn btn--secondary btn--sm'"
                  data-testid="pvz-select-btn"
                  @click="selectPvz(pvz)"
                >
                  <Icon
                    v-if="deliveryStore.selectedPickupPoint?.code === pvz.code"
                    name="ph:check-bold"
                    size="14"
                  />
                  {{ deliveryStore.selectedPickupPoint?.code === pvz.code ? 'Выбрано' : 'Выбрать' }}
                </button>
              </div>
            </div>
          </template>

          <!-- Courier address form -->
          <template v-if="deliveryStore.deliveryType === 'courier' && deliveryStore.selectedCity">
            <div class="courier-form">
              <div class="form-group">
                <label class="form-label" for="courier-street">Улица</label>
                <input
                  id="courier-street"
                  :value="deliveryStore.courierAddress.street"
                  type="text"
                  class="form-input form-input--no-icon"
                  placeholder="Введите улицу"
                  data-testid="courier-street"
                  @input="deliveryStore.setCourierAddress({ street: ($event.target as HTMLInputElement).value })"
                />
              </div>
              <div class="courier-row">
                <div class="form-group">
                  <label class="form-label" for="courier-building">Дом / корпус</label>
                  <input
                    id="courier-building"
                    :value="deliveryStore.courierAddress.building"
                    type="text"
                    class="form-input form-input--no-icon"
                    placeholder="Например: 12А"
                    data-testid="courier-building"
                    @input="deliveryStore.setCourierAddress({ building: ($event.target as HTMLInputElement).value })"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label" for="courier-apartment">Квартира (необяз.)</label>
                  <input
                    id="courier-apartment"
                    :value="deliveryStore.courierAddress.apartment"
                    type="text"
                    class="form-input form-input--no-icon"
                    placeholder="56"
                    @input="deliveryStore.setCourierAddress({ apartment: ($event.target as HTMLInputElement).value })"
                  />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label" for="courier-comment">Комментарий (необяз.)</label>
                <textarea
                  id="courier-comment"
                  :value="deliveryStore.courierAddress.comment"
                  class="form-textarea"
                  rows="2"
                  placeholder="Код домофона, этаж и т.д."
                  @input="deliveryStore.setCourierAddress({ comment: ($event.target as HTMLTextAreaElement).value })"
                />
              </div>
            </div>
          </template>
        </section>
      </div>

      <!-- RIGHT: Order summary -->
      <aside class="order-summary">
          <div class="summary-card">
            <h3 class="summary-card__title">Ваш заказ</h3>

            <ul class="summary-items">
              <li v-for="item in cartStore.items" :key="item.id" class="summary-item">
                <span class="summary-item__name">{{ item.name }} × {{ item.quantity }}</span>
                <span class="summary-item__price">{{ formatPrice(item.price * item.quantity) }}</span>
              </li>
            </ul>

            <div class="summary-divider" />

            <div class="summary-row">
              <span class="summary-label">Товары ({{ cartStore.totalCount }} шт.)</span>
              <span class="summary-value">{{ formatPrice(cartStore.totalPrice) }}</span>
            </div>

            <div class="summary-row">
              <span class="summary-label">
                {{ deliveryStore.selectedProvider
                  ? `Доставка ${deliveryStore.availableOptions.find(o => o.provider === deliveryStore.selectedProvider)?.provider_label || 'СДЭК'}`
                  : 'Доставка' }}
              </span>
              <span class="summary-value" data-testid="delivery-cost">
                <template v-if="deliveryStore.isCalculating">
                  <Icon name="ph:spinner-gap-bold" size="14" class="city-spin" />
                  Расчёт...
                </template>
                <template v-else-if="deliveryStore.calcResult">
                  {{ formatPrice(deliveryStore.deliveryCost) }}
                  <span class="delivery-days">({{ deliveryStore.deliveryDays }} дн.)</span>
                </template>
                <template v-else>
                  <span class="summary-muted">Выберите город</span>
                </template>
              </span>
            </div>

            <div class="summary-divider" />

            <div class="summary-row summary-row--total">
              <span class="summary-label-total">Итого</span>
              <span class="summary-value-total" data-testid="order-total">
                {{ formatPrice(orderTotal) }}
              </span>
            </div>

            <button
              class="btn btn--primary btn--lg checkout-submit-btn"
              :disabled="!deliveryStore.isDeliveryReady || orderPending"
              data-testid="checkout-btn"
              @click="placeOrder"
            >
              <Icon
                v-if="orderPending"
                name="ph:spinner-gap-bold"
                size="18"
                class="city-spin"
              />
              <Icon v-else name="ph:lock-simple-bold" size="18" />
              {{ orderPending ? 'Оформляем...' : 'Оформить заказ' }}
            </button>

            <p v-if="!deliveryStore.isDeliveryReady" class="checkout-hint">
              <Icon name="ph:info-bold" size="14" />
              {{
                !deliveryStore.selectedCity
                  ? 'Выберите город доставки'
                  : deliveryStore.deliveryType === 'pickup'
                    ? 'Выберите пункт выдачи'
                    : 'Укажите улицу и дом'
              }}
            </p>

            <div class="summary-footer">
              <Icon name="ph:shield-check-bold" size="16" />
              <span>Оплата через ЮMoney — безопасно</span>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<style scoped>
.checkout-page {
  padding: 40px 0 80px;
}

.checkout-page__title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 32px;
  color: var(--color-text);
  border-left: 4px solid var(--color-accent);
  padding-left: 16px;
}

.checkout-empty {
  text-align: center;
  padding: 80px 20px;
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--color-muted);
}

/* ── Layout ── */
.checkout-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
  align-items: start;
}

@media (min-width: 1024px) {
  .checkout-layout {
    grid-template-columns: 1fr 380px;
  }
}

.checkout-main-col {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.checkout-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 28px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.form-error {
  display: block;
  font-size: var(--text-xs);
  color: var(--color-error);
  margin-top: 4px;
}

.form-input--error {
  border-color: var(--color-error) !important;
}

.mb-6 { margin-bottom: 24px; }

/* ── Section title ── */
.section-title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 20px;
}

/* ── Delivery section ── */
.delivery-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 28px;
}

/* ── Type toggle ── */
.type-toggle {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
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

/* ── Form elements ── */
.form-group {
  margin-bottom: 16px;
  position: relative;
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 10px 36px 10px 40px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  color: var(--color-text);
  font-size: 16px;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  outline: none;
  box-sizing: border-box;
}

.form-input--no-icon {
  padding-left: 14px;
  padding-right: 14px;
}

.form-input:focus {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.form-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  color: var(--color-text);
  font-size: 16px;
  font-family: var(--font-sans);
  resize: vertical;
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  box-sizing: border-box;
}

.form-textarea:focus {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

/* ── City input ── */
.city-input-wrap {
  position: relative;
}

.city-icon {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-muted);
  pointer-events: none;
}

.city-icon--left {
  left: 12px;
}

.city-clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast);
  min-width: 28px;
  min-height: 28px;
  justify-content: center;
}

.city-clear-btn:hover {
  color: var(--color-error);
}

.city-spin {
  animation: spin 1s linear infinite;
}

/* ── City dropdown ── */
.city-dropdown {
  position: absolute;
  z-index: var(--z-overlay);
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  max-height: 260px;
  overflow-y: auto;
  list-style: none;
  padding: 4px;
  margin: 0;
}

.city-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
  gap: 8px;
}

.city-option:hover {
  background: var(--color-surface-2);
}

.city-option__name {
  font-weight: 600;
  color: var(--color-text);
  font-size: var(--text-sm);
}

.city-option__region {
  font-size: var(--text-xs);
  color: var(--color-muted);
  text-align: right;
  flex-shrink: 0;
}

/* ── PVZ states ── */
.pvz-state {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-muted);
  font-size: var(--text-sm);
  padding: 16px 0;
}

/* ── PVZ list ── */
.pvz-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 2px;
}

.pvz-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface-2);
  transition: border-color var(--transition-fast), background var(--transition-fast);
}

.pvz-item--selected {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
}

.pvz-item__info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pvz-item__address {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
}

.pvz-item__hours {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-xs);
  color: var(--color-text-2);
}

.pvz-item__phone,
.pvz-item__note {
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.pvz-select-btn {
  flex-shrink: 0;
}

/* ── Courier form ── */
.courier-form {
  margin-top: 8px;
}

.courier-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

/* ── Order summary ── */
.order-summary {
  position: sticky;
  top: 100px;
}

.summary-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 28px;
}

.summary-card__title {
  font-size: var(--text-xl);
  font-weight: 800;
  margin-bottom: 20px;
  color: var(--color-text);
}

.summary-items {
  list-style: none;
  padding: 0;
  margin: 0 0 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--text-sm);
  gap: 8px;
}

.summary-item__name {
  color: var(--color-text-2);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-item__price {
  color: var(--color-text);
  font-weight: 600;
  flex-shrink: 0;
}

.summary-divider {
  height: 1px;
  background: var(--color-border);
  margin: 14px 0;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: var(--text-sm);
  gap: 8px;
}

.summary-label {
  color: var(--color-text-2);
}

.summary-value {
  color: var(--color-text);
  font-weight: 600;
  text-align: right;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.summary-muted {
  color: var(--color-muted);
  font-weight: 400;
  font-size: var(--text-xs);
}

.delivery-days {
  font-size: var(--text-xs);
  color: var(--color-muted);
  font-weight: 400;
}

.summary-row--total {
  margin-bottom: 20px;
  align-items: center;
}

.summary-label-total {
  font-size: var(--text-lg);
  font-weight: 800;
  color: var(--color-text);
}

.summary-value-total {
  font-size: var(--text-xl);
  font-weight: 800;
  color: var(--color-accent);
}

.checkout-submit-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.checkout-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.checkout-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-xs);
  color: var(--color-muted);
  text-align: center;
  justify-content: center;
  margin-bottom: 12px;
}

.summary-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 16px;
  color: var(--color-muted);
  font-size: var(--text-xs);
}

/* ── Buttons ── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  font-weight: 700;
  font-size: var(--text-sm);
  cursor: pointer;
  border: none;
  text-decoration: none;
  transition: background var(--transition-fast), transform var(--transition-fast), border-color var(--transition-fast);
  min-height: 44px;
}

.btn:active:not(:disabled) {
  transform: scale(0.97);
}

.btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.btn--primary {
  background: var(--color-accent);
  color: var(--color-on-accent);
}

.btn--primary:hover:not(:disabled) {
  background: var(--color-accent-hover);
}

.btn--secondary {
  border: 1px solid var(--color-accent);
  background: transparent;
  color: var(--color-accent);
}

.btn--secondary:hover:not(:disabled) {
  background: var(--color-accent-glow);
}

.btn--sm {
  padding: 8px 14px;
  font-size: var(--text-xs);
  min-height: 36px;
}

.btn--lg {
  padding: 14px 24px;
  font-size: var(--text-base);
  min-height: 52px;
}
</style>
