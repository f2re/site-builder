<script setup lang="ts">
import { useCartStore } from '~/stores/cartStore'
import { useToast } from '~/composables/useToast'
import AppBreadcrumbs from '~/components/AppBreadcrumbs.vue'
import { formatPrice } from '~/composables/useFormatters'

const cartStore = useCartStore()
const toast = useToast()

const breadcrumbItems = [
  { name: 'Каталог', path: '/products' },
  { name: 'Корзина', path: '/cart' }
]

const updateQuantity = (id: string, delta: number) => {
  const item = cartStore.items.find(i => i.id === id)
  if (item) {
    if (delta > 0 && item.quantity >= (item.maxStock ?? Infinity)) {
      toast.warning('Достигнут максимум', `В наличии только ${item.maxStock} шт.`)
      return
    }
    cartStore.updateQuantity(id, item.quantity + delta)
  }
}

const removeItem = (id: string, name: string) => {
  cartStore.removeItem(id)
  toast.info('Товар удален', `${name} удален из корзины`)
}

// SEO
useSeoMeta({
  title: 'Корзина | WifiOBD',
  description: 'Ваш список покупок в магазине WifiOBD. Оформите заказ прямо сейчас.',
  ogTitle: 'Корзина | WifiOBD',
})

useHead({
  meta: [
    { name: 'robots', content: 'noindex' }
  ]
})
</script>

<template>
  <div class="cart-page">
    <div class="container">
      <AppBreadcrumbs :items="breadcrumbItems" />

      <h1 class="cart-page__title">Корзина</h1>

      <div v-if="cartStore.items.length === 0" class="cart-empty">
        <div class="cart-empty__icon">
          <Icon name="ph:shopping-cart-light" size="80" />
        </div>
        <h2 class="cart-empty__title">Ваша корзина пуста</h2>
        <p class="cart-empty__text">Самое время добавить в неё что-нибудь полезное!</p>
        <NuxtLink to="/products" class="btn btn--primary btn--lg">Перейти в каталог</NuxtLink>
      </div>

      <div v-else class="cart-layout">
        <div class="cart-items">
          <div v-for="item in cartStore.items" :key="item.id" class="cart-item" data-testid="cart-item">
            <div class="cart-item__image">
              <NuxtImg :src="item.image" :alt="item.name" width="100" height="100" fit="contain" format="webp" />
            </div>

            <div class="cart-item__content">
              <div class="cart-item__info">
                <NuxtLink :to="`/products/${item.variantId || item.id}`" class="cart-item__name">{{ item.name }}</NuxtLink>
                
                <!-- Selected Options -->
                <div v-if="item.selectedOptions && item.selectedOptions.length > 0" class="cart-item__options">
                  <div v-for="opt in item.selectedOptions" :key="opt.value_id" class="cart-item__option">
                    <span class="opt-group">{{ opt.group_name }}:</span>
                    <span class="opt-value">{{ opt.value_name }}</span>
                    <span v-if="opt.price_modifier !== 0" class="opt-price">
                      ({{ opt.price_modifier > 0 ? '+' : '' }}{{ formatPrice(opt.price_modifier) }})
                    </span>
                  </div>
                </div>

                <div class="cart-item__price">{{ formatPrice(item.price) }} / шт.</div>
              </div>

              <div class="cart-item__actions">
                <div class="cart-item__stepper-wrap">
                  <div class="qty-stepper" data-testid="cart-item-qty">
                    <button
                      class="qty-btn"
                      data-testid="cart-qty-decrease"
                      @click="updateQuantity(item.id, -1)"
                      :disabled="item.quantity <= 1"
                    >
                      <Icon name="ph:minus-bold" size="16" />
                    </button>
                    <span class="qty-value">{{ item.quantity }}</span>
                    <button
                      class="qty-btn"
                      data-testid="cart-qty-increase"
                      @click="updateQuantity(item.id, 1)"
                      :disabled="item.quantity >= (item.maxStock ?? Infinity)"
                    >
                      <Icon name="ph:plus-bold" size="16" />
                    </button>
                  </div>
                  <span v-if="item.maxStock" class="qty-max-hint">макс. {{ item.maxStock }} шт.</span>
                </div>

                <div class="cart-item__total">
                  {{ formatPrice(item.price * item.quantity) }}
                </div>

                <button class="remove-btn" data-testid="cart-remove-btn" @click="removeItem(item.id, item.name)" aria-label="Удалить">
                  <Icon name="ph:trash-bold" size="20" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <aside class="cart-summary">
          <div class="summary-card">
            <h3 class="summary-card__title">Итого</h3>
            
            <div class="summary-row">
              <span class="summary-label">Товаров ({{ cartStore.totalCount }})</span>
              <span class="summary-value">{{ formatPrice(cartStore.totalPrice) }}</span>
            </div>
            
            <div class="summary-row">
              <span class="summary-label">Доставка</span>
              <span class="summary-value summary-value--free">Рассчитывается на следующем шаге</span>
            </div>

            <div class="summary-divider"></div>

            <div class="summary-row summary-row--total">
              <span class="summary-label">К оплате</span>
              <span class="summary-value" data-testid="cart-total">{{ formatPrice(cartStore.totalPrice) }}</span>
            </div>

            <NuxtLink to="/checkout" class="btn btn--primary btn--lg btn-checkout" data-testid="checkout-btn">
              Оформить заказ
            </NuxtLink>

            <div class="summary-footer">
              <Icon name="ph:shield-check-bold" size="18" />
              <span>Безопасная оплата и гарантия возврата</span>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cart-page {
  padding: 40px 0;
}

.cart-page__title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 32px;
  color: var(--color-text);
  border-left: 4px solid var(--color-accent);
  padding-left: 16px;
}

.cart-empty {
  text-align: center;
  padding: 80px 20px;
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
}

.cart-empty__icon {
  color: var(--color-muted);
  margin-bottom: 24px;
  opacity: 0.5;
}

.cart-empty__title {
  font-size: var(--text-xl);
  font-weight: 700;
  margin-bottom: 8px;
}

.cart-empty__text {
  color: var(--color-text-2);
  margin-bottom: 32px;
}

.cart-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
}

@media (min-width: 1024px) {
  .cart-layout {
    grid-template-columns: 1fr 380px;
    align-items: start;
  }
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cart-item {
  display: flex;
  gap: 24px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  transition: border-color var(--transition-fast);
}

.cart-item:hover {
  border-color: var(--color-accent);
}

.cart-item__image {
  width: 100px;
  height: 100px;
  flex-shrink: 0;
  background: var(--color-bg-subtle);
  border-radius: var(--radius-md);
  padding: 8px;
}

.cart-item__image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.cart-item__content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

@media (min-width: 640px) {
  .cart-item__content {
    flex-direction: row;
    align-items: center;
  }
}

.cart-item__info {
  margin-bottom: 16px;
}

@media (min-width: 640px) {
  .cart-item__info {
    margin-bottom: 0;
    max-width: 60%;
  }
}

.cart-item__name {
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--color-text);
  text-decoration: none;
  display: block;
  margin-bottom: 4px;
}

.cart-item__name:hover {
  color: var(--color-accent);
}

.cart-item__price {
  font-size: var(--text-sm);
  color: var(--color-muted);
}

.cart-item__options {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.cart-item__option {
  font-size: var(--text-xs);
  color: var(--color-text-2);
  display: flex;
  align-items: center;
  gap: 4px;
}

.opt-group {
  color: var(--color-muted);
}

.opt-value {
  font-weight: 600;
}

.opt-price {
  color: var(--color-accent);
  font-family: var(--font-mono);
  font-size: 10px;
}

.cart-item__actions {
  display: flex;
  align-items: center;
  gap: 24px;
  justify-content: space-between;
}

.qty-stepper {
  display: flex;
  align-items: center;
  background: var(--color-surface-2);
  border-radius: var(--radius-md);
  padding: 4px;
  border: 1px solid var(--color-border);
}

.qty-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--color-text);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.qty-btn:hover:not(:disabled) {
  background: var(--color-surface-3);
  color: var(--color-accent);
}

.qty-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.qty-value {
  width: 40px;
  text-align: center;
  font-weight: 700;
  font-size: var(--text-sm);
}

.cart-item__total {
  font-size: var(--text-lg);
  font-weight: 800;
  color: var(--color-text);
  min-width: 100px;
  text-align: right;
}

.remove-btn {
  background: transparent;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  padding: 8px;
  transition: all var(--transition-fast);
}

.remove-btn:hover {
  color: var(--color-error);
  transform: scale(1.1);
}

/* Summary Card */
.summary-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 32px;
  position: sticky;
  top: 100px;
}

.summary-card__title {
  font-size: var(--text-xl);
  font-weight: 800;
  margin-bottom: 24px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: var(--text-base);
}

.summary-label {
  color: var(--color-text-2);
}

.summary-value {
  color: var(--color-text);
  font-weight: 600;
}

.summary-value--free {
  font-size: var(--text-xs);
  color: var(--color-muted);
  text-align: right;
  max-width: 150px;
}

.summary-divider {
  height: 1px;
  background: var(--color-border);
  margin: 16px 0 24px;
}

.summary-row--total {
  margin-bottom: 32px;
}

.summary-row--total .summary-label {
  font-size: var(--text-lg);
  font-weight: 800;
  color: var(--color-text);
}

.summary-row--total .summary-value {
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--color-accent);
}

.btn-checkout {
  width: 100%;
}

.summary-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
  color: var(--color-muted);
  font-size: var(--text-xs);
}

.cart-item__stepper-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.qty-max-hint {
  font-size: var(--text-xs);
  color: var(--color-muted);
  white-space: nowrap;
}
</style>
