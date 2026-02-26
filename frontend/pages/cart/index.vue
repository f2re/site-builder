<script setup lang="ts">
import { useCart } from '~/composables/useCart'

const { fetchCart, removeFromCart, updateQuantity } = useCart()

// Fetch cart data
const { data: cart, pending, error, refresh } = await fetchCart()

const handleRemove = async (variantId: string) => {
  await removeFromCart(variantId)
  await refresh()
}

const handleUpdateQuantity = async (variantId: string, quantity: number) => {
  if (quantity < 1) {
    await handleRemove(variantId)
  } else {
    // Current backend logic: POST /cart/add increments quantity.
    // If we want to *set* quantity, we need to know the current quantity.
    // This is a simplified approach.
    await addToCart(variantId, 1) // Temporary: just adds 1 more
    await refresh()
  }
}

useHead({
  title: 'Корзина | Race-Shop'
})
</script>

<template>
  <div class="cart-page container">
    <header class="cart-page__header">
      <h1 class="cart-page__title">Корзина</h1>
      <span v-if="cart?.items?.length" class="cart-page__count">
        {{ cart.items.length }} товара
      </span>
    </header>

    <div v-if="pending && !cart" class="cart-page__loading">
      <div class="cart-page__items-skeleton">
        <USkeleton v-for="i in 3" :key="i" height="120px" class="skeleton-item" />
      </div>
      <div class="cart-page__summary-skeleton">
        <USkeleton height="300px" />
      </div>
    </div>

    <div v-else-if="error" class="cart-page__error">
      <div class="error-box">
        <Icon name="ph:warning-circle-bold" size="48" class="error-icon" />
        <p>Произошла ошибка при загрузке корзины.</p>
        <UButton @click="refresh">Повторить попытку</UButton>
      </div>
    </div>

    <div v-else-if="!cart || cart.items.length === 0" class="cart-page__empty">
      <div class="empty-box">
        <Icon name="ph:shopping-cart-simple-bold" size="64" class="empty-icon" />
        <p>Ваша корзина пуста</p>
        <UButton to="/products" variant="primary" size="lg">Перейти к покупкам</UButton>
      </div>
    </div>

    <div v-else class="cart-page__content">
      <div class="cart-page__items">
        <TransitionGroup name="list">
          <UCard v-for="item in cart.items" :key="item.variant_id" class="cart-item">
            <div class="cart-item__content">
              <div class="cart-item__main">
                <div class="cart-item__image">
                  <img v-if="item.image_url" :src="item.image_url" :alt="item.name" />
                  <div v-else class="image-placeholder">
                    <Icon name="ph:package-bold" size="32" />
                  </div>
                </div>
                <div class="cart-item__info">
                  <div class="cart-item__name">
                    {{ item.name }}
                  </div>
                  <div class="cart-item__meta">
                    <span class="cart-item__price">
                      {{ item.price.toLocaleString() }} ₽
                    </span>
                  </div>
                </div>
              </div>

              <div class="cart-item__controls">
                <div class="cart-item__quantity">
                  <button 
                    class="quantity-btn" 
                    aria-label="Уменьшить"
                    @click="handleRemove(item.variant_id)"
                  >
                    <Icon name="ph:minus-bold" size="16" />
                  </button>
                  <span class="quantity-value">{{ item.quantity }}</span>
                  <button 
                    class="quantity-btn" 
                    aria-label="Увеличить"
                    @click="handleUpdateQuantity(item.variant_id, item.quantity + 1)"
                  >
                    <Icon name="ph:plus-bold" size="16" />
                  </button>
                </div>
                
                <div class="cart-item__total">
                  {{ item.subtotal.toLocaleString() }} ₽
                </div>

                <UButton 
                  variant="ghost" 
                  size="sm" 
                  class="cart-item__remove"
                  @click="handleRemove(item.variant_id)"
                >
                  <template #icon>
                    <Icon name="ph:trash-bold" />
                  </template>
                </UButton>
              </div>
            </div>
          </UCard>
        </TransitionGroup>
      </div>

      <aside class="cart-page__summary">
        <UCard class="summary-card">
          <h2 class="summary-card__title">Детали заказа</h2>
          
          <div class="summary-card__details">
            <div class="summary-row">
              <span>Сумма за товары</span>
              <span>{{ cart.total_price.toLocaleString() }} ₽</span>
            </div>
            <div class="summary-row">
              <span>Доставка</span>
              <span class="free-badge">Рассчитывается далее</span>
            </div>
          </div>

          <div class="summary-card__divider"></div>
          
          <div class="summary-card__total">
            <span class="total-label">Итого</span>
            <div class="total-amount-box">
              <span class="total-price">{{ cart.total_price.toLocaleString() }} ₽</span>
            </div>
          </div>

          <UButton 
            variant="primary" 
            size="lg" 
            class="summary-card__checkout"
            to="/checkout"
          >
            Оформить заказ
            <template #iconRight>
              <Icon name="ph:arrow-right-bold" />
            </template>
          </UButton>

          <p class="summary-card__note">
            Нажимая кнопку, вы соглашаетесь с условиями оферты
          </p>
        </UCard>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.cart-page {
  padding-block: clamp(2rem, 5vh, 4rem);
}

.cart-page__header {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 2rem;
}

.cart-page__title {
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--color-text);
  margin: 0;
}

.cart-page__count {
  color: var(--color-text-2);
  font-size: var(--text-base);
}

.cart-page__content {
  display: grid;
  gap: 2rem;
  grid-template-columns: 1fr;
  align-items: start;
}

@media (min-width: 1024px) {
  .cart-page__content {
    grid-template-columns: 1fr 380px;
  }
}

.cart-page__items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cart-item {
  padding: 1rem;
}

@media (min-width: 640px) {
  .cart-item {
    padding: 1.5rem;
  }
}

.cart-item__content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

@media (min-width: 640px) {
  .cart-item__content {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}

.cart-item__main {
  display: flex;
  gap: 1rem;
  flex: 1;
}

.cart-item__image {
  width: 80px;
  height: 80px;
  background: var(--color-surface-2);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--color-muted);
}

.cart-item__info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.cart-item__name {
  font-weight: 600;
  font-size: var(--text-base);
  color: var(--color-text);
  text-decoration: none;
  transition: color var(--transition-fast);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cart-item__name:hover {
  color: var(--color-accent);
}

.cart-item__meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.cart-item__price {
  color: var(--color-text-2);
  font-weight: 500;
}

.cart-item__stock-warning {
  color: var(--color-warning);
  font-size: var(--text-xs);
  font-weight: 600;
}

.cart-item__controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

@media (min-width: 640px) {
  .cart-item__controls {
    justify-content: flex-end;
  }
}

.cart-item__quantity {
  display: flex;
  align-items: center;
  background: var(--color-surface-2);
  border-radius: var(--radius-md);
  padding: 2px;
  border: 1px solid var(--color-border);
}

.quantity-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--color-text);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.quantity-btn:hover {
  background-color: var(--color-surface-3);
  color: var(--color-accent);
}

.quantity-value {
  width: 32px;
  text-align: center;
  font-weight: 700;
  font-family: var(--font-mono);
}

.cart-item__total {
  font-weight: 800;
  font-size: var(--text-lg);
  color: var(--color-text);
  min-width: 100px;
  text-align: right;
}

.summary-card {
  padding: 2rem;
  position: sticky;
  top: 100px;
}

.summary-card__title {
  font-size: var(--text-xl);
  font-weight: 800;
  margin-bottom: 1.5rem;
  letter-spacing: -0.02em;
}

.summary-card__details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  color: var(--color-text-2);
  font-size: var(--text-sm);
}

.free-badge {
  color: var(--color-muted);
  font-style: italic;
}

.summary-card__divider {
  height: 1px;
  background-color: var(--color-border);
  margin-block: 1.5rem;
}

.summary-card__total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.total-label {
  font-weight: 700;
  font-size: var(--text-lg);
}

.total-price {
  font-size: var(--text-2xl);
  font-weight: 900;
  color: var(--color-accent);
  text-shadow: 0 0 20px var(--color-accent-glow);
}

.summary-card__checkout {
  width: 100%;
  margin-bottom: 1rem;
}

.summary-card__note {
  font-size: var(--text-xs);
  color: var(--color-muted);
  text-align: center;
  line-height: 1.4;
}

.cart-page__loading {
  display: grid;
  gap: 2rem;
}

@media (min-width: 1024px) {
  .cart-page__loading {
    grid-template-columns: 1fr 380px;
  }
}

.cart-page__items-skeleton {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cart-page__empty,
.cart-page__error {
  padding-block: 6rem;
  text-align: center;
}

.empty-box,
.error-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  max-width: 400px;
  margin: 0 auto;
}

.empty-icon {
  color: var(--color-surface-3);
}

.error-icon {
  color: var(--color-error);
}

.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>
